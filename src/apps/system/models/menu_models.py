from apps.system.choices import UseYnChoices, YnChoices
from core.models.abstract import TimeStampModel
from core.models.fields import ChineseCharField, EnglishCharField, OrderIntegerField
from django.core.exceptions import ValidationError
from django.db import models


class SystemMenu(TimeStampModel):
    """
    시스템 메뉴정보 모델
    """

    def program_yn_validator(self, value):
        """
        upper_menu_cd_key 값이 없는데 최하위 프로그램메뉴구분 값이 'Y'로 들어오면 Validation Error를 발생시킵니다.
        즉, 최하위 프로그램메뉴는 반드시 상위메뉴가 존재해야 합니다.
        """
        if value == YnChoices.YES and self.upper_menu_cd_key is None:
            message = "상위메뉴코드값이 없으면 최하위 프로그램메뉴가 될 수 없습니다."
            raise ValidationError(message)

    menu_cd_key = models.CharField(
        db_column="MENU_CD_KEY",
        primary_key=True,
        max_length=30,
        verbose_name="메뉴식별자(시스템구분코드/메뉴코드)",
    )
    system_div_cd = models.CharField(
        db_column="SYSTEM_DIV_CD",
        max_length=40,
        verbose_name="시스템구분코드",
    )
    menu_cd = models.CharField(
        db_column="MENU_CD",
        max_length=20,
        verbose_name="메뉴코드",
    )
    menu_nm = models.CharField(
        db_column="MENU_NM",
        max_length=100,
        verbose_name="메뉴명",
    )
    menu_cd_eng_nm = EnglishCharField(
        db_column="MENU_CD_ENG_NM",
        max_length=100,
        blank=True,
        verbose_name="메뉴영문명",
    )
    menu_cd_chn_nm = ChineseCharField(
        db_column="MENU_CD_CHN_NM",
        max_length=100,
        blank=True,
        verbose_name="메뉴중문명",
    )
    program_yn = models.CharField(
        db_column="PROGRAM_YN",
        max_length=1,
        choices=YnChoices.choices,
        default=YnChoices.NO,
        validators=[program_yn_validator],
        verbose_name="프로그램메뉴구분",
    )
    order = OrderIntegerField(
        db_column="ORDER",
        verbose_name="정렬순서",
    )
    use_yn = models.CharField(
        db_column="USE_YN",
        max_length=1,
        choices=UseYnChoices.choices,
        default=UseYnChoices.사용,
        verbose_name="사용여부",
    )
    remark = models.TextField(
        db_column="REMARK",
        blank=True,
        null=True,
        verbose_name="비고",
    )

    # Relation Fields
    upper_menu_cd_key = models.ForeignKey(
        "self",
        on_delete=models.DO_NOTHING,
        db_column="UPPER_MENU_CD_KEY",
        null=True,
        verbose_name="상위메뉴식별자(시스템구분코드/메뉴코드)",
    )

    class Meta:
        # TODO: 해당 모델의 DB로 변경하세요.
        # db_alias = "SYSTEM"
        db_alias = "default"
        db_table = "SYSTEM_MENU"
        verbose_name = "시스템메뉴"

        constraints = [
            models.UniqueConstraint(
                fields=["system_div_cd", "menu_cd"],
                name="system_menu_unique",
            ),
        ]
        ordering = ["upper_menu_cd_key_id", "order"]

    def save(self, *args, **kwargs):
        """
        모델 저장시 menu_cd_key system_div_cd/menu_cd 조합으로 저장합니다.
        """
        if not self.menu_cd_key:
            self.common_cd_key = f"{self.system_div_cd}/{self.menu_cd}"

        return super().save(*args, **kwargs)
