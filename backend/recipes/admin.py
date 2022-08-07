from django.contrib import admin

from .models import *


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')


admin.site.register(User)
admin.site.register(Follow)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Favourite)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Cart)
