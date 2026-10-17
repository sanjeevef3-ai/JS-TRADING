"""
Dynamic Pattern Weight Calibrator
Calibrates agent confidence weights dynamically based on continuous learning data.
"""

from typing import Dict, Any
from .pattern_ledger import PatternLedger

class WeightCalibrator:
    """Self-adjusting calibrator for pattern confidence and agent weights."""
    
    def __init__(self):
        self.ledger = PatternLedger()

    def get_calibrated_confidence(self, pattern_name: str, base_confidence: float) -> float:
        """
        Adjusts base confidence according to learned empirical win rate.
        Formula: Calibrated = (0.6 * base) + (0.4 * empirical_win_rate)
        """
        stats = self.ledger.get_pattern_stats()
        if pattern_name in stats:
            empirical_wr = stats[pattern_name].get("win_rate", base_confidence)
            calibrated = (0.6 * base_confidence) + (0.4 * empirical_wr)
            return round(calibrated, 1)
        return base_confidence

    def get_all_calibrated_weights(self) -> Dict[str, Any]:
        """Returns full table of calibrated pattern win-rates and weights."""
        return self.ledger.get_pattern_stats()
