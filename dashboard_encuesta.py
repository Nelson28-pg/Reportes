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
color_celeste = "#A98700" # Color para la barra más alta (respuesta más común)
color_neutro = '#888888' # Color para las otras barras
color_neutro2 = "#7D7D7D" # Color para las otras barras

# =============================================
# FUNCIÓN PARA CREAR GRÁFICO
# =============================================
def crear_grafico_barras_horizontales(df, columna):
    # Contar la frecuencia de cada respuesta y ordenarlas de mayor a menor para el gráfico
    counts = df[columna].value_counts().sort_values(ascending=True)

    # Calcular porcentajes
    total_responses = counts.sum()
    percentages = (counts.values / total_responses * 100) if total_responses > 0 else [0] * len(counts)

    # Asignar colores: un color destacado para la barra más alta (la última, por el sort_values)
    colors = [color_neutro2] * (len(counts) - 1) + [color_celeste]

    # Crear un DataFrame para facilitar el manejo en Plotly
    df_grafico = pd.DataFrame({
        'respuesta': counts.index,
        'valores': counts.values,
        'porcentaje': percentages,
        'color': colors
    })

    fig = go.Figure()

    # --- Lógica para texto y hover ---
    text_values = []
    hover_templates = []
    for _, row in df_grafico.iterrows():
        # Si la barra es muy corta (ej. < 15%), el texto del porcentaje solo se muestra en el hover.
        if row['porcentaje'] < 21:
            text_values.append('') # No mostrar texto en la barra
            hover_templates.append(f"Porcentaje: {row['porcentaje']:.1f}%<br>Cantidad: <b>{row['valores']}</b><extra></extra>")
        else:
            text_values.append(f"{row['porcentaje']:.1f}%")
            hover_templates.append(f"<br>Cantidad: <b>{row['valores']}</b><extra></extra>")

    # Agregar barras horizontales
    fig.add_trace(go.Bar(
        y=df_grafico['respuesta'],
        x=df_grafico['porcentaje'],
        orientation='h',
        marker=dict(
            color=df_grafico['color'],
            line=dict(width=0),
            cornerradius=8
        ),
        text=text_values,
        textposition='outside',
        textfont=dict(
            size=12,
            color='white',
            family='Arial, sans-serif'
        ),
        hovertemplate=hover_templates,
        hoverlabel=dict(
            bgcolor=color_celeste, # Color de fondo del hover
            font=dict(color='black') # Color de la fuente del hover para contraste
        ),
        showlegend=False
    ))

    # --- Anotaciones para etiquetas de respuesta dentro de la barra ---
    annotations = []
    for i, row in df_grafico.iterrows():
        # El color de la etiqueta debe contrastar con el fondo de la barra.
        # Para los colores oscuros que usamos (celeste y gris), el blanco funciona bien.
        label_color = 'white'

        annotations.append(dict(
            xref='x', yref='y',
            x=2,  # Posicionar la etiqueta ligeramente a la derecha del inicio de la barra
            y=row['respuesta'],
            text=f"<b>{row['respuesta']}</b>",
            font=dict(family='Arial, sans-serif', size=13, color=label_color),
            showarrow=False,
            xanchor='left',
        ))

    # Configurar layout moderno y limpio
    fig.update_layout(
        title=dict(
            text=f'<b>{columna}</b>',
            x=0.14, #es el margen izquierdo del título
            xanchor='left',
            font=dict(size=16, family='Arial, sans-serif')
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', family='Arial, sans-serif'),
        margin=dict(l=90, r=30, t=60, b=40), # Aumentar margen derecho de los gráficos
        height=max(300, len(counts.index) * 50 + 60),
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[0, max(df_grafico['porcentaje']) * 1.40] # Aumentar espacio para texto fuera de la barra
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False # Ocultar etiquetas del eje Y, ya que usamos anotaciones
        ),
        bargap=0.5, # Espacio entre barras
        annotations=annotations
    )

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
