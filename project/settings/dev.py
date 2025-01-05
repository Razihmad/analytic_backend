from .base import *  # noqa

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            "formatter": "verbose"
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "../logs/django_all_logs.log"),  # noqa
            "formatter": "simple",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
    "formatters": {
        "simple": {
            "format": "%(levelname)s %(message)s"
        },
        "verbose": {
            "format": "%(asctime)s | %(levelname)s | %(module)s  | %(funcName)d | %(message)s"
        }
    }
}
