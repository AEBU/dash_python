# -*- coding: utf-8 -*-
"""
Created on Wed Jun 23 22:24:59 2021

@author: Alexis Bautista
"""

# FASE 1: IMPORTAR LIBRERÍAS
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output
from CONSTANTES import TOKEN_MAPBOX

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

#


# FASE 2: CARGA DE DATOS
# Ventas Detalles
df_ventas = pd.read_excel('Ventas.xlsx', sheet_name='Detalle')
# Ventas Acumuladas
df_ventas_acum = pd.read_excel('Ventas.xlsx', sheet_name='Acumulado')

# FASE 3: CREACIÓN GRÁFICO GEOGRÁFICO
mapbox_access_token = TOKEN_MAPBOX

# DEFINIR FIGURA ESTÁTICA PARA VENTAS GEOGRÁFICAS
fig_mapa = go.Figure(go.Scattermapbox(
        lon = df_ventas_acum['Longitud'],
        lat = df_ventas_acum['Latitud'],
        mode='markers',
        text = ["Ventas Totales: " + str(x) for x in df_ventas_acum['Suma Ingresos']],
        textposition = "bottom right",
        marker=go.scattermapbox.Marker(
            size=df_ventas_acum['Suma Ingresos']/50000,
            color=df_ventas_acum['Suma Ingresos']/50000
        )
    ))

fig_mapa.update_layout(
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=dict(
            lat=47.2333,
            lon=22.65
        ),
        pitch=0,
        zoom=2
    ),
    showlegend = True
)

## Definición de Gráficos
# Barplot Importe vs Segmento
df_agrupado_seg = df_ventas.groupby("Segmento")["Importe"].agg("sum").to_frame(name = "Ingresos").reset_index()
    

data2 = [go.Bar(x=df_agrupado_seg["Segmento"],
            y=df_agrupado_seg["Ingresos"])]

layout2 = go.Layout(title="Ingresos por segmento",
                    xaxis=dict(title="Segmento"),
                    yaxis=dict(title="Ingreso"))

# Barplot Beneficios vs Categoría
df_agrupado_cat = df_ventas.groupby("Categoría")["Beneficio"].agg("sum").to_frame(name = "Beneficios").reset_index()
    

data3 = [go.Bar(x=df_agrupado_cat["Categoría"],
            y=df_agrupado_cat["Beneficios"])]

layout3 = go.Layout(title="Beneficios por categoría",
                    xaxis=dict(title="Categorías"),
                    yaxis=dict(title="Beneficios"))


# Scatter plot Cantidad por fecha
df_agrupado_date = df_ventas.groupby("Fecha compra")["Cantidad"].agg("sum").to_frame(name = "Cantidad").reset_index()

data1 = [go.Scatter(x=df_agrupado_date["Fecha compra"],
                    y=df_agrupado_date["Cantidad"],
                    mode="lines+markers",
                    opacity=0.7,
                    marker={'size': 5}
                    )]

layout1 = go.Layout(title="Cantidades en Fechas",
                    xaxis=dict(title="Fecha"),
                    yaxis=dict(title="Cantidad"),
                    hovermode='closest')





# FASE 4: DEFINICIÓN LAYOUT
app.layout = html.Div([
                    
                html.Div([
                    # Dropdown para países
                    html.Div([
                    html.Label('País'),
                    dcc.Dropdown(id='selector_country',
                        options=[{'label': i, 'value': i} for i in df_ventas['País'].unique()],
                        value='Spain'
                    )],style={'width': '48%', 'display': 'inline-block'}),

                    #Dropdown para fechas
                    html.Div(                        
                        [
                        html.Label('Rango fechas'),
                        dcc.DatePickerRange(id='selector_fecha',start_date=df_ventas["Fecha compra"].min(),end_date=df_ventas["Fecha compra"].max())
                        ],style={'width': '48%', 'float': 'right'}, className="box-flex"),

                    ], className= "div-headers"),
  
                    # Ventas Segmento vs Ingresos
                    html.Div([
                        dcc.Graph(id='barplot_ventas_seg',
                             figure = {'data':data2,
                            'layout':layout2})
                        ], style={'width': '33%', 'float': 'left', 'display': 'inline-block'}),

                    # Ventas Categoría vs Beneficios
                    html.Div([
                        dcc.Graph(id='barplot_ventas_cat',
                             figure = {'data':data3,
                            'layout':layout3})
                        ], style={'width': '33%', 'float': 'center', 'display': 'inline-block'}),
                    
                    # Catndidad en fechas de compra
                    html.Div([
                        dcc.Graph(id='scatter_quantity_date',
                             figure = {'data':data1,
                            'layout':layout1})
                        ], style={'width': '33%', 'float': 'right', 'display': 'inline-block'}),

                    # Integración del mapa
                    html.Div([
                        dcc.Graph(id='mapa_ventas', 
                                  figure=fig_mapa)
                        ],style={'width': '100%'}),                
                    ])


# FASE 4: Callback para actualizar gráfico de Segmento en función del dropdown de País y según selector de fechas

@app.callback(Output('barplot_ventas_seg', 'figure'),
              [Input('selector_country', 'value'),
               Input('selector_fecha','start_date'),
               Input('selector_fecha','end_date')])
def actualizar_graph_seg(selector_country, fecha_min, fecha_max):
    filtered_df = df_ventas[
                     (df_ventas["País"]==selector_country)
                     & (df_ventas["Fecha compra"]>=fecha_min) 
                     & (df_ventas["Fecha compra"]<=fecha_max)
                     ]
    
    df_agrupado = filtered_df.groupby("Segmento")["Importe"].agg("sum").to_frame(name = "Ingresos").reset_index()
    
    data2 = [go.Bar(x=df_agrupado["Segmento"],
            y=df_agrupado["Ingresos"])]

    return{
        'data': data2,
        'layout': layout2
        }
        

# Funciones para la parte de Beneficios por categoría
@app.callback(Output('barplot_ventas_cat', 'figure'),
              [Input('selector_country', 'value'),
               Input('selector_fecha','start_date'),
               Input('selector_fecha','end_date'),
               Input('barplot_ventas_seg', 'hoverData')])
def actualizar_graph_cat(selector_country, fecha_min, fecha_max, hover_data_seg):
    """
    {'points': [{'curveNumber': 0, 'pointNumber': 0, 'pointIndex': 0, 'x': 'Consumer', 'y': 905453.4515999986, 'label': 'Consumer', 'value': 905453.4515999986}]}
    """
    filtered_df = df_ventas[
                     (df_ventas["País"]==selector_country)
                     & (df_ventas["Fecha compra"]>=fecha_min) 
                     & (df_ventas["Fecha compra"]<=fecha_max)
                     & (df_ventas["Fecha compra"]<=fecha_max)                     
                     ]
    
    if hover_data_seg is not None:
        filtered_df = filtered_df [
                     (filtered_df["Segmento"]==hover_data_seg['points'][0]['x'])
                ]

    # Barplot Beneficios vs Categoría
    df_agrupado_cat = filtered_df.groupby("Categoría")["Beneficio"].agg("sum").to_frame(name = "Beneficios").reset_index()
        
    
    data3 = [go.Bar(x=df_agrupado_cat["Categoría"],
                y=df_agrupado_cat["Beneficios"])]

    return{
        'data': data3,
        'layout': layout3
        }


# Funciones para Fecha Compra y Cantdiad
@app.callback(Output('scatter_quantity_date', 'figure'),
              [Input('selector_country', 'value'),
               Input('selector_fecha','start_date'),
               Input('selector_fecha','end_date')])
def actualizar_scatter(selector_country, fecha_min, fecha_max):
    filtered_df = df_ventas[
                     (df_ventas["País"]==selector_country)
                     & (df_ventas["Fecha compra"]>=fecha_min) 
                     & (df_ventas["Fecha compra"]<=fecha_max)
                     ]

    # Barplot Beneficios vs Categoría
    df_agrupado_date = filtered_df.groupby("Fecha compra")["Cantidad"].agg("sum").to_frame(name = "Cantidad").reset_index()        
    
    data1 = [go.Scatter(x=df_agrupado_date["Fecha compra"],
                        y=df_agrupado_date["Cantidad"],
                        mode="lines+markers",
                        opacity=0.7,
                        marker={'size': 5}
                        )]

    return{
        'data': data1,
        'layout': layout1
        }



if __name__ == '__main__':
    #app.run_server()
    app.run_server(debug=True, use_reloader=False)

#