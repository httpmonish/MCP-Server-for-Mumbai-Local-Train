from typing import Any, Dict, List

from playwright.async_api import Page

from ..base_adapter import BasePortalAdapter, CampusAdapterRegistry
from ..exceptions import PortalAuthenticationError, PortalSelectorError, PortalTimeoutError


@CampusAdapterRegistry.register("MU_STANDARD")
class MUStandardAdapter(BasePortalAdapter):
    campus_code: str = "MU_STANDARD"
    campus_name: str = "University of Mumbai Standard ERP"
    base_url: str = "https://mu.ac.in/portal"

    async def authenticate(self, page: Page, username: str, password: str) -> None:
        try:
            await page.goto(f"{self.base_url}/login", timeout=15000)
            await page.fill('input[name="username"], input[name="roll_no"]', username)
            await page.fill('input[name="password"]', password)
            await page.click('button[type="submit"], input[type="submit"]')

            # Wait for dashboard indicator or invalid credentials banner
            try:
                await page.wait_for_selector(".dashboard-container, #student-nav", timeout=8000)
            except Exception:
                error_elem = await page.query_selector(".alert-danger, .error-message")
                if error_elem:
                    error_text = await error_elem.inner_text()
                    raise PortalAuthenticationError(f"Authentication failed: {error_text.strip()}")
                raise PortalTimeoutError("Timed out waiting for MU portal dashboard.")
        except (PortalAuthenticationError, PortalTimeoutError):
            raise
        except Exception as exc:
            raise PortalTimeoutError(f"MU portal login navigation error: {exc}") from exc

    async def parse_attendance(self, page: Page) -> List[Dict[str, Any]]:
        try:
            await page.goto(f"{self.base_url}/academic/attendance", timeout=15000)
            await page.wait_for_selector("table.attendance-grid, table#attendance-table", timeout=8000)

            records: List[Dict[str, Any]] = []
            rows = await page.query_selector_all("table.attendance-grid tbody tr, table#attendance-table tbody tr")

            for row in rows:
                cols = await row.query_selector_all("td")
                if len(cols) >= 4:
                    subject = (await cols[0].inner_text()).strip()
                    conducted = int((await cols[1].inner_text()).strip() or 0)
                    attended = int((await cols[2].inner_text()).strip() or 0)
                    pct_str = (await cols[3].inner_text()).strip().replace("%", "")
                    pct = float(pct_str) if pct_str else (attended / conducted * 100 if conducted > 0 else 0.0)

                    records.append(
                        {
                            "subject_name": subject,
                            "total_conducted": conducted,
                            "total_attended": attended,
                            "percentage": round(pct, 1),
                        }
                    )
            return records
        except Exception as exc:
            raise PortalSelectorError(f"Failed parsing MU attendance records: {exc}") from exc

    async def parse_exam_schedule(self, page: Page) -> List[Dict[str, Any]]:
        try:
            await page.goto(f"{self.base_url}/academic/exams", timeout=15000)
            await page.wait_for_selector("table.exam-grid, table#exam-table", timeout=8000)

            exams: List[Dict[str, Any]] = []
            rows = await page.query_selector_all("table.exam-grid tbody tr, table#exam-table tbody tr")

            for row in rows:
                cols = await row.query_selector_all("td")
                if len(cols) >= 4:
                    subject = (await cols[0].inner_text()).strip()
                    date_val = (await cols[1].inner_text()).strip()
                    time_slot = (await cols[2].inner_text()).strip()
                    classroom = (await cols[3].inner_text()).strip()

                    exams.append(
                        {
                            "subject_name": subject,
                            "exam_date": date_val,
                            "time_slot": time_slot,
                            "classroom": classroom,
                        }
                    )
            return exams
        except Exception as exc:
            raise PortalSelectorError(f"Failed parsing MU exam schedules: {exc}") from exc
