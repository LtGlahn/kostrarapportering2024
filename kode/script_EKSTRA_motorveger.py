from datetime import datetime 

import geopandas as gpd 
import pandas as pd
import numpy as np
from copy import deepcopy

import STARTHER
import lastnedvegnett  
import skrivdataframe
import nvdbapiv3
import nvdbgeotricks

t0 = datetime.now()

# Teller motorveg av klasse A og motortrafikkveg

# mittfilter = lastnedvegnett.kostraFagdataFilter( mittfilter={} )
mittfilter = { 'tidspunkt': '2024-12-31'}
# mittfilter['adskiltelop'] = 'med,nei'
# mittfilter['sideanlegg'] = 'false'

sok = nvdbapiv3.nvdbFagdata( 595  )
sok.filter( mittfilter )
myGdf = nvdbgeotricks.records2gdf( sok.to_records( ) ) 

myGdf = myGdf[ myGdf['trafikantgruppe'] == 'K']    # Kun kjørende 
myGdf = myGdf[ myGdf['adskilte_lop'] != 'Mot' ]     # Adskilte løp = Med,Nei 
myGdf = myGdf[ ~myGdf['vref'].str.contains( 'SD') ] # Fjerner sideanlegg
myGdf = myGdf[ ~myGdf['vref'].str.contains( 'KD') ] # Fjerner kryssdeler
myGdf = myGdf[ myGdf['typeVeg'] != 'Rampe' ] # Fjerner ramper 

telling = myGdf.groupby( ['fylke', 'Motorvegtype' ]).agg( { 'segmentlengde' : 'sum'} ).astype(int).reset_index()  
telling.rename( columns={ 'segmentlengde' : 'Lengde (m)' }, inplace=True)
lengde = myGdf.groupby( [ 'Motorvegtype' ]).agg( { 'segmentlengde' : 'sum'} ).astype(int).reset_index()
print( "Motorveg i fjor", lengde)

metadata = { 'tidspunkt' : '2024-12-31', 'Kryssdeler' : 'Kryssdeler filtrert vekk', 'Sideanlegg' : 'Sideanlegg filtrert vekk', 'Ramper' : 'Ramper filtrert vekk', 'trafikantgruppe' : 'K', 'datauttak' : '2025-06-01' }

telling = myGdf.groupby( ['fylke', 'Motorvegtype' ]).agg( { 'segmentlengde' : 'sum'} ).astype(int).reset_index()  
telling.rename( columns={ 'segmentlengde' : 'Lengde (m)' }, inplace=True)
skrivdataframe.skrivdf2xlsx( telling, '../kostraleveranse2024/EKSTRARAPPORT motorveger.xlsx', sheet_name='Motorveger', metadata=metadata )


tidsbruk = datetime.now() - t0 

print( "tidsbruk rapporttype motorveg alle vegkategorier", tidsbruk)