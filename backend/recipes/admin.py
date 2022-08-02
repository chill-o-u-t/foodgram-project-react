from django.contrib import admin

from .models import *


admin.site.register(User)
admin.site.register(Follow)
admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(Favourite)
admin.site.register(Ingredients)
