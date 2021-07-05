from django.db import models
from django.db.models import QuerySet
from typing import Optional
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    UserManager,
    PermissionsMixin,
)
from core.models import TimeStampModel
from django.conf import settings
from rest_framework_jwt.settings import api_settings


class CustomUserManager(UserManager):
    pass


class User(AbstractBaseUser, PermissionsMixin, TimeStampModel):
    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["name", "email"]

    is_active = models.BooleanField(
        db_column="IS_ACTIVE",
        default=True,
    )
    is_staff = models.BooleanField(
        db_column="IS_STAFF",
        default=False,
    )
    is_superuser = models.BooleanField(
        db_column="IS_SUPERUSER",
        default=False,
    )
    last_login = models.DateTimeField(
        db_column="LAST_LOGIN",
        blank=True,
        null=True,
        verbose_name="마지막로그인일시",
    )

    token = models.CharField(
        db_column="TOKEN",
        max_length=500,
        db_index=True,
        null=True,
    )
    expired_at = models.DateTimeField(
        db_column="EXPIRED_AT",
        db_index=True,
        null=True,
    )

    username = models.CharField(
        db_column="USER_ID",
        primary_key=True,
        # unique=True,
        max_length=20,
        verbose_name="사용자아이디",
    )
    name = models.CharField(
        db_column="NM",
        max_length=50,
        verbose_name="이름",
    )
    email = models.EmailField(
        db_column="EMAIL",
        max_length=50,
        verbose_name="이메일",
    )
    password = models.CharField(
        db_column="PASSWORD",
        max_length=128,
        verbose_name="비밀번호",
    )

    class Meta:
        # db_alias = "SYSTEM"
        db_alias = "default"
        db_table = "SYSTEM_USER"
        verbose_name = "사용자"


class IssuedTokenQuerySet(QuerySet):
    def expired(self, user: Optional[User]) -> QuerySet:
        return self.filter(expired_at__lt=timezone.now(), user=user)

    def active(self, user: Optional[User]) -> QuerySet:
        qs = self.filter(is_active=True, user=user)
        return qs


class IssuedToken(TimeStampModel):
    objects = IssuedTokenQuerySet.as_manager()

    token = models.CharField(
        db_column="TOKEN",
        max_length=500,
        primary_key=True,
        verbose_name="사용자인증토큰내용",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column="USER_ID",
        max_length=100,
        verbose_name="사용자식별자(사용자아이디)",
        on_delete=models.CASCADE,
    )
    expired_at = models.DateTimeField(
        db_column="EXPIRED_DT",
        blank=True,
        null=True,
        verbose_name="사용자인증만료일시",
    )

    class Meta:
        # db_alias = "SYSTEM"
        db_alias = "default"
        db_table = "SYSTEM_USER_TOKEN"
        verbose_name = "공통.사용자인증"

    def __str__(self):
        return "Issued token - {} - {}".format(self.user, self.token)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # jwt expire 시간을 넘겨, 더 이상 체킹할 필요가 없는 Token Records를 제거
        # self.__class__.objects.expired().delete()

    @classmethod
    def inactive_all_and_create(cls, user: User, token: str):
        # 기존에 발급된 모든 토큰들을 비활성화시킵니다.

        if cls.objects.filter(username=user.username).count() > 0:
            created_issued_token = cls.objects.filter(username=user.username).update(
                token=token,
                expired_at=timezone.now() + api_settings.JWT_EXPIRATION_DELTA,
            )
        else:
            created_issued_token = cls.objects.create(
                token=token,
                user=user,
                is_active=True,
                is_authenticated=True,
                is_staff=False,
                is_anonymous=False,
                is_superuser=False,
                expired_at=timezone.now() + api_settings.JWT_EXPIRATION_DELTA,
            )
        return created_issued_token
