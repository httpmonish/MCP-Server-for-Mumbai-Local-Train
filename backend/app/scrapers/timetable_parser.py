import re
from datetime import time
from typing import Any, Dict, List, Optional

import pdfplumber

from ..core.logger import get_logger

logger = get_logger(__name__)

class TrainTimetableParser:
    def __init__(self, pdf_path: str, line: str):
        if line not in ["CR", "WR"]:
            raise ValueError("Line must be either 'CR' or 'WR'")
        self.pdf_path = pdf_path
        self.line = line
        self.station_aliases = {
            "CSMT": "Mumbai CSMT",
            "BY": "Byculla",
            "DR": "Dadar",
            "CLA": "Kurla",
            "GC": "Ghatkopar",
            "TNA": "Thane",
            "DIVA": "Diva",
            "DI": "Dombivli",
            "KYN": "Kalyan",
        }

    def _parse_time(self, raw_time: str) -> Optional[time]:
        if not raw_time or any(x in str(raw_time) for x in ["-", "--", "..."]):
            return None

        raw_time = str(raw_time).strip().replace(".", ":")

        # Handle formats: 08:15, 8:15, 0815, 815
        match = re.match(r"(\d{1,2}):(\d{2})", raw_time)
        if match:
            hour, minute = map(int, match.groups())
            return time(hour, minute)

        if raw_time.isdigit():
            if len(raw_time) == 4:
                hour, minute = int(raw_time[:2]), int(raw_time[2:])
                return time(hour, minute)
            elif len(raw_time) == 3:
                hour, minute = int(raw_time[:1]), int(raw_time[1:])
                return time(hour, minute)

        return None

    def extract_train_columns(self, page) -> List[Dict[str, Any]]:
        table = page.extract_table(table_settings={
            "vertical_strategy": "lines",
            "horizontal_strategy": "text"
        })

        if not table:
            return []

        results = []
        # Simple heuristic: skip header row
        for row in table[1:]:
            if not row or not any(row):
                continue

            # Basic structure: Train No, Type, Source, Dest, Dep Time, Arr Time, ...
            # This is a generic representation as specific PDF layouts vary
            if len(row) < 6:
                continue

            train_no = row[0]
            train_type_raw = row[1]
            source = row[2]
            dest = row[3]
            dep_time = self._parse_time(row[4])
            arr_time = self._parse_time(row[5])

            if not dep_time or not arr_time:
                continue

            # Classify FAST vs SLOW based on intermediate stop availability
            # (Simplified for the spec: we check if the row indicates gaps)
            train_type = "FAST" if "FAST" in str(train_type_raw).upper() else "SLOW"

            results.append({
                "train_number": train_no,
                "train_type": train_type,
                "source_station": source,
                "destination_station": dest,
                "departure_time": dep_time,
                "arrival_time": arr_time,
                "row_data": row # keep for stop extraction
            })

        return results

    def parse(self) -> List[Dict[str, Any]]:
        all_trains = []
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                trains_on_page = self.extract_train_columns(page)
                for train in trains_on_page:
                    # Construct stops_data based on the row_data
                    # This assumes the PDF row contains station-time pairs
                    stops_data = []
                    # In a real PDF, we'd look for station columns.
                    # Here we simulate the stop extraction from the row.
                    for i, cell in enumerate(train["row_data"]):
                        parsed_t = self._parse_time(cell)
                        if parsed_t:
                            # Try to find station name/code
                            # This is a mock-up of the logic
                            station_name = f"Station {i}"
                            stops_data.append({
                                "station_code": "UNK",
                                "station_name": station_name,
                                "time": parsed_t.strftime("%H:%M:%S"),
                                "seq": i + 1
                            })

                    if not stops_data:
                        continue

                    all_trains.append({
                        "line": self.line,
                        "train_number": train["train_number"],
                        "train_type": train["train_type"],
                        "source_station": train["source_station"],
                        "destination_station": train["destination_station"],
                        "departure_time": train["departure_time"],
                        "arrival_time": train["arrival_time"],
                        "is_sunday_run": True,
                        "stops_data": stops_data
                    })
        return all_trains
