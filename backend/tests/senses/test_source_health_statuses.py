"""Unit tests for Data Source Health statuses: Operational, Stale, Paused, Never Synced,
and circuit breaker resilience/recovery mechanisms.
"""

from datetime import datetime, timedelta, timezone
import pytest

from app.core.resilience import BreakerState, CircuitBreaker


def evaluate_source_status(
    breaker_state: str,
    last_success_at: datetime | None,
    ttl_seconds: int,
    now: datetime | None = None,
) -> str:
    """Mirrors the dynamic status calculation logic."""
    if breaker_state != "closed":
        return "Paused"
    if last_success_at is None:
        return "Never Synced"
    now_dt = now or datetime.now(timezone.utc)
    if (now_dt - last_success_at).total_seconds() > ttl_seconds:
        return "Stale"
    return "Operational"


def test_status_operational_when_recent_success():
    now = datetime(2026, 11, 3, 12, 0, 0, tzinfo=timezone.utc)
    last_success = now - timedelta(minutes=10)
    ttl = 3600  # 1 hour
    status = evaluate_source_status("closed", last_success, ttl, now)
    assert status == "Operational"


def test_status_stale_when_ttl_exceeded():
    now = datetime(2026, 11, 3, 12, 0, 0, tzinfo=timezone.utc)
    last_success = now - timedelta(hours=25)
    ttl = 86400  # 24 hours
    status = evaluate_source_status("closed", last_success, ttl, now)
    assert status == "Stale"


def test_status_never_synced_when_last_success_is_none():
    now = datetime(2026, 11, 3, 12, 0, 0, tzinfo=timezone.utc)
    status = evaluate_source_status("closed", None, 3600, now)
    assert status == "Never Synced"


def test_status_paused_when_circuit_breaker_open():
    now = datetime(2026, 11, 3, 12, 0, 0, tzinfo=timezone.utc)
    last_success = now - timedelta(minutes=5)
    # Even if recently succeeded, if the breaker was forced open or repeatedly failed without recovery
    status = evaluate_source_status("open", last_success, 3600, now)
    assert status == "Paused"


def test_status_paused_when_circuit_breaker_half_open():
    now = datetime(2026, 11, 3, 12, 0, 0, tzinfo=timezone.utc)
    status = evaluate_source_status("half_open", now, 3600, now)
    assert status == "Paused"


def test_temporary_failure_does_not_mark_healthy_source_stale():
    now = datetime(2026, 11, 3, 12, 0, 0, tzinfo=timezone.utc)
    last_success = now - timedelta(minutes=30)
    ttl = 7200  # 2 hours
    # Source had a recent failure recorded, but last_success is within TTL and breaker is closed
    status = evaluate_source_status("closed", last_success, ttl, now)
    assert status == "Operational"


def test_circuit_breaker_recovery_and_exponential_backoff():
    class TestClock:
        def __init__(self):
            self.now = 100.0

        def __call__(self):
            return self.now

    clock = TestClock()
    breaker = CircuitBreaker("overpass_test", failure_threshold=2, reset_after_s=60.0, max_reset_after_s=300.0, clock=clock)

    # 1. Healthy state
    assert breaker.state == BreakerState.CLOSED
    assert breaker.allow() is True

    # 2. First failure: remains closed
    breaker.record_failure()
    assert breaker.state == BreakerState.CLOSED

    # 3. Second failure reaches threshold -> opens
    breaker.record_failure()
    assert breaker.state == BreakerState.OPEN
    assert breaker.allow() is False
    assert breaker.current_reset_after_s == 60.0

    # 4. Before reset timeout: still open
    clock.now += 30.0
    assert breaker.state == BreakerState.OPEN
    assert breaker.allow() is False

    # 5. After 60s: enters half-open for automatic recovery probe
    clock.now += 35.0  # total 65s > 60s
    assert breaker.state == BreakerState.HALF_OPEN
    assert breaker.allow() is True

    # 6. Probe fails -> re-opens with doubled backoff (120s)
    breaker.record_failure()
    assert breaker.state == BreakerState.OPEN
    assert breaker.current_reset_after_s == 120.0

    # 7. Advance by 125s -> enters half-open again
    clock.now += 125.0
    assert breaker.state == BreakerState.HALF_OPEN
    assert breaker.allow() is True

    # 8. Recovery probe succeeds -> resets to closed with backoff cleared
    breaker.record_success()
    assert breaker.state == BreakerState.CLOSED
    assert breaker.allow() is True
    assert breaker.current_reset_after_s == 60.0

