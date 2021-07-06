from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
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


class OrderIntegerField(models.PositiveIntegerField):
    """
    정렬순서 필드 (1~100)
    """

    default_validators = [MinValueValidator(1), MaxValueValidator(100)]
