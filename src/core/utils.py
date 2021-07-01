from django.db import  models
from django.http import HttpRequest

def get_client_ip(request: HttpRequest) -> str:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

def add_meta_attr_to_model(attr):
    """
    모델의 Meta 옵션에 커스텀 속성을 추가합니다.
    """
    if attr not in models.options.DEFAULT_NAMES:
        models.options.DEFAULT_NAMES += (attr,)