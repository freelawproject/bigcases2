from django_rq import job

@job
def fail_task() -> float:
    division_by_zero = 1 / 0
    return division_by_zero