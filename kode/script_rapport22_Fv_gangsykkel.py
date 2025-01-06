from datetime import datetime 
import json 

import geopandas as gpd 
from shapely.ops import transform 

import STARTHER
import lastnedvegnett  
import skrivdataframe
import nvdbgeotricks

t0 = datetime.now()

vegobjektfilter = lastnedvegnett.filtersjekk(  )
vegobjektfilter['tidspunkt'] = '2024-12-31'

mittfilter = { }
mittfilter['vegsystemreferanse'] = 'Fv'
mittfilter['trafikantgruppe'] = 'G'
mittfilter['tidspunkt'] = vegobjektfilter['tidspunkt']
mittfilter['srid'] = 4326

myGdf = nvdbgeotricks.vegnett2gdf( mittfilter=mittfilter )

# myGdf.to_file( 'kostraleveranser.gpkg', layer='sykkelfelt', driver='GPKG')
# myGdf  = gpd.read_file( 'kostraleveranser.gpkg', layer='sykkelfelt')

# Må bytte om X og Y (lat, lon) => (lon, lat)
# https://gis.stackexchange.com/questions/291247/interchange-y-x-to-x-y-with-geopandas-python-or-qgis/312082#312082 
# med min tilføyelse om z=None 
myGdf['geometry'] = myGdf['geometry'].apply(lambda mygeom: transform(lambda x, y,z=None: (y, x, z), mygeom))

jsonfil = '../kostraleveranse2024/Kostra22  - sykkelveger_fylkesveg.geojson'
with open( jsonfil, 'w'  ) as f: 
    f.write( myGdf.to_json())



tidsbruk = datetime.now() - t0 
print( "Tidsbruk rapport 22:", tidsbruk ) # Ca 84 sekunder

print( jsonfil, 'skal zippes' )
