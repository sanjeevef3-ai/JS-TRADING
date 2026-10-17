"""
Pattern Recognition Package for Indian Stock Market
Includes Candlestick Patterns, Classical Chart Patterns, and Comprehensive Scanner.
"""

from .candlestick import detect_candlestick_patterns
from .chart_patterns import detect_classical_patterns
from .pattern_engine import scan_all_patterns

__all__ = [
    "detect_candlestick_patterns",
    "detect_classical_patterns",
    "scan_all_patterns"
]
