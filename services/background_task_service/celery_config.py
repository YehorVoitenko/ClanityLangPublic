from celery.schedules import crontab

beat_schedule = {
    "send-inactive-user-message-daily": {
        "task": "tasks.send_telegram_message",
        "schedule": crontab(hour=16, minute=30),
    },
    "update-free-term-sub-to-non": {
        "task": "tasks.update_free_term_sub_to_non",
        "schedule": crontab(hour=23, minute=0),
    },
    "update-promocodes-to-non-sub": {
        "task": "tasks.update_promocodes_to_non_sub",
        "schedule": crontab(hour=23, minute=0),
    },
    "update-user-subscription-levels": {
        "task": "tasks.update_user_subscription_levels",
        "schedule": crontab(hour=23, minute=0),
    },
}

timezone = "UTC"
