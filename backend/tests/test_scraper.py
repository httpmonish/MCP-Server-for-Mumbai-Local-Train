from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from app.scrapers.college_portal import CollegePortalScraper


@pytest.mark.asyncio
async def test_offline_scraper_dom_parser_with_fixture():
    fixture_path = Path(__file__).parent / "fixtures" / "attendance_fixture.html"
    assert fixture_path.exists()

    scraper = CollegePortalScraper(base_url="https://mock.portal")

    # Mock page elements based on fixture structure
    mock_cell_1 = AsyncMock()
    mock_cell_1.inner_text = AsyncMock(return_value="Data Structures")
    mock_cell_2 = AsyncMock()
    mock_cell_2.inner_text = AsyncMock(return_value="40")
    mock_cell_3 = AsyncMock()
    mock_cell_3.inner_text = AsyncMock(return_value="30")
    mock_cell_4 = AsyncMock()
    mock_cell_4.inner_text = AsyncMock(return_value="75.0%")

    mock_row = AsyncMock()
    mock_row.query_selector_all = AsyncMock(
        return_value=[mock_cell_1, mock_cell_2, mock_cell_3, mock_cell_4]
    )

    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.wait_for_selector = AsyncMock()
    mock_page.query_selector_all = AsyncMock(return_value=[mock_row])

    results = await scraper.scrape_attendance(mock_page)

    assert len(results) == 1
    assert results[0]["subject_name"] == "Data Structures"
    assert results[0]["total_conducted"] == 40
    assert results[0]["total_attended"] == 30
    assert results[0]["percentage"] == 75.0
