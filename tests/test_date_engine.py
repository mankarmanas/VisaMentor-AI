from datetime import date, timedelta
from src.rag.date_engine import DateEngine


engine = DateEngine()


def test_cpt_eligibility_dates():
    result = engine.calculate(
        program_start_date=date(2024, 9, 1),
        program_end_date=date(2026, 5, 15),
        stem_eligible=False,
    )
    # CPT eligible after 9 months = June 2025
    assert result["cpt"]["eligible_date"] == "2025-06-01"


def test_opt_apply_window_opens_90_days_before_end():
    program_end = date(2026, 5, 15)
    result = engine.calculate(
        program_start_date=date(2024, 9, 1),
        program_end_date=program_end,
        stem_eligible=False,
    )
    expected = (program_end - timedelta(days=90)).isoformat()
    assert result["opt"]["apply_window_opens"] == expected


def test_opt_end_date_is_365_days_after_start():
    program_end = date(2026, 5, 15)
    result = engine.calculate(
        program_start_date=date(2024, 9, 1),
        program_end_date=program_end,
        stem_eligible=False,
    )
    expected = (program_end + timedelta(days=365)).isoformat()
    assert result["opt"]["end_date"] == expected


def test_stem_opt_returned_when_eligible():
    result = engine.calculate(
        program_start_date=date(2024, 9, 1),
        program_end_date=date(2026, 5, 15),
        stem_eligible=True,
    )
    assert result["stem_opt"] is not None
    assert result["stem_opt"]["total_work_authorization_months"] == 36


def test_stem_opt_none_when_not_eligible():
    result = engine.calculate(
        program_start_date=date(2024, 9, 1),
        program_end_date=date(2026, 5, 15),
        stem_eligible=False,
    )
    assert result["stem_opt"] is None


def test_opt_grace_period_60_days_after_opt_end():
    program_end = date(2026, 5, 15)
    result = engine.calculate(
        program_start_date=date(2024, 9, 1),
        program_end_date=program_end,
        stem_eligible=False,
    )
    opt_end = date.fromisoformat(result["opt"]["end_date"])
    expected = (opt_end + timedelta(days=60)).isoformat()
    assert result["opt"]["grace_period_end"] == expected


def test_custom_opt_start_date():
    program_end = date(2026, 5, 15)
    opt_start = date(2026, 6, 1)
    result = engine.calculate(
        program_start_date=date(2024, 9, 1),
        program_end_date=program_end,
        stem_eligible=False,
        opt_start_date=opt_start,
    )
    expected = (opt_start + timedelta(days=365)).isoformat()
    assert result["opt"]["end_date"] == expected