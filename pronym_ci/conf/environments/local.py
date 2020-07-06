from pronym_ci.conf.generic.settings import *  # noqa


DEBUG = True
DEBUG_STATIC_FILES = True
RAISE_ON_500 = True

ALLOWED_HOSTS = ['*']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        }
    }
}

REPO_BASE_PATH = os.path.join(os.path.dirname(BASE_DIR), 'repo')
