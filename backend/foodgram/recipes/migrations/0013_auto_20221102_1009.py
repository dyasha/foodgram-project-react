# Generated by Django 3.2 on 2022-11-02 10:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0012_auto_20221027_1306'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-pub_date',), 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='is_favorited',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='is_in_shopping_cart',
        ),
    ]
