from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


# USCIS Rules — update these constants if regulations change
# Source: uscis.gov/opt | Last verified: June 2026
OPT_APPLY_WINDOW_DAYS = 90        # days before program end to start applying
OPT_GRACE_PERIOD_DAYS = 60        # days after program end to submit application
OPT_DURATION_DAYS = 365           # 12 months work authorization
OPT_POST_GRACE_DAYS = 60          # days after OPT ends before must leave USA
STEM_OPT_DURATION_DAYS = 730      # 24 months extension
STEM_OPT_APPLY_WINDOW_DAYS = 90   # days before OPT end to apply for STEM
CPT_ELIGIBLE_MONTHS = 9           # full academic year before CPT eligibility


class DateEngine:

    def calculate(
        self,
        program_start_date: date,
        program_end_date: date,
        stem_eligible: bool,
        opt_start_date: date = None,
    ) -> dict:

        today = date.today()
        dates = {}

        # CPT
        cpt_eligible_date = program_start_date + relativedelta(months=CPT_ELIGIBLE_MONTHS)
        dates["cpt"] = {
            "eligible_date": cpt_eligible_date.isoformat(),
            "is_eligible_now": today >= cpt_eligible_date,
            "days_until_eligible": max(0, (cpt_eligible_date - today).days),
        }

        # OPT
        opt_apply_window_opens = program_end_date - timedelta(days=OPT_APPLY_WINDOW_DAYS)
        opt_apply_deadline = program_end_date + timedelta(days=OPT_GRACE_PERIOD_DAYS)
        opt_start_date = opt_start_date if opt_start_date else program_end_date
        opt_end_date = opt_start_date + timedelta(days=OPT_DURATION_DAYS)
        opt_grace_period_end = opt_end_date + timedelta(days=OPT_POST_GRACE_DAYS)

        dates["opt"] = {
            "apply_window_opens": opt_apply_window_opens.isoformat(),
            "apply_deadline": opt_apply_deadline.isoformat(),
            "earliest_start_date": opt_start_date.isoformat(),
            "end_date": opt_end_date.isoformat(),
            "grace_period_end": opt_grace_period_end.isoformat(),
            "can_apply_now": today >= opt_apply_window_opens,
            "days_until_apply_window": max(0, (opt_apply_window_opens - today).days),
            "student_chosen_start": opt_start_date.isoformat() if opt_start_date else None,
        }

        # STEM OPT
        if stem_eligible:
            stem_apply_window_opens = opt_end_date - timedelta(days=STEM_OPT_APPLY_WINDOW_DAYS)
            stem_end_date = opt_end_date + timedelta(days=STEM_OPT_DURATION_DAYS)
            stem_grace_period_end = stem_end_date + timedelta(days=OPT_POST_GRACE_DAYS)

            dates["stem_opt"] = {
                "apply_window_opens": stem_apply_window_opens.isoformat(),
                "end_date": stem_end_date.isoformat(),
                "grace_period_end": stem_grace_period_end.isoformat(),
                "total_work_authorization_months": 36,
            }
        else:
            dates["stem_opt"] = None

        # Grace period after program ends (if no OPT filed)
        grace_period_end = program_end_date + timedelta(days=OPT_GRACE_PERIOD_DAYS)
        dates["grace_period"] = {
            "end_date": grace_period_end.isoformat(),
            "days_remaining": max(0, (grace_period_end - today).days),
        }

        # current status summary
        dates["current_status"] = self._get_current_status(
            today,
            program_end_date,
            opt_apply_window_opens,
            opt_apply_deadline,
            opt_end_date,
        )

        return dates

    def _get_current_status(
        self,
        today: date,
        program_end_date: date,
        opt_apply_window_opens: date,
        opt_apply_deadline: date,
        opt_end_date: date,
    ) -> str:
        if today < opt_apply_window_opens:
            days = (opt_apply_window_opens - today).days
            return f"OPT application window opens in {days} days ({opt_apply_window_opens.isoformat()})"
        elif today < program_end_date:
            return f"OPT application window is open — apply now. Program ends {program_end_date.isoformat()}"
        elif today <= opt_apply_deadline:
            days = (opt_apply_deadline - today).days
            return f"Program ended — {days} days left to submit OPT application (deadline {opt_apply_deadline.isoformat()})"
        elif today <= opt_end_date:
            days = (opt_end_date - today).days
            return f"OPT active — {days} days remaining until {opt_end_date.isoformat()}"
        else:
            return "OPT period has ended"