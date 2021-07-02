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

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    token = models.CharField(max_length=500, db_index=True, null=True)
    expired_at = models.DateTimeField(db_index=True, null=True)

    username = models.CharField(
        db_column="USER_ID",
        unique=True,
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
        return self.filter(expires_at__lt=timezone.now(), user=user)

    def active(self, user: Optional[User]) -> QuerySet:
        qs = self.filter(is_active=True, user=user)
        return qs


class IssuedToken(TimeStampModel):
    objects = IssuedTokenQuerySet.as_manager()

    token = models.CharField(
        db_column="USER_ACCREDIT_TOKEN_CONTENT",
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
    is_active = models.BooleanField(
        db_column="USER_ACCREDIT_LOGIN_FG",
        verbose_name="사용자인증로그인여부",
    )
    is_staff = models.BooleanField(
        db_column="USER_ACCREDIT_STAFF_FG",
        verbose_name="사용자인증직원여부",
    )
    is_anonymous = models.BooleanField(
        db_column="USER_ACCREDIT_UNSIGN_FG",
        verbose_name="사용자인증무기명여부",
    )
    is_authenticated = models.BooleanField(
        db_column="USER_ACCREDIT_AUTH_FG",
        verbose_name="사용자인증권한여부",
    )
    is_superuser = models.BooleanField(
        db_column="USER_ACCREDIT_BEST_MNG_USER_FG",
        verbose_name="사용자인증최고관리사용자여부",
    )
    expires_at = models.DateTimeField(
        db_column="USER_ACCREDIT_EXPIRE_DT",
        blank=True,
        null=True,
        verbose_name="사용자인증만료일시",
    )
    created_at = models.DateTimeField(
        db_column="USER_ACCREDIT_CREATE_DT",
        blank=True,
        null=True,
        verbose_name="사용자인증생성일시",
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
                expires_at=timezone.now() + api_settings.JWT_EXPIRATION_DELTA,
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
                expires_at=timezone.now() + api_settings.JWT_EXPIRATION_DELTA,
            )
        return created_issued_token
