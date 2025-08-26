from datetime import datetime
from typing import Callable

import pytz


def run_background_tasks(local_time: datetime, tasks: list[Callable]):
    ukraine_tz = pytz.timezone("Europe/Kyiv")
    local_run_at = ukraine_tz.localize(local_time)
    run_at_utc = local_run_at.astimezone(pytz.UTC)

    for task in tasks:
        task.apply_async(eta=run_at_utc)
