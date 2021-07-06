from django.db.models import TextChoices


class UseYnChoices(TextChoices):
    """
    사용여부 Choices
    """

    사용 = ("Y", "사용")
    미사용 = ("N", "미사용")
