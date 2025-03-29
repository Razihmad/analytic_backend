CACHE_NAMES = {
    "SC_ACCESS_TOKEN": {
        "key": "sc-access-token-{user_id}-{amazon_seller_id}",
        "timeout": 3600,
    },
    "SC_REFRESH_TOKEN": {
        "key": "sc-refresh-token-{user_id}-{amazon_seller_id}",
        "timeout": 24 * 60 * 60,
    },
    "ADS_ACCESS_TOKEN": {
        "key": "ads-access-token-{user_id}-{amazon_seller_id}-{region}",
        "timeout": 3600,
    },
    "ADS_REFRESH_TOKEN": {
        "key": "ads-refresh-token-{user_id}-{amazon_seller_id}",
        "timeout": 24 * 60 * 60,
    },
    "ADS_PROFILE_ID": {
        "key": "ads-profile-id-{user_id}-{amazon_seller_id}",
        "timeout": 24 * 60 * 60,
    },
}
