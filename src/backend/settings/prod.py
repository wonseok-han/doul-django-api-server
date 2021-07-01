from .common import *

DEBUG = env.bool("DEBUG", False)

# whitenoise 미들웨어는 SecurityMiddleware 다음에 위치해야만 합니다.
assert MIDDLEWARE[0] == "django.middleware.security.SecurityMiddleware"
MIDDLEWARE[1:1] = ["whitenoise.middleware.WhiteNoiseMiddleware"]

# AnomalyDetectMiddleware에서 참조
ALLOW_EMPTY_SIGNED_HEADER = env.bool("ALLOW_EMPTY_SIGNED_HEADER", False)
