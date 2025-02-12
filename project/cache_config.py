CACHE_NAMES = {
    "SC_ACCESS_TOKEN": {
        "key": "sc-access-token-{user_id}",
        "timeout": 3600,
    },
    "SCC_REFRESH_TOKEN": {
        "key": "sc-refresh-token-{user_id}",
        "timeout": 24 * 60 * 60,
    },
    "REPORT_CANCELLED": {
        "key": "is-report-cancelled-{seller_id}",
        "timeout": 24 * 60 * 60,
    },
}
