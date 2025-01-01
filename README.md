# sein-gui

```
python -m venv .venv
```

```
source .venv/bin/activate
```

```
pip install streamlit streamlit-folium
```

```
java -jar /Users/stefan/apps/ili2gpkg-5.1.1/ili2gpkg-5.1.1.jar --dbfile sein_konfig.gpkg --nameByTopic --defaultSrsCode 2056 --strokeArcs --models SO_ARP_SEin_Konfiguration_20241227 --modeldir "." --doSchemaImport --import themen_und_konfig.xtf
```

```
streamlit run app.py
```