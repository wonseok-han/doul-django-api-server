from .common import *

INSTALLED_APPS += [
    "debug_toolbar",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
] + MIDDLEWARE

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] += [
    "rest_framework.renderers.BrowsableAPIRenderer",
]

DEBUG_LOGGING = env.bool("DEBUG_LOGGING", True)

if DEBUG_LOGGING:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "ignore": {
                #     "()": "core.logging.IgnoreFilter",
                #     # 해당 패턴이 포함된 로그 메세지는 출력되지 않습니다.
                #     # 패턴은 대소문자를 무시하며, | 를 구분자로 하여 다수 패턴 등록할 수 있습니다.
                #     # 사용 예: LOG_IGNORE_PATTERNS 환경변수에 vw_lnk_orgnn|pa01t1 문자열 정의
                #     "ignore_patterns": env.str("LOG_IGNORE_PATTERNS", ""),
            }
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "filters": ["ignore"],
            }
        },
        "loggers": {
            "django.db.backends": {
                "handlers": ["console"],
                "level": "DEBUG",
            },
            # "planet.core": {
            #     "handlers": ["console"],
            #     "level": "DEBUG",
            # },
        },
    }

CORS_ORIGIN_ALLOW_ALL = True
