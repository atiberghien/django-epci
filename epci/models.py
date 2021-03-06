# -*- coding: utf-8 -*- 
from django.db import connection 
from django.contrib.gis.db import models
from django.utils.translation import gettext as _
from mptt.models import MPTTModel, TreeForeignKey
from geolocation_helper.models import GeoLocatedModel
from django.contrib.gis.geos.geometry import GEOSGeometry

class TerritorialDelimitation(MPTTModel):
    DELIM_TYPES = (
        ('REG', _("Région")),
        ('DEP', _("Département")),
        ('CC', _("Communauté de communes")),
        ('CU', _("Communauté urbaine")),
        ('CA', _("Communauté d'agglomération")),
    )
    name = models.CharField(max_length=150, verbose_name=_("nom de la délimitation territoriale"), blank=True, null=True)
    code = models.CharField(max_length=15, verbose_name=_("code (insee)"))
    type = models.CharField(max_length=3, choices=DELIM_TYPES)
    
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    
    poly = models.GeometryField(blank=True, null=True)
    objects = models.GeoManager()
    
    def __unicode__(self):
        if self.name and self.type in self.name:
            return self.name.replace(self.type, self.get_type_display())
        return "%s %s" % (self.get_type_display(), self.name)
    
    def get_boundary(self, force=False):
        if force or not self.poly:
            cursor = connection.cursor()
            cursor.execute("SELECT ST_Collect(ARRAY(SELECT poly FROM epci_city where delim_id = %s and poly IS NOT NULL));", [self.id])
            self.poly = GEOSGeometry(cursor.fetchone()[0]).cascaded_union
            self.save()
        return self.poly
    
    class MPTTMeta:
        order_insertion_by = ['code']
    
    class Meta:
        verbose_name = _("délimitation territoriale")


class City(GeoLocatedModel):
    name = models.CharField(max_length=150, verbose_name=_("nom de la commune"))
    zipcode = models.CharField(max_length=5, verbose_name=_("code postal"), blank=True, null=True)
    insee = models.CharField(max_length=5, verbose_name=_("code insee"))
    
    delim = models.ForeignKey(TerritorialDelimitation, null=True)
    
    poly = models.PolygonField(blank=True, null=True)
    objects = models.GeoManager()
    
    @property
    def point(self):
        return self.geom
    
    def get_location_as_string(self): #from GeoLocatedModel
        return self.name
    
    def __unicode__(self):
        return self.get_location_as_string()
    
    class Meta:
        ordering = ['zipcode']
        verbose_name = _("ville")    

"""
#XXX: Uncomment for from scratch importation 

class PlanetOsmPolygon(models.Model):
    
#     This model wraps the legacy planet_osm_polygon containing city boundaries (admin_level=8)
#     It contains only a subset of attributes.
#     It is not used in application, just for importation
    
    osm_id = models.AutoField(primary_key=True)
    addr_housename = models.TextField(db_column='addr:housename', blank=True) # Field renamed to remove unsuitable characters.
    addr_housenumber = models.TextField(db_column='addr:housenumber', blank=True) # Field renamed to remove unsuitable characters.
    addr_interpolation = models.TextField(db_column='addr:interpolation', blank=True) # Field renamed to remove unsuitable characters.
    admin_level = models.TextField(blank=True)
    name = models.TextField(blank=True)
    place = models.TextField(blank=True)
    ref = models.TextField(blank=True)
    surface = models.TextField(blank=True)
    way = models.GeometryField(srid=900913, null=True, blank=True)
    objects = models.GeoManager()
    class Meta:
        db_table = 'planet_osm_polygon'
"""