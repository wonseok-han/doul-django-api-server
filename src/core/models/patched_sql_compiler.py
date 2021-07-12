import re
import sys
from functools import cached_property
from typing import Dict

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import connections
from django.db.backends.signals import connection_created
from django.db.models.sql.compiler import (
    SQLCompiler,
    # FIXME: 이 객체를 통해서는 as_sql 오버라이딩이 되지 않습니다. sql_server 객체를 직접 임포트하여 처리합니다.
    SQLInsertCompiler,
    SQLUpdateCompiler,
    SQLDeleteCompiler,
    SQLAggregateCompiler,
)

# FIXME: sql_server는 mssql 전용 라이브러리
# from sql_server.pyodbc.compiler import (
#     SQLInsertCompiler,
# )  # FIXME: 왜 장고 compiler로는 as_sql 오버라이딩이 안 될까요?

from core.signals import app_ready
from core.utils import add_meta_attr_to_model


add_meta_attr_to_model("db_alias")


# 각 db table에 db명을 붙인 table source
_DB_TABLES_MAPPING: Dict[str, str] = {}

# 각 db table이 속한 db alias
# router의 db_for_write에서 사용됩니다.
PRE_SCANNED_DB_ALIAS_BY_TABLE_NAME: Dict[str, str] = {}


def handle_app_ready(**kwargs):
    # 프로세스 단위로 전역변수 형태로 _DB_TABLES_MAPPING 을 조사합니다.
    global _DB_TABLES_MAPPING

    if not _DB_TABLES_MAPPING:
        db_alias_dict_on_model_meta: Dict[str, str] = {
            model_cls._meta.db_table: model_cls._meta.db_alias
            for model_cls in apps.get_models()
            if hasattr(model_cls._meta, "db_table")
            and hasattr(model_cls._meta, "db_alias")
        }

        db_name_dict = {
            db_alias: db_settings["NAME"]
            for db_alias, db_settings in settings.DATABASES.items()
        }

        # 여러 Databases에 걸쳐서 중복된 이름의 table_name이 존재할 수 있습니다.
        for db_alias, db_settings in settings.DATABASES.items():
            connection = connections[db_alias]
            quote_name = connection.ops.quote_name
            is_sqlserver = "pyodbc" in db_settings["ENGINE"]
            is_sqlite = "sqlite" in db_settings["ENGINE"]

            table_names = connection.introspection.table_names()

            # view 목록을 획득하는 API 는 장고에서 지원하고 있지 않기에, 직접 쿼리를 통해 목록을 조회합니다.
            if is_sqlserver:
                with connection.cursor() as cursor:
                    # https://docs.microsoft.com/ko-kr/sql/relational-databases/system-compatibility-views/sys-sysobjects-transact-sql?view=sql-server-ver15
                    #  xtype : V (뷰), U (사용자 테이블), SQ (서비스 큐) 등
                    cursor.execute("SELECT name FROM sys.sysobjects WHERE xtype = 'V';")
                    view_names = [row[0] for row in cursor.fetchall()]
            else:
                # 다른 DB 엔진에 대해서는 구현되어 있지 않습니다.
                view_names = []

            for table_name in map(lambda s: s, table_names + view_names):
                current_db_alias = db_alias_dict_on_model_meta.get(table_name, db_alias)

                PRE_SCANNED_DB_ALIAS_BY_TABLE_NAME[table_name] = current_db_alias

                if is_sqlite:
                    db_name = current_db_alias
                else:
                    try:
                        db_name = (
                            current_db_alias
                            if db_name_dict["default"] == current_db_alias
                            else db_name_dict[current_db_alias]
                        )
                    except KeyError:
                        raise ImproperlyConfigured(
                            f"{current_db_alias} 데이터베이스 설정이 누락되었습니다."
                        )

                quoted_db_name = quote_name(db_name)
                quoted_table_name = quote_name(table_name)

                if is_sqlserver:
                    _DB_TABLES_MAPPING[
                        quoted_table_name
                    ] = f"{quoted_db_name}.{quote_name('dbo')}.{quoted_table_name}"
                else:
                    _DB_TABLES_MAPPING[
                        quoted_table_name
                    ] = f"{quoted_db_name}.{quoted_table_name}"


app_ready.connect(handle_app_ready, dispatch_uid="handle_app_ready")


class PatchSQL:
    @cached_property
    def patterns(self):
        patterns_ = []
        for table_name, table_name_with_db_name in _DB_TABLES_MAPPING.items():
            pattern = re.compile(re.escape(table_name), re.IGNORECASE)
            patterns_.append((pattern, table_name_with_db_name))
        return patterns_

    def __call__(self, sql: str) -> str:
        for pattern, table_name_with_db_name in self.patterns:
            sql = pattern.sub(table_name_with_db_name, sql)
        return sql


patch_sql = PatchSQL()


#
# Patch SQLCompiler Query for select
#


def patched_get_from_clause(self):
    """
    SQL from 절에서 table_name 문자열을 db_name.table_name 문자열로 변환하여,
    multi db 간의 JOIN을 가능케합니다.

    DB Router의 db_for_read에서는 "default" 만을 반환해야만 합니다.
    """

    from_, f_params = orig_get_from_clause(self)

    from_with_db_name = []
    for chunk in from_:
        chunk = patch_sql(chunk)
        from_with_db_name.append(chunk)

    return from_with_db_name, f_params


orig_get_from_clause = SQLCompiler.get_from_clause
SQLCompiler.get_from_clause = patched_get_from_clause
print("patched get_from_clause member function in SQLCompiler class.", file=sys.stderr)


#
# Patch SQLInsertCompiler Query for inesrt
#


def patched_as_sql_in_insert_compiler(self):
    for sql, params in orig_as_sql_in_insert_compiler(self):
        yield patch_sql(sql), params


orig_as_sql_in_insert_compiler = SQLInsertCompiler.as_sql
SQLInsertCompiler.as_sql = patched_as_sql_in_insert_compiler
print("patched as_sql member function in SQLInsertCompiler class.", file=sys.stderr)


#
# Patch SQLUpdateCompiler Query for update
#


def patched_as_sql_in_update_compiler(self):
    sql, args = orig_as_sql_in_update_compiler(self)
    return patch_sql(sql), args


orig_as_sql_in_update_compiler = SQLUpdateCompiler.as_sql
SQLUpdateCompiler.as_sql = patched_as_sql_in_update_compiler
print("patched as_sql member function in SQLUpdateCompiler class.", file=sys.stderr)


#
# Patch SQLDeleteCompiler Query for delete
#


def patched_as_sql_in_delete_compiler(self, query):
    sql, args = orig_as_sql_in_delete_compiler(self, query)
    return patch_sql(sql), args


orig_as_sql_in_delete_compiler = SQLDeleteCompiler._as_sql
SQLDeleteCompiler._as_sql = patched_as_sql_in_delete_compiler
print("patched _as_sql member function in SQLDeleteCompiler class.", file=sys.stderr)


#
# Patch SQLAggregateCompiler Query for aggregate
#


def patched_as_sql_in_aggregate_compiler(self, query):
    sql, args = orig_as_sql_in_aggregate_compiler(self, query)
    return patch_sql(sql), args


orig_as_sql_in_aggregate_compiler = SQLAggregateCompiler.as_sql
SQLAggregateCompiler._as_sql = patched_as_sql_in_aggregate_compiler
print("patched as_sql member function in SQLAggregateCompiler class.", file=sys.stderr)


#
# Make DB_TABLES_MAPPING Global Variable
#


def make_DB_TABLES_MAPPING(sender, connection, **kwargs):
    """
    SQLite 에서의 Multi Database 에서의 SQL JOIN 수행을 위해서, ATTACH 를 통해 db alias 를 지정합니다.
    """

    if "sqlite" in settings.UNIQUE_DB_ENGINE:
        with connection.cursor() as cursor:
            for db_alias, db_settings in settings.DATABASES.items():
                # SQLite 에서의 Multi Database 에서의 SQL JOIN 수행을 위해서
                # ATTACH 를 통해 db alias 를 지정합니다.
                sql = f"""ATTACH DATABASE '{db_settings['NAME']}' AS '{db_alias}'"""
                cursor.execute(sql)


if settings.DB_MULTI_JOIN:
    connection_created.connect(make_DB_TABLES_MAPPING)
