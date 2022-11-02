import django_filters

from recipes.models import Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    tag = django_filters.filters.ModelMultipleChoiceFilter(
        field_name='tag__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    author = django_filters.filters.NumberFilter(
        field_name='author__id'
    )

    class Meta:
        model = Recipe
        fields = ('tag', 'author')
