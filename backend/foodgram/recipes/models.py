from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

ADMIN = 'admin'
USER = 'user'


class CustomUser(AbstractUser):
    USER_ROLES = (
        (ADMIN, _('Administrator')),
        (USER, _('User')),
    )
    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    role = models.CharField(
        max_length=15,
        choices=USER_ROLES,
        default=USER,)

    class Meta:
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    @property
    def is_admin(self):
        return self.role == ADMIN

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             null=True
                             )
    author = models.ForeignKey(CustomUser,
                               on_delete=models.CASCADE,
                               related_name='following',
                               null=True
                               )

    class Meta:
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_follow_object'),
            models.CheckConstraint(
                name="prevent_self_follow",
                check=~models.Q(user=models.F('author')),
            ),
        ]

        def __str__(self):
            return f'{self.user.username} - {self.author.username}'


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ('id',)
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag,
                                  through='TagRecipe',
                                  )
    author = models.ForeignKey(CustomUser,
                               related_name='recipes',
                               on_delete=models.CASCADE
                               )
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientRecipe',
                                         related_name='recipes'
                                         )
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='recipes/images/%Y/%m/%d/')
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)])
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    tags = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tags} {self.recipe}'

    class Meta:
        verbose_name_plural = 'Тег с рецептом'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        default=1)

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'

    class Meta:
        default_related_name = 'ingredient_recipes'
        verbose_name_plural = 'Ингредиент с рецептом'
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredient', 'amount'],
                                    name='unique_ingredient_recipe_object'),
        ]


class Favorite(models.Model):
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE,
                             related_name='user',
                             null=True
                             )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='favorite',
                               null=True
                               )

    class Meta:
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favorite_object'),
        ]

        def __str__(self):
            return self.user.username


class ShoppingCart(models.Model):
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE,
                             related_name='usershop',
                             )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='shop',
                               )

    class Meta:
        verbose_name_plural = 'Корзина'
