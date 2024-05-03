from rest_framework.filters import BaseFilterBackend

class CustomFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        airline = request.query_pararms.get('airline', None)
        if airline:
            queryset = [item for item in queryset if item['airline']==airline]
        return queryset
