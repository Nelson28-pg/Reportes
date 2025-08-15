import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, State, callback_context
import os
import json
import numpy as np

# =============================================
# FUNCIÓN PARA LEER ARCHIVO
# =============================================
def leer_archivo(ruta_xlsx):
    # Lee un archivo de Excel. Se necesita tener instalado 'openpyxl'
    df = pd.read_excel(ruta_xlsx)
    df.columns = df.columns.str.strip()
    return df

# =============================================
# CARGAR DATOS INICIALES
# =============================================
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    xlsx_path = os.path.join(script_dir, "limpieza encuesta_cnc.xlsx")
    df_encuesta = leer_archivo(xlsx_path)
    columnas_graficables = df_encuesta.columns[2:].tolist() # Excluir IRE y grupo_eficiencia
except Exception as e:
    print(f"Error al cargar datos en dashboard_encuesta: {e}")
    df_encuesta = pd.DataFrame()
    columnas_graficables = []

# =============================================
# ESTILOS Y COLORES
# =============================================
# --- Estilos para los componentes del dashboard ---
# Puede personalizar estos diccionarios para cambiar la apariencia de los controles.

# Estilo para el panel que contiene los filtros (botones y dropdown)
control_panel_style = {
    'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'gap': '20px',
    'margin': '10px 0', 'padding': '10px', 'backgroundColor': '#1a1a1a',
    'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.2)',
}

# Estilo base para los botones de filtro de preguntas
button_style = {
    'backgroundColor': '#333333', 'color': 'white', 'padding': '8px 15px',
    'borderRadius': '5px', 'cursor': 'pointer', 'border': '1px solid #444',
    'transition': 'all 0.2s ease-in-out'
}

# Estilo para el botón cuando está seleccionado (activo)
button_selected_style = {
    **button_style,
    'backgroundColor': '#00FFFF', 'color': 'black', 'border': '1px solid #00FFFF'
}

# Estilo para las tarjetas que contienen cada gráfico
graph_card_style = {
    'backgroundColor': '#333333', 'padding': '20px', 'borderRadius': '10px',
    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.4)',
    'flex': '1 1 45%', 'margin': '10px', 'minWidth': '400px'
}

# Estilo para las tarjetas de estadísticas, similar a los otros dashboards
stat_card_style = {
    'backgroundColor': '#333333', 'padding': '20px', 'borderRadius': '10px',
    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.4)',
    'textAlign': 'center', 'flex': '1', 'margin': '0'
}

# --- Paletas de colores para los gráficos ---
# Puede cambiar o agregar colores a estas listas.
color_celeste = "#FFCC00" # Color para la barra más alta (respuesta más común)
color_neutro = '#888888' # Color para las otras barras
color_neutro2 = "#AAAAAA" # Color para las otras barras

# =============================================
# FUNCIÓN PARA CREAR GRÁFICO
# =============================================
def crear_grafico_barras_horizontales(df, columna):
    # Contar la frecuencia de cada respuesta y ordenarlas de menor a mayor
    counts = df[columna].value_counts().sort_values(ascending=True)

    # Calcular porcentajes
    total_responses = counts.sum()
    percentages = (counts.values / total_responses * 100) if total_responses > 0 else [0] * len(counts)

    # Asignar colores: uno especial para la barra más alta y otros para el resto
    colors = [color_neutro2] * (len(counts) - 1) + [color_celeste]

    fig = go.Figure(data=[go.Bar(
        y=counts.index,
        x=counts.values,
        orientation='h',
        # Personalización de las barras
        marker=dict(
            color=colors, 
            line=dict(color='#2c2c2c', width=0.2), # Borde de las barras
            cornerradius=10 # Bordes de barra redondeados
        ),
        # El texto con el valor porcentual se posiciona fuera de la barra.
        text=[f'{p:.1f}%' for p in percentages],
        textposition='outside',
        textfont=dict(color='white', size=12),
        # Personalización del texto que aparece al pasar el cursor (hover)
        hovertemplate='cant : <b>%{x}</b><extra></extra>'
    )])
    
    # --- Personalización del Layout del Gráfico ---
    height = max(250, len(counts.index) * 40 + 80) # Altura dinámica del gráfico
    
    # Se preparan las anotaciones para colocar la etiqueta de categoría encima de cada barra.
    annotations = []
    for i, label in enumerate(counts.index):
        # El color de la anotación es blanco para todas las barras, excepto la más alta.
        annotation_color = 'white' if i < len(counts) - 1 else colors[i]
        annotations.append(
            dict(
                xref='x', yref='y',
                x=0, y=label, # Posición al inicio de la barra
                xanchor='left',
                text= f'{str(label)}',
                font=dict(family='Arial', size=15, color=annotation_color),
                showarrow=False,
                align='left',
                yshift=24 # Se ajusta el desplazamiento para la nueva fuente
            )
        )

    fig.update_layout(
        # Para poner el título en negrita, usamos etiquetas HTML <b>
        title_text=f'{columna}',
        title_x=0.03, # Alinea el título a la izquierda
        title_xanchor='left',
        paper_bgcolor="rgba(0,0,0,0)", # Fondo del área del gráfico (transparente para ver el de la tarjeta)
        plot_bgcolor="rgba(0,0,0,0)",  # Fondo del área de trazado (transparente)
        font_color="white",
        showlegend=False,
        margin=dict(t=50, b=20, l=20, r=60), # Ajustar márgenes para las etiquetas
        height=height,
        # Se reduce el espacio entre barras para que estas sean más gruesas y modernas.
        bargap=0.6,
        annotations=annotations
    )
    # Ocultar líneas y etiquetas de los ejes para un look más limpio
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=False) # Se oculta el eje Y, ya que se usan anotaciones
    return fig

# =============================================
# LAYOUT DE LA APLICACIÓN
# =============================================
def get_layout():
    layout = html.Div(
        className='dashboard-content',
        style={"backgroundColor": "#2c2c2c", "color": "white", "padding": "10px", "fontFamily": "Arial, sans-serif"},
        children=[
            # Almacén de datos en el lado del cliente para guardar el estado del filtro de preguntas
            dcc.Store(id='store-question-filter-encuesta', data='primeras'),
            # Panel de control principal con filtros
            html.Div(
                style={
                    "backgroundColor": "#1a1a1a", "padding": "15px", "borderRadius": "10px",
                    "marginBottom": "10px", "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.3)"
                },
                children=[
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "gap": "15px", "flexWrap": "wrap", "justifyContent": "center"},
                        children=[
                            html.Div(
                                # Contenedor para los botones de filtro de preguntas
                                id='panel-botones-encuesta',
                                style=control_panel_style,
                                children=[
                                    html.Button('Las primeras 5 preguntas', id='btn-primeras-5-encuesta', n_clicks=0, style=button_style),
                                    html.Button('Las últimas 5 preguntas', id='btn-ultimas-5-encuesta', n_clicks=0, style=button_style),
                                ]
                            ),
                            # Dropdown para filtrar por grupo de eficiencia
                            dcc.Dropdown(
                                id="dropdown-filter-encuesta",
                                options=[
                                    {'label': 'Mayores a Línea Base', 'value': 'mayor a Linea Base'},
                                    {'label': 'Menores a Línea Base', 'value': 'menor a Linea Base'},
                                    {'label': 'Todas las intendencias', 'value': 'Todas las intendencias'}
                                ],
                                value='Todas las intendencias',
                                clearable=False,
                                style={'color': '#000', 'backgroundColor': '#ADD8E6', 'minWidth': '250px', 'flex': '1'}
                            )
                        ]
                    )
                ]
            ),
            # Contenedor donde se renderizarán los gráficos
            html.Div(
                id='graficos-encuesta-container', 
                style={
                    'marginTop': '20px', 'display': 'flex', 
                    'flexWrap': 'wrap', 'justifyContent': 'space-around',
                    # Se agrega un margen horizontal para que las tarjetas no lleguen a los bordes de la página.
                    'margin': '0 40px'
                }
            )
        ]
    )
    return layout

# =============================================
# CALLBACKS
# =============================================
def register_callbacks(app):
    # Callback para actualizar el filtro de preguntas (primeras/últimas 5) en el dcc.Store
    @app.callback(
        Output('store-question-filter-encuesta', 'data'),
        [Input('btn-primeras-5-encuesta', 'n_clicks'),
         Input('btn-ultimas-5-encuesta', 'n_clicks')],
        prevent_initial_call=True
    )
    def update_question_filter(btn_primeras, btn_ultimas):
        ctx = callback_context
        if not ctx.triggered:
            return 'primeras'
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'btn-ultimas-5-encuesta':
            return 'ultimas'
        return 'primeras'

    # Callback para actualizar el estilo de los botones según el filtro seleccionado
    @app.callback(
        [Output('btn-primeras-5-encuesta', 'style'),
         Output('btn-ultimas-5-encuesta', 'style')],
        [Input('store-question-filter-encuesta', 'data')]
    )
    def update_button_styles(selected_filter):
        if selected_filter == 'primeras':
            return button_selected_style, button_style
        elif selected_filter == 'ultimas':
            return button_style, button_selected_style
        return button_style, button_style

    # Callback principal para generar y actualizar los gráficos
    @app.callback(
        Output("graficos-encuesta-container", "children"),
        [Input("store-question-filter-encuesta", "data"),
         Input("dropdown-filter-encuesta", "value")]
    )
    def actualizar_graficos_encuesta(question_filter, selected_filter):
        if df_encuesta.empty:
            return [html.P("No se pudieron cargar los datos de la encuesta.")]

        df_filtered = df_encuesta.copy()
        if selected_filter != 'Todas las intendencias':
            df_filtered = df_encuesta[df_encuesta['grupo_eficiencia'] == selected_filter]

        # --- Tarjeta de Estadísticas Adicional ---
        # Se crea una tarjeta extra con información resumida.
        # Se coloca al inicio para que el orden de los gráficos sea ascendente.
        
        # Calcular el número de participantes únicos según el filtro actual
        total_ires = df_filtered['IRE'].nunique() if 'IRE' in df_filtered.columns else 0

        # Crear la tarjeta de estadísticas con un estilo consistente al resto del proyecto
        stats_card = html.Div(
            style={**graph_card_style, 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'alignItems': 'center', 'gap': '10px'},
            children=[
                # Fila superior con dos tarjetas
                html.Div(
                    style={'display': 'flex', 'justifyContent': 'center', 'width': '100%', 'gap': '10px'},
                    children=[
                        # Tarjeta de participantes
                        html.Div(style=stat_card_style, children=[
                            html.H4(f"{total_ires}", style={"margin": "0", "fontSize": "36px", "color": "#00FFFF"}),
                            html.P("Intendencias participantes", style={"margin": "5px 0 0 0", "fontSize": "14px", "color": "white"})
                        ]),
                        # Tarjeta de no participantes
                        html.Div(style=stat_card_style, children=[
                            html.H4("3", style={"margin": "0", "fontSize": "36px", "color": "#00FFFF"}),
                            html.P("No participaron", style={"margin": "5px 0 0 0", "fontSize": "14px", "color": "white"})
                        ]),
                    ]
                ),
                # Fila inferior con una tarjeta
                html.Div(
                    style={**stat_card_style, 'width': '100%', 'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'boxSizing': 'border-box'},
                    children=[
                        html.P("Encuesta realizada por UCEC - 12/08/2025", style={'color': '#D3D3D3', 'fontSize': '12px'})
                    ]
                )
            ]
        )

        children_elements = [stats_card]

        if question_filter == 'primeras':
            preguntas_a_mostrar = columnas_graficables[:5]
        else:
            preguntas_a_mostrar = columnas_graficables[-5:]

        for col in preguntas_a_mostrar:
            grafico_div = html.Div(
                dcc.Graph(figure=crear_grafico_barras_horizontales(df_filtered, col), config={'displayModeBar': False}),
                style=graph_card_style
            )
            children_elements.append(grafico_div)
        
        return children_elements
