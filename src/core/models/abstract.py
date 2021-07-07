from django.db import models


class TimeStampModel(models.Model):
    insert_user_id = models.CharField(
        db_column="INS_USER_ID",
        max_length=20,
        default="dev",
        verbose_name="입력사용자아이디",
    )
    insert_user_ip = models.GenericIPAddressField(
        db_column="INS_USER_IP",
        max_length=20,
        default="127.0.0.1",
        verbose_name="입력사용자IP",
    )
    insert_date_time = models.DateTimeField(
        db_column="INS_DT",
        auto_now_add=True,
        verbose_name="입력일시",
    )
    update_user_id = models.CharField(
        db_column="UPD_USER_ID",
        max_length=20,
        blank=True,
        verbose_name="수정사용자아이디",
    )
    update_user_ip = models.GenericIPAddressField(
        db_column="UPD_USER_IP",
        max_length=40,
        blank=True,
        null=True,
        verbose_name="수정사용자IP",
    )
    update_date_time = models.DateTimeField(
        db_column="UPD_DT",
        blank=True,
        null=True,
        auto_now=True,
        verbose_name="수정일시",
    )

    class Meta:
        abstract = True
