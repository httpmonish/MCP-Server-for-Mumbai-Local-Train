import math
from datetime import datetime, timezone
from typing import Any, Dict, List

from ..models.transit_delay import TrainDelayReport


class DelayConsensusEngine:
    HALF_LIFE_MINUTES = 15.0  # Delay reports lose 50% credibility every 15 minutes
    CONFIRMATION_THRESHOLD = 2.5  # Minimum weighted score to mark a delay as verified

    def calculate_weighted_delay(self, reports: List[TrainDelayReport]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        weighted_delay_sum = 0.0
        total_weight = 0.0
        valid_reports_count = 0

        for report in reports:
            created = report.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)

            age = (now - created).total_seconds() / 60.0
            # Discard reports older than 45 minutes or future timestamps
            if age > 45.0 or age < 0:
                continue

            # Time-decay weighting based on half-life
            weight = math.pow(0.5, age / self.HALF_LIFE_MINUTES)
            weighted_delay_sum += float(report.reported_delay_minutes) * weight
            total_weight += weight
            valid_reports_count += 1

        if total_weight == 0.0:
            return {
                "verified": False,
                "delay_minutes": 0,
                "confidence": 0.0,
                "report_count": 0,
            }

        consensus_delay = round(weighted_delay_sum / total_weight)
        verified = total_weight >= self.CONFIRMATION_THRESHOLD

        return {
            "verified": verified,
            "delay_minutes": int(consensus_delay),
            "confidence": round(total_weight, 2),
            "report_count": len(reports),
        }
