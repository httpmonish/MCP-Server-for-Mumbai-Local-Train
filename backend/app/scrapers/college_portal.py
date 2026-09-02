from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .exceptions import PortalAuthError, PortalSelectorError, PortalTimeoutError


class CollegePortalScraper:
    def __init__(self, base_url: str, timeout: int = 15000):
        self.base_url = base_url
        self.timeout = timeout

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=6),
        retry=retry_if_exception_type(PortalTimeoutError)
    )
    async def login(self, page, username, password):
        try:
            await page.goto(f"{self.base_url}/login", timeout=self.timeout)
            await page.fill('#username', username)
            await page.fill('#password', password)
            await page.click('button[type="submit"]')

            # Wait for dashboard or error
            try:
                await page.wait_for_selector('#dashboard-container', timeout=self.timeout)
            except PlaywrightTimeoutError:
                if await page.query_selector('#error-banner'):
                    raise PortalAuthError("Login failed: Error banner appeared")
                raise PortalTimeoutError("Login timed out: Dashboard container not found")
        except PlaywrightTimeoutError as e:
            raise PortalTimeoutError(f"Network timeout during login: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=6),
        retry=retry_if_exception_type(PortalTimeoutError)
    )
    async def scrape_attendance(self, page):
        try:
            await page.goto(f"{self.base_url}/attendance", timeout=self.timeout)
            try:
                await page.wait_for_selector('table#attendance-table', timeout=self.timeout)
            except PlaywrightTimeoutError:
                raise PortalSelectorError("Attendance table not found on page")

            rows = await page.query_selector_all('table#attendance-table tbody tr')
            results = []
            for row in rows:
                cells = await row.query_selector_all('td')
                if len(cells) >= 4:
                    subject_name = await cells[0].inner_text()
                    conducted = int(await cells[1].inner_text())
                    attended = int(await cells[2].inner_text())
                    percentage_text = await cells[3].inner_text()
                    percentage = float(percentage_text.strip('%'))

                    results.append({
                        'subject_name': subject_name,
                        'total_conducted': conducted,
                        'total_attended': attended,
                        'percentage': percentage
                    })
            return results
        except PlaywrightTimeoutError as e:
            raise PortalTimeoutError(f"Timeout while scraping attendance: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=6),
        retry=retry_if_exception_type(PortalTimeoutError)
    )
    async def scrape_exam_timetable(self, page):
        try:
            await page.goto(f"{self.base_url}/exams", timeout=self.timeout)
            rows = await page.query_selector_all('table#exam-table tbody tr')
            results = []
            for row in rows:
                cells = await row.query_selector_all('td')
                if len(cells) >= 4:
                    results.append({
                        'subject_name': await cells[0].inner_text(),
                        'exam_date': await cells[1].inner_text(),
                        'time_slot': await cells[2].inner_text(),
                        'classroom': await cells[3].inner_text()
                    })
            return results
        except PlaywrightTimeoutError as e:
            raise PortalTimeoutError(f"Timeout while scraping exam timetable: {str(e)}")
