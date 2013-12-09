# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import TerritorialDelimitation, City
from django.contrib.gis.admin.options import OSMGeoAdmin
from mptt.admin import MPTTModelAdmin


admin.site.register(TerritorialDelimitation, MPTTModelAdmin)

class CityAdmin(OSMGeoAdmin):
    map_width = 400
    map_height = 400
    search_fields = ("name", "zipcode", "insee")
    list_display = ('name', "zipcode", "insee", )
    fieldsets = (
        (None, {
            'fields': (('name', 'insee', 'zipcode'),
                       ('delim'),
                       ('geom', 'poly'))
        }),
    )

admin.site.register(City, CityAdmin)