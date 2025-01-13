"""
Fikser grensejustering 1.1.2025, som får tilbakevirkende kraft i NVDB og derfor påvirker datauttaket vårt. 
Mer presis så er det en liten flk av Risør som ble overført til Tvedestrand, ref https://lovdata.no/dokument/LF/forskrift/2023-06-09-837
"""


import STARTHER
import nvdbapiv3
import pandas as pd
import geopandas as gpd
from shapely import wkt
from datetime import datetime


if __name__ == '__main__': 
    t0 = datetime.now()
    sok = nvdbapiv3.nvdbFagdata( 946)
    sok.filter( {'egenskap' : "11770='Tvedestrand'"}) 
    tvedestrand2025 = sok.nesteForekomst()
    # Konverter fra multipolygon til polygon 
    flateTvedestrand2025 = list( wkt.loads( [ x for x in tvedestrand2025['egenskaper']  if x['navn'] == 'Geometri, flate'][0]['verdi'] ) )[0]

    # Henter ALLE historiske kommuner fra NVDB, det er noe tull med indekseringen og ID på egenskapsverdier som vi kan bruke i filteret
    sok = nvdbapiv3.nvdbFagdata( 536 )

    # komm = sok.nesteForekomst()
    for (ii, komm) in enumerate(sok): 

        navn =  [ x for x in komm['egenskaper'] if x['navn'] == 'Kommunenavn'  ][0]
        if 'Risør' in navn['verdi']: 
            print( f"Fant {navn['verdi']} nvdb ID {komm['id']}\n{komm['href']}")
            flateRisør2024 = wkt.loads( [ x for x in komm['egenskaper']  if x['navn'] == 'Geometri, flate'][0]['verdi'] )

        if ii == 1 or ii % 20 == 0:
            print( f"\tHar sjekket {ii} kommuner")


    # Intersection mellom disse flatene er ganske grisete pga dårlig geometri. Må filtrere vekk litt støy for å finne 
    # det vi vil ha
    int = flateRisør2024.intersection( flateTvedestrand2025 )
    interGdf = gpd.GeoDataFrame( {'navn' : 'grensejustering', 'geometry' : int } )

    # En del degenerte tilfeller der vi har fått linjegeometri
    interGdf['geom_type'] = interGdf['geometry'].apply( lambda x : x.geom_type )
    interGdf = interGdf[ interGdf['geom_type'] == 'Polygon' ].copy()

    # Har mange smale geometrier, den vi vil ha er 100x større enn nest største
    interGdf['areal'] = interGdf['geometry'].apply( lambda x : x.area )
    grensejustertAreal = interGdf.sort_values( by='areal', ascending=False ).iloc[0]['geometry']
    justertGdf = gpd.GeoDataFrame( [{ 'navn' : 'justert areal', 'beskrivelse' : 'Areal fra Gamle Risør til nye Tvedestrand', 'geometry' : grensejustertAreal }], crs=5973 )

    # Henter vegnettsdata som er lastet ned 6.1.2025 
    myGdf = gpd.read_file( 'vegnetthelelandet.gpkg' )
    # Lettvint index for å kryssreferere med resultatet av geografiske søk 
    myGdf['myIndex'] = myGdf.index
    # Finner de vegsemgentene som er helt innafor området
    innafor = myGdf[ myGdf.within( grensejustertAreal ) ]
    # Finner de vegsegmentene som krysser områdegrensen
    krysser = myGdf[ myGdf.crosses( grensejustertAreal ) ]

    # Endrer kommunenummer på de vegsegmentene som er helt innafor området
    # 4201 = Risør 
    myGdf.loc[ myGdf['myIndex'].isin( innafor['myIndex'] ), 'kommune'] = 4201 

    # Lagrer til fil
    # myGdf.to_file( 'vegnetthelelandet_justert.gpkg', driver='GPKG', layer='norge' )

    # # Lagrer for inspeksjon
    # gpkgfil =  'kommunejustering2025.gpkg'
    # justertGdf.to_file( gpkgfil, driver='GPKG', layer='grensejustertAreal'  )
    # myDf = pd.DataFrame( [ {'navn' : 'Tvedestrand 2025', 'geometry' : flateTvedestrand2025},
    #                 {'navn' : 'Risør 2024', 'geometry' : flateRisør2024 }  ]  )
    # kommuneFlater = gpd.GeoDataFrame( myDf, geometry='geometry', crs=5973 )
    # kommuneFlater.to_file( gpkgfil, driver='GPKG', layer='kommuneflater' )
    # innafor.to_file( gpkgfil, driver='GPKG', layer='TreffHeltInnafor')
    # krysser.to_file( gpkgfil, driver='GPKG', layer='TreffKrysser')

    print( f"Tidsbruk: {datetime.now()-t0}")

