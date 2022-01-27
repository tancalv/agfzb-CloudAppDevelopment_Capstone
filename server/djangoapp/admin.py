from django.contrib import admin
# from .models import related models
from .models import CarMake, CarModel

# Register your models here.

# CarModelInline class
class CarModelInline(admin.StackedInline):
    model = CarModel
    extra = 5

# CarModelAdmin class
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('dealer_id', 'name', 'types', 'year')

# CarMakeAdmin class with CarModelInline

class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInline]
    list_display = ('name', 'description')
    list_filter = ['description']
    search_fields = ['name', 'description']

 
# Register models here
admin.site.register(CarModel, CarModelAdmin)
admin.site.register(CarMake, CarMakeAdmin)