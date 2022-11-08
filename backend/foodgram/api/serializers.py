import webcolors
from django.db.models import F
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (CustomUser, Favorite, Follow, Ingredient,
                            IngredientRecipe, Recipe, ShoppingCart, Tag,
                            TagRecipe)


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            if Follow.objects.filter(
                    user=user,
                    author=CustomUser.objects.get(id=obj.id)).exists():
                return True
            return False
        return False


class CustomUserSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')


class RecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(UserSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = RecipesSerializer(many=True, read_only=True)

    class Meta(UserSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientRecipe
        fields = ['id', 'amount']

    def validate_amount(self, data):
        if int(data) < 1:
            raise serializers.ValidationError({
                'ingredients': (
                    'Количество должно быть больше, либо равно 1'
                ),
                'msg': data
            })
        return data

    def create(self, validated_data):
        return IngredientRecipe.objects.create(
            ingredient=validated_data.get('id'),
            amount=validated_data.get('amount')
        )


class IngredientViewSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    author = CustomUserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name',
                  'image', 'text', 'is_favorited', 'is_in_shopping_cart',
                  'name', 'cooking_time')
        read_only_fields = ('author',)

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id', 'name',
            'measurement_unit',
            amount=F('ingredient_recipes__amount')
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            if Favorite.objects.filter(
                    user=user,
                    recipe=Recipe.objects.get(id=obj.id)).exists():
                return True
            return False
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            if ShoppingCart.objects.filter(
                    user=user,
                    recipe=Recipe.objects.get(id=obj.id)).exists():
                return True
            return False
        return False


class WriteRecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientSerializer(many=True)
    tags = serializers.SlugRelatedField(many=True,
                                        slug_field='id',
                                        queryset=Tag.objects.all()
                                        )

    def validate_ingredients(self, value):
        ingredients = value
        ingredients_list = []
        for item in ingredients:
            ingredient = item["ingredient"].id
            if ingredient in ingredients_list:
                raise serializers.ValidationError({
                    'ingredients': 'Ингредиенты не могут повторяться!'
                })
            ingredients_list.append(ingredient)
        return value

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        count = 0
        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(
                id=self.context.get('request').data.get(
                    'ingredients')[count].get('id'))

            IngredientRecipe.objects.create(
                ingredient=current_ingredient,
                recipe=recipe,
                amount=self.context.get('request').data.get(
                    'ingredients')[count].get('amount'))
            count += 1

        for tag in tags:
            current_tag = Tag.objects.get(id=tag.id)
            TagRecipe.objects.create(tags=current_tag, recipe=recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get(
            'image', instance.image
        )
        instance.name = validated_data.get(
            'name', instance.name
        )
        instance.text = validated_data.get(
            'text', instance.text
        )
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )

        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags', None)
            lst = []
            for tag in tags_data:
                current_tag = Tag.objects.get(id=tag.id)
                lst.append(current_tag)
            instance.tags.set(lst)

        if 'ingredients' in validated_data:
            ingredients_data = validated_data.pop('ingredients', None)
            lst = []
            count = 0
            for ingredient in ingredients_data:
                id_ingredients = self.context['request'].data.get(
                    'ingredients')[count].get('id')
                amount = self.context['request'].data.get(
                    'ingredients')[count].get('amount')
                current_ingredient = Ingredient.objects.get(id=id_ingredients)
                if IngredientRecipe.objects.filter(
                    recipe=instance,
                    ingredient=current_ingredient
                ).exists():
                    IngredientRecipe.objects.filter(
                        recipe=instance,
                        ingredient=current_ingredient
                    ).update(amount=amount)
                else:
                    IngredientRecipe.objects.create(
                        recipe=instance,
                        ingredient=current_ingredient,
                        amount=amount
                    )
                count += 1
                lst.append(current_ingredient)
            instance.ingredients.set(lst)

        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance,
                                context={
                                    'request': self.context.get('request'),
                                }
                                ).data

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('author',)


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
