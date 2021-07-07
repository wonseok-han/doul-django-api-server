from django.db import transaction
from rest_framework.response import Response
from .serializers import get_columns_from_serializer
from rest_framework.decorators import action


class CoreMixinViewSet:
    """
    CoreHyperlinkedSerializer를 수용하는 Mixin ViewSet을 생성합니다.
    """

    def dispatch(self, request, *args, **kwargs):
        # batch를 통한 요청
        if getattr(request, "_batch_request", False):
            return super().dispatch(request, *args, **kwargs)

        # 일반적인 요청 : ATOMIC_REQUESTS를 설정한 효과
        with transaction.atomic():
            return super().dispatch(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        데이터 리스트를 한번 dict로 한 번 감싼 후 제공합니다.
        """
        if "queryset" in kwargs:
            base_queryset = kwargs["queryset"]
        else:
            base_queryset = self.get_queryset()

        queryset = self.filter_queryset(base_queryset)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)

            list_data = serializer.data

            # FIXME: 조회시 meta colums가 필요할까?
            # columns = get_columns_from_serializer(serializer)

            # FIXME: 테스트 후 필요한지 추후 결정
            # list_data에서 조작된 FK URL 문자열을 회복
            cleaned_list_data = [self.clean_fk_url(row_data) for row_data in list_data]

            response_dict = dict(
                count=self.paginator.page.paginator.count,
                results=cleaned_list_data,
            )

            return Response(response_dict)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        context["kwargs"] = self.kwargs

        return context

    def get_serializer_class(self):
        return self.serializer_class

    @action(detail=False, methods=["GET"])
    def meta(self, request, *args, **kwargs):
        """
        Front단에서 사용할 Validation 체킹를 위해 meta url을 제공합니다.
        """
        context = self.get_serializer_context()

        serializer = self.get_serializer_class()(context=dict(context))

        return Response({"meta": get_columns_from_serializer(serializer)})
