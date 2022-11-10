import pdfkit
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import loader
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (CustomUser, Favorite, Follow, Ingredient, Recipe,
                            ShoppingCart, Tag)

from .filters import RecipeFilter, SearchIngredient
from .pagination import PaginateCustom
from .permissions import AuthorOrStaffOrReadOnly, IsAdminOrReadOnly, OnlyAuthor
from .serializers import (FavoriteSerializer, IngredientRecipe,
                          IngredientViewSerializer, RecipeSerializer,
                          ShoppingCartSerializer, SubscribeSerializer,
                          TagSerializer, UserSerializer, WriteRecipeSerializer)

ONE = '1'


class UserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = PaginateCustom

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        author = get_object_or_404(CustomUser, id=id)
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                author, context={'request': request}
            )
            Follow.objects.get_or_create(
                user=request.user, author=author
            )
            return Response(serializer.data)

        if Follow.objects.filter(user=request.user,
                                 author=author).exists():
            Follow.objects.get(user=request.user,
                               author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise ValidationError(
            {'errors': 'Вы не подписаны на пользователя'}
        )

    @action(detail=False,
            methods=['get'],
            permission_classes=[OnlyAuthor])
    def subscriptions(self, request):
        user = CustomUser.objects.filter(following__user=self.request.user)
        page = self.paginate_queryset(user)
        serializer = SubscribeSerializer(
            page, context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    pagination_class = None
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    pagination_class = None
    filter_backends = (SearchIngredient,)
    search_fields = ('^name',)
    serializer_class = IngredientViewSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (AuthorOrStaffOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PaginateCustom

    def get_queryset(self):
        queryset = Recipe.objects.all()
        is_favorite = self.request.query_params.get('is_favorited')
        if is_favorite == ONE:
            queryset = queryset.filter(favorite__user=self.request.user)
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if is_in_shopping_cart == ONE:
            queryset = queryset.filter(shop__user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return RecipeSerializer
        return WriteRecipeSerializer

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if Favorite.objects.filter(
                    user=request.user,
                    recipe=recipe).exists():
                return Response('Нельзя добавлять дважды')
            Favorite.objects.create(
                user=request.user, recipe=recipe)
            serializer = FavoriteSerializer(recipe)
            return Response(serializer.data)

        favorite = Favorite.objects.get(
            user=request.user, recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(
                    user=request.user,
                    recipe=recipe).exists():
                return Response('Нельзя добавлять дважды',
                                status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(
                user=request.user, recipe=recipe)
            serializer = ShoppingCartSerializer(recipe)
            return Response(serializer.data)

        favorite = ShoppingCart.objects.get(
            user=request.user, recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        recipes = Recipe.objects.filter(shop__user=request.user)
        recipe = []
        for i in recipes:
            recipe.append(i.id)
        ing_recipes = {}
        ingredients_recipes = IngredientRecipe.objects.filter(
            recipe__in=recipe)
        for i in ingredients_recipes:
            if not i.ingredient.name in ing_recipes:
                ing_recipes[i.ingredient.name] = [
                    i.ingredient.measurement_unit, i.amount]
            else:
                amount = ing_recipes.get(i.ingredient.name)
                new_amount = amount[1] + i.amount
                ing_recipes[i.ingredient.name] = [
                    i.ingredient.measurement_unit, new_amount]
        template = loader.get_template('text.html')
        context = {
            'ing_recipes': ing_recipes
        }
        html = template.render(context, request)
        dirr = pdfkit.from_string(html, False)
        response = HttpResponse(dirr, content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="Список Покупок.pdf"')
        return response
