from typing import Type

from django.apps import apps
from django.conf import settings
from django.db.models import Model

from core.models import PRE_SCANNED_DB_ALIAS_BY_TABLE_NAME


class Router:
    def _get_pre_scanned_db_alias(
        self, model_cls: Type[Model], default_db_alias: str = "default"
    ) -> str:
        db_table = model_cls._meta.db_table

        try:
            db_alias = PRE_SCANNED_DB_ALIAS_BY_TABLE_NAME[db_table]
        except KeyError:
            db_alias = default_db_alias

        return db_alias

    def db_for_read(self, model_cls: Type[Model], **hints) -> str:
        """
        DB read 시에 참조할 DB Alias를 반환

        조회 시에는 default DB 로부터 시작하여, 다른 DB에 대해서는 모든 테이블에 DB NAME 을 붙여서,
        멀티 데이터베이스에서 JOIN 을 지원토록 합니다.

        다중 DB 간의 JOIN을 지원할 때에는 default connection을 통해서
        쿼리가 수행되도록 합니다.

        :param model_cls: 장고 모델 클래스
        :param hints:

        :return: model_cls 관련된 Table이 속한 DB ALIAS 문자열
        """

        if settings.DB_MULTI_JOIN:
            return "default"

        return self._get_pre_scanned_db_alias(model_cls)

    def db_for_write(self, model_cls: Type[Model], **hints) -> str:
        """
        DB write 시에 참조할 DB Alias를 반환

        :param model_cls: 장고 모델 클래스
        :param hints:

        :return: model_cls 관련된 Table이 속한 DB ALIAS 문자열
        """

        return self._get_pre_scanned_db_alias(model_cls)

    def allow_relation(self, model_obj1: Model, model_obj2: Model, **hints) -> bool:
        """
        두 모델 인스턴스 간에 관계 설정이 가능한 것인지 여부를 체크할 때 호출이 됩니다.

        만약 Post모델의 author=FK(settings.AUTH_USER_MODEL) 관계일 때,
        본 메서드에서 False를 반환하면 아래 코드는 Relation 불가 판정으로 에러가 발생하게 됩니다.

        >>> post.author = request.user

        이는 단순히 Validation 시에만 동작하며, 다중 데이터베이스를 사용할 때 Relation을 할당하지 못하도록 막는 역할을 합니다.
        우리는 다중 데이터베이스에 대해서 허용을 할 것이기 때문에, 같은 DB HOST/PORT일 때에는 허용토록 하겠습니다.

        :param model_obj1: Master 모델 객체
        :param model_obj2: Slave 모델 객체

        :return: 2개 모델 Instance 간의 Relation 허용 여부
        """

        # 일단은 같은 DB HOST/PORT를 체크하지 않고 True를 반환
        return True

    def allow_migrate(
        self, target_db_alias, app_label, model_name=None, **hints
    ) -> bool:
        """
        `python manage.py migrate` 명령 시에 실제로 Database 마이그레이션을 수행할 것인지 여부를 결정합니다.

        본 메서드에서 False를 반환할 경우, 해당 마이그레이션 작업은 실제로 수행되진 않지만
        수행한 것으로 `django_migrations`에 표기됩니다.

        :param target_db_alias:
        :param app_label:
        :param model_name:
        :param hints:

        :return: Migrate 허용여부를 반환
        """

        if model_name is None:
            db_alias = "default"
        else:
            model_cls = apps.get_model(app_label, model_name)
            if model_cls._meta.managed is False:
                return False

            db_alias = getattr(model_cls._meta, "db_alias", "default")

        is_migrate = target_db_alias == db_alias

        return is_migrate
