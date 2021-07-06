from django.core.validators import RegexValidator
from django.db import models


class EnglishCharField(models.CharField):
    """
    영문_숫자 필드
    """

    default_validators = [RegexValidator(r"^[a-zA-Z\d\s]*$", message="영문, 숫자만 입력해주세요.")]


class ChineseCharField(models.CharField):
    """
    중문_숫자 필드
    """

    default_validators = [RegexValidator(r"^[一-龥\d\s]*$", message="중문, 숫자만 입력해주세요.")]
