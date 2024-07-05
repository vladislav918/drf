from django_filters import rest_framework as filters
from datetime import date, timedelta


from .models import ReadList


class ReadBookListFilter(filters.FilterSet):
    date_added = filters.DateFilter(lookup_expr='gte')
    genre = filters.CharFilter(field_name='book__genre__title') 

    class Meta:
        model = ReadList
        fields = ['date_added', 'genre']
