from django.contrib import admin
from .models import Pictures, DBTest
# Register your models here.

class PicturesAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)

admin.site.register(Pictures, PicturesAdmin)