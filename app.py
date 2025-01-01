import streamlit as st
import sqlite3
import pandas as pd
import json

db_path = "sein_konfig.gpkg"
#map_url = "https://geo.so.ch/map/?t=default&bl=hintergrundkarte_sw&c=2618500,1238000&s=188976&l="
map_url = "https://geo.so.ch/map/?t=default&bl=hintergrundkarte_sw&l="

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

# Streamlit app
st.title("SEin-App")

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