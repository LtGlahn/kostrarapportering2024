from datetime import datetime 

import geopandas as gpd 
import pandas as pd
import numpy as np

import STARTHER
import lastnedvegnett  
import skrivdataframe
import nvdbapiv3

t0 = datetime.now()

mittfilter = lastnedvegnett.filtersjekk(  )
mittfilter['vegsystemreferanse'] = 'Fv'
junk = mittfilter.pop( 'historisk', None)

sok = nvdbapiv3.nvdbFagdata( 595 )
sok.filter( mittfilter )
data = sok.to_records( )
mydf = pd.DataFrame( data )

lengde = mydf.groupby( ['fylke', 'vegkategori', 'nummer' ]).agg( {'segmentlengde' : 'sum' } ).reset_index()
lengde['Veg'] = 'FV' + lengde['nummer'].astype(str)
lengde['Lengde (m)'] = lengde['segmentlengde']
lengde = lengde[[ 'fylke', 'Veg', 'Lengde (m)']]

skrivdataframe.skrivdf2xlsx( lengde, '../kostraleveranse2024/Kostra 02 - Fylkesveg med motorveg og motortrafikkveg.xlsx', sheet_name='Fv med motor(trafikk)veg', metadata=mittfilter)

tidsbruk = datetime.now() - t0 
print( "Tisdbruk rapporttype 2", tidsbruk)