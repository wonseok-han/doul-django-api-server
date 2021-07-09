from apps.system.choices import UseYnChoices
from core.models.abstract import TimeStampModel
from core.models.fields import OrderIntegerField
from django.db import models


class SystemAuth(TimeStampModel):
    """
    시스템 권한 모델
    """

    auth_cd_key = models.CharField(
        db_column="AUTH_CD_KEY",
        primary_key=True,
        max_length=80,
        verbose_name="시스템권한식별자(시스템구분코드/권한코드)",
    )
    system_div_cd = models.CharField(
        db_column="SYSTEM_DIV_CD",
        max_length=40,
        verbose_name="시스템구분코드",
    )
    auth_cd = models.CharField(
        db_column="AUTH_CD",
        max_length=40,
        verbose_name="권한코드",
    )
    auth_nm = models.CharField(
        db_column="AUTH_NM",
        max_length=100,
        verbose_name="권한명",
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

    class Meta:
        # TODO: 해당 모델의 DB로 변경하세요.
        # db_alias = "SYSTEM"
        db_alias = "default"
        db_table = "SYSTEM_AUTH"
        verbose_name = "권한정보"

        constraints = [
            models.UniqueConstraint(
                fields=["system_div_cd", "auth_cd"],
                name="system_auth_unique",
            ),
        ]
        ordering = ["order", "system_div_cd", "auth_cd", "auth_nm"]


class SystemMenuAuth(TimeStampModel):
    """
    시스템 메뉴권한 모델
    """

    menu_auth_cd_key = models.CharField(
        db_column="MENU_AUTH_CD_KEY",
        primary_key=True,
        max_length=110,
        verbose_name="메뉴권한식별자(시스템권한식별자/메뉴식별자)",
    )
    search_use_yn = models.CharField(
        db_column="SEARCH_USE_YN",
        max_length=1,
        choices=UseYnChoices.choices,
        default=UseYnChoices.사용,
        verbose_name="조회권한여부",
    )
    new_use_yn = models.CharField(
        db_column="NEW_USE_YN",
        max_length=1,
        choices=UseYnChoices.choices,
        default=UseYnChoices.사용,
        verbose_name="신규권한여부",
    )
    delete_use_yn = models.CharField(
        db_column="DELETE_USE_YN",
        max_length=1,
        choices=UseYnChoices.choices,
        default=UseYnChoices.사용,
        verbose_name="삭제권한여부",
    )
    save_use_yn = models.CharField(
        db_column="SAVE_USE_YN",
        max_length=1,
        choices=UseYnChoices.choices,
        default=UseYnChoices.사용,
        verbose_name="삭제권한여부",
    )
    excel_use_yn = models.CharField(
        db_column="EXCEL_USE_YN",
        max_length=1,
        choices=UseYnChoices.choices,
        default=UseYnChoices.사용,
        verbose_name="엑셀권한여부",
    )
    print_use_yn = models.CharField(
        db_column="PRINT_USE_YN",
        max_length=1,
        choices=UseYnChoices.choices,
        default=UseYnChoices.사용,
        verbose_name="출력권한여부",
    )
    remark = models.TextField(
        db_column="REMARK",
        blank=True,
        null=True,
        verbose_name="비고",
    )

    # Relation Fields
    system_auth = models.ForeignKey(
        "SystemAuth",
        on_delete=models.DO_NOTHING,
        db_column="AUTH_CD_KEY",
        verbose_name="시스템권한식별자",
    )
    system_menu = models.ForeignKey(
        "system.SystemMenu",
        on_delete=models.DO_NOTHING,
        db_column="menu_cd_key",
        verbose_name="메뉴식별자",
    )

    class Meta:
        # TODO: 해당 모델의 DB로 변경하세요.
        # db_alias = "SYSTEM"
        db_alias = "default"
        db_table = "SYSTEM_MENU_AUTH"
        verbose_name = "메뉴권한"

        constraints = [
            models.UniqueConstraint(
                fields=["system_auth", "system_menu"],
                name="system_menu_auth_unique",
            ),
        ]


class SystemUserAuth(TimeStampModel):
    """
    시스템 사용자권한 모델
    """

    user_auth_cd_ky = models.CharField(
        db_column="USER_AUTH_CD_KEY",
        primary_key=True,
        max_length=100,
        verbose_name="사용자권한식별자(시스템권한식별자/사용자ID)",
    )
    remark = models.TextField(
        db_column="REMARK",
        blank=True,
        null=True,
        verbose_name="비고",
    )

    # Relation Fields
    system_auth = models.ForeignKey(
        "SystemAuth",
        on_delete=models.DO_NOTHING,
        db_column="AUTH_CD_KEY",
        verbose_name="시스템권한식별자",
    )
    system_user = models.ForeignKey(
        "account.User",
        on_delete=models.DO_NOTHING,
        db_column="USER_ID",
        verbose_name="사용자ID",
    )

    class Meta:
        # TODO: 해당 모델의 DB로 변경하세요.
        # db_alias = "SYSTEM"
        db_alias = "default"
        db_table = "SYSTEM_USER_AUTH"
        verbose_name = "사용자권한"

        constraints = [
            models.UniqueConstraint(
                fields=["system_auth", "system_user"],
                name="system_user_auth_unique",
            ),
        ]


class SystemUserGroupAuth(TimeStampModel):
    """
    시스템 사용자그룹권한 모델
    """

    user_group_auth_cd_ky = models.CharField(
        db_column="USER_GROUP_AUTH_CD_KEY",
        primary_key=True,
        max_length=100,
        verbose_name="그룹권한식별자(시스템권한식별자/그룹식별자)",
    )
    remark = models.TextField(
        db_column="REMARK",
        blank=True,
        null=True,
        verbose_name="비고",
    )

    # Relation Fields
    system_auth = models.ForeignKey(
        "SystemAuth",
        on_delete=models.DO_NOTHING,
        db_column="AUTH_CD_KEY",
        verbose_name="시스템권한식별자",
    )
    system_group = models.ForeignKey(
        "system.SystemDepartment",
        on_delete=models.DO_NOTHING,
        db_column="DEPT_CD",
        verbose_name="소속코드",
    )

    class Meta:
        # TODO: 해당 모델의 DB로 변경하세요.
        # db_alias = "SYSTEM"
        db_alias = "default"
        db_table = "SYSTEM_USER_GROUP_AUTH"
        verbose_name = "사용자권한"

        constraints = [
            models.UniqueConstraint(
                fields=["system_auth", "system_group"],
                name="system_user_group_auth_unique",
            ),
        ]
