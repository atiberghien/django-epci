# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import EPCI, City
from django.contrib.gis.admin.options import OSMGeoAdmin


class EPCIAdmin(OSMGeoAdmin):
    map_width = 400
    map_height = 400
    list_filter = ('type', )
    model = EPCI


class CityAdmin(OSMGeoAdmin):
    map_width = 400
    map_height = 400
    search_fields = ("name", "zipcode", "insee")
    list_display = ('name', "zipcode", "insee", 'epci', )
    list_editable = ('epci', )
    fieldsets = (
        (None, {
            'fields': (('name', 'insee', 'zipcode'),
                       ('epci'),
                       ('geom', 'poly'))
        }),
    )

admin.site.register(EPCI, EPCIAdmin)
admin.site.register(City, CityAdmin)