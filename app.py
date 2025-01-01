import streamlit as st
import sqlite3
import pandas as pd
import json
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium
from pyproj import CRS
from folium import MacroElement
from jinja2 import Template

db_path = "sein_konfig.gpkg"
#map_url = "https://geo.so.ch/map/?t=default&bl=hintergrundkarte_sw&c=2618500,1238000&s=188976&l="
map_url = "https://geo.so.ch/map/?t=default&bl=hintergrundkarte_sw&l="


proj4leaflet_js = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/proj4js/2.6.2/proj4.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/proj4leaflet/1.0.2/proj4leaflet.js"></script>
"""

epsg2056_js = """
<script>
    L.CRS.EPSG2056 = new L.Proj.CRS('EPSG:2056', 
        '+proj=somerc +lat_0=46.95240555555556 +lon_0=7.439583333333333 ' +
        '+k_0=1 +x_0=2600000 +y_0=1200000 +ellps=bessel ' +
        '+towgs84=674.374,15.056,405.346,0,0,0,0 +units=m +no_defs', {
            resolutions: [
                4000, 3750, 3500, 3250, 3000, 2750, 2500, 2250, 2000, 1750,
                1500, 1250, 1000, 750, 650, 500, 250, 100, 50, 20, 10, 5, 2.5, 2, 1.5, 1, 0.5
            ],
            origin: [2420000, 1350000],
            bounds: L.bounds([2420000, 1030000], [2900000, 1350000])
        }
    );
</script>
"""

my_js = '''
console.log('here add your code javascript')
'''


def get_gemeinden():
    with sqlite3.connect(db_path) as conn:
        query = "SELECT aname FROM sein_gemeinde ORDER BY aname"
        df = pd.read_sql_query(query, conn)
    return df["aname"].tolist()

def get_details_for_gemeinde(gemeinde_name):
    with sqlite3.connect(db_path) as conn:
        query = f"""
SELECT 
    gr.aname AS gruppe,
    JSON_GROUP_ARRAY(
        JSON_OBJECT(
            'thema', t.aname,
            'layer_id', t.karte,
            'ist_betroffen', tg.ist_betroffen,
            'gemeinde', g.aname,
            'bfsnr', g.bfsnr
        )
    ) AS details
FROM 
    sein_gemeinde AS g 
    LEFT JOIN sein_thema_gemeinde AS tg 
    ON g.T_Id = tg.gemeinde_r 
    LEFT JOIN sein_thema AS t 
    ON t.T_Id = tg.thema_r 
    LEFT JOIN sein_gruppe AS gr 
    ON gr.T_Id = t.gruppe_r 
WHERE 
    g.aname = ?
GROUP BY 
    gr.aname
        """
        df = pd.read_sql_query(query, conn, params=(gemeinde_name,))
    return df

def create_map(center, zoom):
    # m = folium.Map(
    #     location=[47.208703, 7.536123],  # Center of Switzerland
    #     zoom_start=10,
    #     crs="EPSG2056",
    #     tiles="https://geo.so.ch/api/wmts/1.0.0/ch.so.agi.hintergrundkarte_sw/default/2056/{z}/{x}/{y}.png",
    #     attr='Map data: &copy; <a href="https://www.swisstopo.ch" target="_blank" rel="noopener noreferrer">swisstopo</a>, <a href="https://www.housing-stat.ch/" target="_blank" rel="noopener noreferrer">BFS</a>'
    # )

    # m.get_root().html.add_child(folium.Element(epsg2056_js))


    # Add a custom tile layer (e.g., using Swisstopo tiles)
    # folium.TileLayer(
    #     tiles="https://geo.so.ch/api/wmts/1.0.0/ch.so.agi.hintergrundkarte_sw/default/2056/{z}/{x}/{y}.png",
    #     attr="© Swisstopo",
    #     name="Swisstopo Map",
    #     overlay=False,
    # ).add_to(m)
    
    #swisstopo_tiles = "https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe/default/current/2056/{z}/{x}/{y}.jpeg"
    swisstopo_tiles = "https://geo.so.ch/api/wmts/1.0.0/ch.so.agi.hintergrundkarte_sw/default/2056/{z}/{x}/{y}.png"
    swisstopo_attr = "© Swisstopo"

    #Create a map object
    m = folium.Map(
        location=[47.208703, 7.536123], 
        zoom_start=2,
        tiles=None,
        #crs='EPSG2056'
    )

    m.get_root().script.add_child(folium.Element(my_js))


    m.get_root().add_child(folium.Element(proj4leaflet_js))
    m.get_root().html.add_child(folium.JavascriptLink('https://cdnjs.cloudflare.com/ajax/libs/proj4js/2.6.2/proj4.js'))
    m.get_root().script.add_child(folium.Element(epsg2056_js))
    m.get_root().add_child(folium.Element(epsg2056_js))
    #m.get_root().add_child(CustomJs(epsg2056_js))


    # Add the Swisstopo tile layer
    folium.TileLayer(
        tiles=swisstopo_tiles,
        attr=swisstopo_attr,
        name="Swisstopo Map",
        overlay=False
    ).add_to(m)

    # Inject custom CRS definition (EPSG:2056)
    #m.get_root().html.add_child(folium.Element(swiss_js))

    # swiss_crs = CRS.from_epsg(2056)
    # m = folium.Map(
    #     location=[46.9480, 7.4474],  # Bern coordinates
    #     crs=folium.TileLayer.EPSG2056,
    #     zoom_start=12
    # )

    # # Add a custom tile layer that supports EPSG:2056
    # folium.TileLayer(
    #     tiles='https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe/default/current/2056/{z}/{x}/{y}.jpeg',
    #     attr='&copy; swisstopo',
    #     name='SwissTopo',
    # ).add_to(m)

    return m



# Streamlit app
st.title("SEin-App")

# Create a placeholder for the map
map_placeholder = st.empty()


m = folium.Map(
    location=[47.208703, 7.536123], 
    zoom_start=2,
    tiles=None,
    #crs='EPSG2056'
)
my_js = '''
console.log('here add your code javascript')
'''

m.get_root().script.add_child(folium.Element(my_js))
m.get_root().script.add_child(folium.Element("alert('Hallo')"))

m.add_child(folium.LatLngPopup())

output = st_folium(m, width=700, height=500)



try:
    gemeinden = get_gemeinden()
    selected_gemeinde = st.selectbox("Wähle eine Gemeinde:", gemeinden, index=None, placeholder="Wähle eine Gemeinde")
    


    if selected_gemeinde:
        details_df = get_details_for_gemeinde(selected_gemeinde)
        
        #st.subheader(f"Details for {selected_gemeinde}:")
        #st.dataframe(details_df)  # Display the DataFrame in Streamlit

        for index, row in details_df.iterrows():
            expander_title = f"{row['gruppe']}" 
            with st.expander(expander_title):
                detail = json.loads(f"{row['details']}")

                betroffene_themen = sorted(
                    [item['thema'] for item in detail if item['ist_betroffen'] == 1]
                )
                nicht_betroffene_themen = sorted(
                    [item['thema'] for item in detail if item['ist_betroffen'] == 0]
                )

                st.markdown("**Karte:**")
                betroffene_layer_id = sorted(
                    [item['layer_id'] for item in detail if item['ist_betroffen'] == 1]
                )
                nicht_betroffene_layer_id = sorted(
                    [item['layer_id'] + "!" for item in detail if item['ist_betroffen'] == 0]
                )
                combined_list = betroffene_layer_id + nicht_betroffene_layer_id
                output = ",".join(combined_list)
                bfsnr = str((detail[0]['bfsnr']))
                map_url += output + "&hp=ch.so.agi.gemeindegrenzen&hf=[[\"bfs_gemeindenummer\",\"=\",\""+bfsnr+"\"]]"
                st.page_link(map_url, label="Web GIS Client", icon=":material/map:")

                st.markdown("**Betroffene Themen:**")
                if betroffene_themen:
                    for thema in betroffene_themen:
                        st.markdown(thema)
                else:
                    st.markdown("--")

                st.markdown("**Nicht betroffene Themen:**")
                if nicht_betroffene_themen:
                    for thema in nicht_betroffene_themen:
                        st.markdown(thema)
                else:
                    st.markdown("--")

        with st.expander("Agglomerationsprogramm"):
            st.write("Dummy");

        with st.expander("Archäologische Fundstellen"):
            st.write("Dummy");

        with st.expander("Nutzungsplanung"):
            st.write("Dummy");

        with st.expander("Störfall"):
            st.write("Dummy");

        with st.expander("..."):
            st.write("Dummy");

except Exception as e:
    st.error(f"An error occurred: {e}")


