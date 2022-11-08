import django_filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class SearchIngredient(SearchFilter):
    search_param = 'name'


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    author = django_filters.filters.NumberFilter(
        field_name='author__id'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')
