from core.utils import get_client_ip
from django.db import models
from flatten_dict import flatten, reducer
from rest_framework import fields, serializers
from rest_framework.request import Request
from .rules import get_rules


class CoreHyperlinkedSerializer(serializers.HyperlinkedModelSerializer):
    url_field_name = "permalink"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        label_fields = getattr(self.Meta, "labels", {})

        for field, label in label_fields.items():
            self.fields[field].label = label

    # Override
    def to_representation(self, instance):
        """
        serializer를 flatten 처리 후 리턴합니다.
        """
        return_dict = super().to_representation(instance)

        return flatten(return_dict, reducer=reducer.make_reducer(delimiter="__"))

    @classmethod
    def with_permalink(cls, detail_view_name):
        """
        하나의 Model이 다수의 Serializer/ViewSet에 의해 참조가 될 수 있습니다.
        permalink 생성에 활용이 될 Viewset의 detail name을 지정해봅니다.

        :param detail_view_name:
        :return:
        """

        class CustomSerializer(cls):
            def build_url_field(self, field_name, model_class):
                field_class = self.serializer_url_field
                field_kwargs = {"view_name": detail_view_name}
                return field_class, field_kwargs

        return CustomSerializer

    # Override
    def save(self, *args, **kwargs):
        """
        Serializer를 통한 저장시 시스템 필드 정보를 request 객체로부터 받아와 저장토록 합니다.
        """
        request: Request = self.context.get("request", None)
        if request is not None:
            ip = get_client_ip(request)
            ip_field_name = (
                "insert_user_ip" if self.instance is None else "update_user_ip"
            )

            user_id = request.user.pk
            user_id_field_name = (
                "insert_user_id" if self.instance is None else "update_user_id"
            )

            # 관련 모델에 ip_field_name 필드가 있을 때에만 ip_field_name 필드에 대한 DB 저장을 시도합니다.
            field_names = {field.name for field in self.Meta.model._meta.get_fields()}
            if ip_field_name in field_names:
                kwargs.update({ip_field_name: ip})
            if user_id_field_name in field_names:
                kwargs.update({user_id_field_name: user_id})

        return super().save(*args, **kwargs)


def get_columns_from_serializer(serializer):
    """
    Front단에서 체킹할 Validate, Label 등의 메타 정보를 생성합니다.
    """

    meta_cls = serializer.Meta
    model_fields_dict = serializer.fields
    # model_fields_dict = {model_field.name: model_field for model_field in meta_fields}

    columns = []
    for serializer_field_name, serializer_field in serializer.fields.items():
        model_field = model_fields_dict.get(serializer_field_name)

        if isinstance(model_field, models.TextField):
            field_type = "textarea"
        elif isinstance(serializer_field, (fields.IntegerField,)):
            field_type = "integer"
        elif isinstance(serializer_field, (fields.FloatField,)):
            field_type = "float"
        elif isinstance(serializer_field, (fields.DecimalField,)):
            field_type = "decimal"
        elif isinstance(serializer_field, (fields.IPAddressField,)):
            field_type = "ip"
        elif isinstance(serializer_field, (fields.CharField,)):
            field_type = "string"
        elif isinstance(serializer_field, (fields.EmailField,)):
            field_type = "email"
        elif isinstance(serializer_field, (fields.URLField,)):
            field_type = "url"
        elif isinstance(serializer_field, (fields.BooleanField,)):
            field_type = "boolean"
        elif isinstance(serializer_field, (fields.DateField,)):
            field_type = "date"
        elif isinstance(serializer_field, (fields.DateTimeField,)):
            field_type = "datetime"
        elif isinstance(serializer_field, (fields.FileField,)):
            field_type = "file"
        elif isinstance(serializer_field, (fields.SerializerMethodField,)):
            if serializer_field.method_name is None:
                method_name = f"get_{serializer_field_name}"
            else:
                method_name = serializer_field.method_name

            method = getattr(serializer, method_name)
            field_type = getattr(method, "field_type", None)
        elif serializer_field_name != "permalink" and isinstance(
            serializer_field, serializers.HyperlinkedRelatedField
        ):
            field_type = "foreign_key"
        else:
            field_type = None

        # label 우선순위 : SerializerField Label, ModelField verbose_name
        label_in_model = None
        if hasattr(meta_cls, "model") and isinstance(
            getattr(meta_cls.model, serializer_field_name, None), property
        ):
            try:
                label_in_model = getattr(
                    meta_cls.model, serializer_field_name
                ).fget.short_description
            except AttributeError:
                pass

        column = {
            "name": serializer_field_name,
            "label": serializer_field_name or label_in_model,
            "rules": get_rules(serializer_field, field_type),
        }

        columns.append(column)

    return columns
