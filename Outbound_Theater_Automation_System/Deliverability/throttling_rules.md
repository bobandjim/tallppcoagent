# Throttling Rules

## Purpose
Prevent sending too many emails too quickly, which triggers spam filters and damages domain reputation.

## Config Location
`config/settings.yaml` → `deliverability` block:
```yaml
deliverability:
  max_sends_per_day: 50
  delay_between_sends_seconds: 90
  current_week: 1
```

## Rules

### Daily Cap
- `max_sends_per_day` is enforced in `DeliverabilityGuard._check_throttle()`
- Counter resets at midnight (local system time)
- When limit is reached: `DailyLimitReached` exception is raised, run stops cleanly
- Never artificially increase the limit mid-day to compensate

### Per-Send Delay
- `delay_between_sends_seconds` sets the sleep time between each individual send
- Default: 90 seconds (40 sends/hour max)
- Never set to 0 — always maintain a delay even at low volume

### Warm-Up Caps by Week

| Week | `max_sends_per_day` | `delay_between_sends_seconds` |
|------|--------------------|-----------------------------|
| 1    | 10                 | 90                          |
| 2    | 25                 | 90                          |
| 3    | 50                 | 60                          |
| 4+   | 100                | 45                          |

Update both values together when advancing warm-up weeks.

## How Throttle Is Enforced in Code

```python
# src/email/deliverability.py — DeliverabilityGuard
def _check_throttle(self) -> None:
    self._reset_if_new_day()
    if self._sends_today >= self.max_per_day:
        raise DailyLimitReached(...)
```

After each successful send:
```python
self._sends_today += 1
time.sleep(self.delay_seconds)
```

## Best Practices
- Run the sequence runner once per day (morning preferred)
- Do not run multiple instances simultaneously — counters are in-memory per process
- If a run is interrupted mid-day, the next run will re-count from 0 (conservative; some sends may be "lost" from the daily count — acceptable)

---

## Drop-In Reusability Notes
The throttling logic in `DeliverabilityGuard` is fully configurable via YAML. For a new project:
1. Set `max_sends_per_day` to the current warm-up week value
2. Set `delay_between_sends_seconds` based on desired send rate
3. Advance values weekly per the warm-up schedule
No code changes needed — config only.
