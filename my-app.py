import streamlit as st
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium
import streamlit.components.v1 as components

st.title("SEin-App")

m = folium.Map(
    location=[47.208703, 7.536123], 
    zoom_start=12,
    max_zoom = 22,
    tiles=None
    #tiles="https://wmts.geo.admin.ch/1.0.0/ch.kantone.cadastralwebmap-farbe/default/current/3857/{z}/{x}/{y}.png",
    #attr='Map data: &copy; <a href="https://www.swisstopo.ch" target="_blank" rel="noopener noreferrer">swisstopo</a>, <a href="https://www.housing-stat.ch/" target="_blank" rel="noopener noreferrer">BFS</a>'
)

# folium.TileLayer(
#     tiles="https://wmts.geo.admin.ch/1.0.0/ch.kantone.cadastralwebmap-farbe/default/current/3857/{z}/{x}/{y}.png",
#     attr="© Swisstopo",
#     name="Swisstopo Map",
#     overlay=False,
# ).add_to(m)

folium.WmsTileLayer(
    url="https://geo.so.ch/api/wms",  # Example WMS server
    layers="ch.so.agi.hintergrundkarte_sw",
    name="Hintergrundkarte s/w",
    fmt="image/png",
    max_zoom = 22,
    transparent=False,
    overlay=False
).add_to(m)

folium.WmsTileLayer(
    url="https://geo.so.ch/api/wms",  # Example WMS server
    layers="ch.so.agi.hintergrundkarte_ortho",
    name="Hintergrundkarte Luftbild",
    fmt="image/png",
    max_zoom = 22,
    transparent=False,
    overlay=False
).add_to(m)


folium.WmsTileLayer(
    url="https://geo.so.ch/api/wms",  # Example WMS server
    layers="ch.so.alw.fruchtfolgeflaechen",
    name="WMS Layer Example",
    fmt="image/png",
    opacity=0.6,
    max_zoom = 22,
    transparent=True
).add_to(m)

lc = folium.map.LayerControl(collapsed=True)
lc.add_to(m)

output = st_folium(m, width=700, height=500)


components.iframe("https://geo.so.ch/map/?t=default&l=&bl=hintergrundkarte_sw&c=2618500%2C1238000&s=188976", height=500)
