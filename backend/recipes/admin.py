from django.contrib import admin

from .models import *


admin.site.regsiter(User)
admin.site.regsiter(Follow)
admin.site.regsiter(Recipe)
admin.site.regsiter(Tag)
admin.site.regsiter(Favourite)
admin.site.regsiter(Ingredients)
