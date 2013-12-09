# -*- coding: utf-8 -*- 

from django.core.management.base import BaseCommand
from django.contrib.gis.gdal import SpatialReference, CoordTransform
from django.contrib.gis.geos.point import Point
from optparse import make_option
from geopy import geocoders

from epci.models import TerritorialDelimitation, City, PlanetOsmPolygon

import csv
import json
import urllib2
import urllib
import sys

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":True,   "y":True,  "ye":True,
             "no":False,     "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-f", 
                    "--file", 
                    dest="filename",
                    help="import FILE", 
                    metavar="FILE"),
        make_option("-d", 
                    "--deps", 
                    dest="deps",
                    help="filter département", 
                    metavar="DEP"),
        )
    
    def __init__(self):
        BaseCommand.__init__(self)
        self.found = 0
        self.no_match = 0
        from_coord = SpatialReference(900913)
        to_coord = SpatialReference(4326)
        self.trans = CoordTransform(from_coord, to_coord)
        self.rtrans = CoordTransform(to_coord, from_coord)
        
    def re_geocode_city(self, city, boundary):
        center = boundary.way.centroid
        center.transform(self.trans)
        city.geom = center
        city.save()
                
    def find_city_geometry(self, city):
        boundary = None
        try:
            boundary = PlanetOsmPolygon.objects.filter(admin_level=8).get(way__contains=city.geom,
                                                                          name__iexact=city.name)
            self.found += 1
        except PlanetOsmPolygon.DoesNotExist:
            try:
                boundary = PlanetOsmPolygon.objects.filter(admin_level=8).get(way__contains=city.geom)
                if not query_yes_no("Import %s <=> %s" % (city.name, boundary.name), default="no"):
                    boundary = None
                    self.no_match += 1
                else:
                    boundary.name = city.name
                    boundary.save()
                    self.found += 1
            except PlanetOsmPolygon.DoesNotExist:
                try:
                    boundary = PlanetOsmPolygon.objects.filter(admin_level=8).get(name__iexact=city.name)
                    self.re_geocode_city(city, boundary)
                    self.find_city_geometry(city)
                except:
                    qs = PlanetOsmPolygon.objects.filter(admin_level=8, name__iexact=city.name)
                    if qs.count():
                        min_dist = sys.float_info.max
                        nearest = None
                        for polygon in qs:
                            dist = polygon.way.distance(city.geom)
                            if dist < min_dist:
                                min_dist = dist
                                nearest = polygon
                        self.re_geocode_city(city, nearest)
                        self.find_city_geometry(city)
                    else:
                        self.no_match += 1
            except PlanetOsmPolygon.MultipleObjectsReturned:
                print "DUPLICATES geom IN OSM DB"
                self.no_match += 1
        except PlanetOsmPolygon.MultipleObjectsReturned:
            print "DUPLICATES (name, geom) IN OSM DB"
            self.no_match += 1
        if boundary:
            city.poly = boundary.way
            city.save()
            
    def handle(self, *args, **options):
            """
            Code Postal    
            nom_comunes    
            dep_epci    
            siren_epci    
            Nom intercommunalité    
            Type d'intercommunalité
            """
            with open(options['filename'], 'rb') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter='|', quotechar='"')
                csv_reader.next()
                for row in csv_reader:
                    city_insee, city_name, dep, epci_insee, epci_name, epci_type = row
                    
                    deps = options['deps'].split(',')
                    if dep in deps:
                        
                        try:
                            dep_obj = TerritorialDelimitation.objects.get(code=dep, type="DEP")
                        except TerritorialDelimitation.DoesNotExist:
                            dep_obj = TerritorialDelimitation.objects.create(code=dep, type="DEP")
                       
                        epci, nop = TerritorialDelimitation.objects.get_or_create(code=epci_insee, 
                                                                                  parent=dep_obj)
                        epci.name = epci_name
                        epci.type = epci_type
                        epci.save()
                           
                        if len(city_insee) == 4:
                            city_insee = "0%s" % city_insee
                           
                        city, nop = City.objects.get_or_create(insee=city_insee,
                                                               delim=epci,
                                                               name=city_name)
                           
                        g = geocoders.GoogleV3()
                        if not city.geom:
                            try:
                                place, (lat, lng) = g.geocode("%s, %s %s" % (city.name, dep, "france"))
                                city.geom = Point(lng, lat)
                                city.save()
                            except:
                                print "NO POINT: %s" % city_name
                         
                        if city.geom and not city.poly:
                            self.find_city_geometry(city)
