"""
MiroFish Loop Protector & Anti-Recursion Shield
Eliminates the "Dark Side of AI" (Infinite loops, hallucinatory recursion,
uncontrolled token drains, deadlocks, and repetitive oscillating states).
"""

import time
import functools
from typing import Callable, Any, Dict, Optional, Set
from config import LOOP_GUARD

class CircuitBreakerTrippedException(Exception):
    """Raised when an operation exceeds safe execution boundaries."""
    pass

class LoopProtector:
    """
    Guarantees deterministic, finite execution for AI agent workflows.
    Enforces hard bounds on simulation rounds, retries, and wall-clock time.
    """
    
    def __init__(self, max_iterations: int = 10, max_rounds: int = None, timeout_seconds: float = None):
        self.max_iterations = max_rounds if max_rounds is not None else max_iterations
        self.timeout_seconds = timeout_seconds or LOOP_GUARD.get("WATCHDOG_TIMEOUT_SECONDS", 30.0)
        self.start_time = time.time()
        self.iteration_count = 0
        self.visited_phases: Set[str] = set()
        self.state_history = []
        self.is_tripped = False

    def phase(self, phase_name: str):
        """
        Guards linear pipeline phases. Prevents recursive cyclic entry into the same phase.
        """
        elapsed = time.time() - self.start_time
        if elapsed > self.timeout_seconds:
            self.is_tripped = True
            raise CircuitBreakerTrippedException(
                f"[LoopProtector] WATCHDOG TIMEOUT in phase '{phase_name}': {round(elapsed, 2)}s elapsed."
            )

        if phase_name in self.visited_phases:
            # Re-entering the same pipeline phase is an illegal cycle
            self.is_tripped = True
            raise CircuitBreakerTrippedException(
                f"[LoopProtector] CYCLIC RECURSION DETECTED: Illegal re-entry into phase '{phase_name}'."
            )
        self.visited_phases.add(phase_name)

    def step(self, state_fingerprint: Optional[str] = None):
        """
        Called in iterative loops (e.g. multi-round debate).
        """
        self.iteration_count += 1
        elapsed = time.time() - self.start_time

        # 1. Timeout Check
        if elapsed > self.timeout_seconds:
            self.is_tripped = True
            raise CircuitBreakerTrippedException(
                f"[LoopProtector] WATCHDOG TIMEOUT: Execution took {round(elapsed, 2)}s "
                f"(Hard limit {self.timeout_seconds}s). Terminating loop safely."
            )

        # 2. Hard Max Iterations Check
        if self.iteration_count > self.max_iterations:
            self.is_tripped = True
            raise CircuitBreakerTrippedException(
                f"[LoopProtector] ITERATION OVERFLOW: Reached {self.iteration_count} iterations "
                f"(Hard limit {self.max_iterations}). Forcing consensus exit."
            )

        # 3. Oscillation / Repeat State Detection
        if state_fingerprint:
            if self.state_history.count(state_fingerprint) >= 2:
                self.is_tripped = True
                raise CircuitBreakerTrippedException(
                    f"[LoopProtector] OSCILLATION DETECTED: Agent state '{state_fingerprint}' repeated. Breaking loop."
                )
            self.state_history.append(state_fingerprint)

    def elapsed_time(self) -> float:
        return time.time() - self.start_time
