from apps.system.choices import UseYnChoices
from core.models.abstract import TimeStampModel
from core.models.fields import EnglishCharField, OrderIntegerField
from django.db import models


class SystemDepartment(TimeStampModel):
    """
    사용자 소속 모델
    """

    dept_cd_key = models.CharField(
        db_column="DEPT_CD_KEY",
        primary_key=True,
        max_length=20,
        verbose_name="소속식별자",
    )
    dept_cd = models.CharField(
        db_column="DEPT_CD",
        max_length=20,
        verbose_name="소속코드",
    )
    dept_nm = models.CharField(
        db_column="DEPT_NM",
        max_length=100,
        verbose_name="소속명",
    )
    dept_eng_nm = EnglishCharField(
        db_column="DEPT_ENG_NM",
        max_length=100,
        verbose_name="소속영문명",
    )
    order = OrderIntegerField(
        db_column="ORDER",
        blank=True,
        null=True,
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
    upper_dept_cd_key = models.ForeignKey(
        "self",
        on_delete=models.DO_NOTHING,
        db_column="UPPER_DEPT_CD_KEY",
        null=True,
        verbose_name="상위소속식별자",
    )

    class Meta:
        # TODO: 해당 모델의 DB로 변경하세요.
        # db_alias = "SYSTEM"
        db_alias = "default"
        db_table = "SYSTEM_DEPT"
        verbose_name = "소속"

        constraints = [
            models.UniqueConstraint(
                fields=["dept_cd"],
                name="system_department_unique",
            ),
        ]

    def save(self, *args, **kwargs):
        """
        모델 저장시 dept_cd_key는 dept_cd로 저장됩니다.
        """
        if not self.dept_cd_key:
            self.dept_cd_key = f"{self.dept_cd_key}"

        return super().save(*args, **kwargs)
