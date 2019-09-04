from users.models import House
import django_filters
from dal import autocomplete

class HouseFilter(django_filters.FilterSet):
    address = django_filters.CharFilter(field_name='address', lookup_expr='icontains')
    beds = django_filters.AllValuesMultipleFilter()
    baths = django_filters.AllValuesMultipleFilter()
    price__gt = django_filters.NumberFilter(field_name='rent', lookup_expr='gt')
    price__lt = django_filters.NumberFilter(field_name='rent', lookup_expr='lt')
    class Meta:
        model = House
        fields = ['address', 'city', 'beds', 'baths', 'price__gt', 'price__lt']