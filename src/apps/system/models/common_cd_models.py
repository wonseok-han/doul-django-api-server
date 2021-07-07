from apps.system.choices import UseYnChoices
from core.models.abstract import TimeStampModel
from core.models.fields import ChineseCharField, EnglishCharField, OrderIntegerField
from django.db import models


class SystemCommonCodeMaster(TimeStampModel):
    """
    공통코드 Master 모델
    """

    common_cd_key = models.CharField(
        db_column="COMMON_CD_KEY",
        primary_key=True,
        max_length=80,
        verbose_name="공통코드식별자(시스템구분코드/공통코드)",
    )
    system_div_cd = models.CharField(
        db_column="SYSTEM_DIV_CD",
        unique=True,
        max_length=40,
        verbose_name="시스템구분코드",
    )
    common_cd = models.CharField(
        db_column="COMMON_CD",
        unique=True,
        max_length=40,
        verbose_name="공통코드",
    )
    common_cd_nm = models.CharField(
        db_column="COMMON_CD_NM",
        max_length=100,
        verbose_name="공통코드명",
    )
    common_cd_eng_nm = EnglishCharField(
        db_column="COMMON_CD_ENG_NM",
        max_length=100,
        null=True,
        verbose_name="공통코드영문명",
    )
    common_cd_chn_nm = ChineseCharField(
        db_column="COMMON_CD_CHN_NM",
        max_length=100,
        null=True,
        verbose_name="공통코드중문명",
    )
    common_content1 = models.CharField(
        db_column="COMMON_CONTENT1",
        max_length=40,
        null=True,
        verbose_name="내용1",
    )
    common_content2 = models.CharField(
        db_column="COMMON_CONTENT2",
        max_length=40,
        null=True,
        verbose_name="내용2",
    )
    common_content3 = models.CharField(
        db_column="COMMON_CONTENT3",
        max_length=40,
        null=True,
        verbose_name="내용3",
    )
    common_content4 = models.CharField(
        db_column="COMMON_CONTENT4",
        max_length=40,
        null=True,
        verbose_name="내용4",
    )
    common_content5 = models.CharField(
        db_column="COMMON_CONTENT5",
        max_length=40,
        null=True,
        verbose_name="내용5",
    )
    order = OrderIntegerField(
        db_column="ORDER",
        verbose_name="정렬순서",
        blank=True,
        null=True,
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

    class Meta:
        # TODO: 해당 모델의 DB로 변경하세요.
        # db_alias = "SYSTEM"
        db_alias = "default"
        db_table = "SYSTEM_COMMON_CODE_MASTER"
        verbose_name = "공통코드"

        constraints = [
            models.UniqueConstraint(
                fields=["system_div_cd", "common_cd"],
                name="system_common_code_master_unique",
            ),
        ]
        ordering = ["system_div_cd", "order", "common_cd", "common_cd_nm"]

    def save(self, *args, **kwargs):
        """
        모델 저장시 common_cd_key는 system_div_cd/common_cd의 조합으로 저장합니다.
        """
        if not self.common_cd_key:
            self.common_cd_key = f"{self.system_div_cd}/{self.common_cd}"

        return super().save(*args, **kwargs)


class SystemCommonCodeDetail(TimeStampModel):
    """
    공통코드 Detail 모델
    """

    common_dtl_cd_key = models.CharField(
        db_column="COMMON_DTL_CD_KEY",
        primary_key=True,
        max_length=120,
        verbose_name="공통상세코드식별자(시스템구분코드/공통코드/공통상세코드)",
    )
    common_dtl_cd = models.CharField(
        db_column="COMMON_DTL_CD",
        unique=True,
        max_length=40,
        verbose_name="공통상세코드",
    )
    common_dtl_cd_nm = models.CharField(
        db_column="COMMON_DTL_CD_NM",
        max_length=100,
        verbose_name="공통상세코드명",
    )
    common_dtl_cd_eng_nm = EnglishCharField(
        db_column="COMMON_DTL_CD_ENG_NM",
        max_length=100,
        blank=True,
        verbose_name="공통상세코드영문명",
    )
    common_dtl_cd_chn_nm = ChineseCharField(
        db_column="COMMON_DTL_CD_CHN_NM",
        max_length=100,
        blank=True,
        verbose_name="공통상세코드중문명",
    )
    common_content1 = models.CharField(
        db_column="COMMON_CONTENT1",
        max_length=40,
        blank=True,
        verbose_name="내용1",
    )
    common_content2 = models.CharField(
        db_column="COMMON_CONTENT2",
        max_length=40,
        blank=True,
        verbose_name="내용2",
    )
    common_content3 = models.CharField(
        db_column="COMMON_CONTENT3",
        max_length=40,
        blank=True,
        verbose_name="내용3",
    )
    common_content4 = models.CharField(
        db_column="COMMON_CONTENT4",
        max_length=40,
        blank=True,
        verbose_name="내용4",
    )
    common_content5 = models.CharField(
        db_column="COMMON_CONTENT5",
        max_length=40,
        blank=True,
        verbose_name="내용5",
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
    system_common_code_master = models.ForeignKey(
        "SystemCommonCodeMaster",
        on_delete=models.DO_NOTHING,
        unique=True,
        db_column="COMMON_CD_KEY",
        verbose_name="공통코드식별자(시스템구분코드/공통코드)",
    )

    class Meta:
        # TODO: 해당 모델의 DB로 변경하세요.
        # db_alias = "SYSTEM"
        db_alias = "default"
        db_table = "SYSTEM_COMMON_CODE_DETAIL"
        verbose_name = "공통상세코드"

        constraints = [
            models.UniqueConstraint(
                fields=["system_common_code_master_id", "common_dtl_cd"],
                name="system_common_code_detail_unique",
            ),
        ]
        ordering = [
            "system_common_code_master",
            "order",
            "common_dtl_cd",
            "common_dtl_cd_nm",
        ]

    def save(self, *args, **kwargs):
        """
        모델 저장시 common_dtl_cd_key system_common_code_master_id/common_dtl_cd 조합으로 저장합니다.
        """
        if not self.common_dtl_cd_key:
            self.common_cd_key = f"{self.system_div_cd}/{self.common_dtl_cd}"

        return super().save(*args, **kwargs)
