import dash
from dash import dcc, html
import plotly.express as px
import geojson
import pandas as pd
from flask import Flask, render_template
import json

# Cargar datos GeoJSON
with open('MUERTO.geojson') as f:
    geojson_data = json.load(f)

# Convertir el GeoJSON a un DataFrame
features = geojson_data['features']

# Extraer coordenadas y propiedades para el DataFrame
data = []
for feature in features:
    coords = feature['geometry']['coordinates']
    properties = feature['properties']
    data.append({
        'longitude': coords[0],
        'latitude': coords[1],
        'Genero': properties.get('GENERO'),
        'Fecha': properties.get("FECHA_HORA_ACC"), 
        'Muerte': properties.get('MUERTE_POSTERIOR'),
        'Codigo_AC':properties.get("CODIGO_ACCIDENTADO")
    })

df = pd.DataFrame(data)


server = Flask(__name__)

external_stylesheets = ['https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css']

app = dash.Dash(__name__, server=server, routes_pathname_prefix='/dash/', external_stylesheets=external_stylesheets)

fig = px.scatter_map(
    df,  
    
    lat="latitude",  
    lon="longitude",  
    color=("Genero"),  
    hover_name="Fecha",  
    hover_data=["Muerte","Codigo_AC"],
    title="Accidentes de Tráfico en Bogotá 2007-2024",
    labels={"Genero": "Sexo del Accidentado"},
)

# Configuración del mapa
fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=10,
    mapbox_center={"lat": 4.60971, "lon": -74.08175},  
)





df_accidentes = df["Genero"].value_counts().reset_index()
df_accidentes.columns = ["Genero", "count"]  

fig_accidentes = px.bar(
    df_accidentes,
    x="Genero", 
    y="count",
    labels={"Genero": "Género", "count": "Número de Accidentados"},
    title="Número de Accidentados por Género",
    color="Genero"
)


df_muertes = df[df["Muerte"] == "S"]["Genero"].value_counts().reset_index()
df_muertes.columns = ["Genero", "count"]  

fig_muertes = px.bar(
    df_muertes,
    x="Genero",
    y="count",
    labels={"Genero": "Género", "count": "Número de Fallecidos"},
    title="Número de Fallecidos por Género",
    color="Genero"
)
app.layout = html.Div([
    html.Div([
        html.Img(
            src="assets/logo.png",  # Ruta a la imagen
            style={
               'position': 'absolute',
            'top': '10px',
            'left': '10px',
            'height': '40px'
            }
        ),
        html.H2("Mapa de Accidentes de Tráfico en Bogotá por Género", 
                style={'color': '#00ff99', 'font-size': '24px', 'textAlign': 'center'})
    ], style={'position': 'relative', 'height': '80px'}),
    
    dcc.Graph(id="mapa", figure=fig),

    html.Div([
        html.H3("Análisis de Accidentes por Género", style={'color': '#00ff99', 'font-size': '20px','textAlign': 'center'}),
        dcc.Graph(id="grafico-accidentes", figure=fig_accidentes),
        dcc.Graph(id="grafico-muertes", figure=fig_muertes),|
    ], style={'margin-top': '30px'})
], style={'backgroundColor': '#121212', 'color': 'white', 'padding': '20px'})



@server.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    server.run(debug=False)