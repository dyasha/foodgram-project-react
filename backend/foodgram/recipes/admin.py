from django.contrib import admin

from .models import (CustomUser, Favorite, Follow, Ingredient,
                     IngredientRecipe, Recipe, ShoppingCart, Tag, TagRecipe)


class MinValidatedInlineMixin:
    validate_min = True

    def get_formset(self, *args, **kwargs):
        return super().get_formset(
            validate_min=self.validate_min, *args, **kwargs
        )


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email')
    list_filter = ('email', 'username')


class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')


class IngredientInline(MinValidatedInlineMixin, admin.StackedInline):
    model = IngredientRecipe
    extra = 0
    min_num = 1
    validate_min = True


class TagRecipeInline(admin.StackedInline):
    model = TagRecipe
    extra = 0
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author')
    list_filter = ('author', 'name', 'tags')
    inlines = (TagRecipeInline, IngredientInline)


class IngridientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author', 'author_id')


class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredient', 'ingredient_id',
                    'recipe', 'recipe_id', 'amount')


class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'tags', 'recipe')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngridientAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(TagRecipe, TagRecipeAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(Favorite, FavoritesAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
