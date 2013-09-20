django-epci
===========

Geographic data (cities and epci boundaries) for France sub-region

Importation from scratch
------------------------

1. Import OSM data

```
osm2pgsql -U <db_user> -d <db_name> nord-pas-de-calais.administrative.osm
```

France sub-regions can be found on http://download.geofabrik.de/europe/france.html
It create 4 tables : planet_osm_line, planet_osm_point, planet_osm_polygon, planet_osm_roads
Only planet_osm_polygon is used (and wrapped by model) and only for City and EPCI importation.

2. Import cities

```
./manage.py import_epci -f communes_EPCI_2013.csv -d 59,62
```

Importation from feature datadump (just Nord-Pas-De-Calais)
--------------------------------------------------------------
```
./manage.py loaddata epci_npdc_2013.json
```