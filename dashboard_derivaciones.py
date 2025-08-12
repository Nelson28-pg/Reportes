import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, State, ALL, callback_context
import os
import json

# =============================================
# FUNCIÓN PARA LEER ARCHIVO
# =============================================
def leer_archivo(ruta_csv):
    df = pd.read_csv(ruta_csv, sep=';', encoding='latin1')
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'AÑO': 'ANIO', 'Porcentaje de Eficiencia': 'EFICIENCIA'})

    for col in ['EFICIENCIA', 'NUMERADOR', 'DENOMINADOR']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.', regex=False), errors='coerce')

    df = df.fillna(0)
    df['ANIO'] = pd.to_numeric(df['ANIO'], errors='coerce')
    df = df.dropna(subset=['ANIO', 'INTENDENCIA'])
    df = df[df['ANIO'] >= 2020]
    return df

# =============================================
# CARGAR Y PROCESAR DATOS
# =============================================
def cargar_y_procesar_datos(ruta_csv):
    df = leer_archivo(ruta_csv)
    df_2025 = df[df['ANIO'] == 2025].copy()
    df_historico = df[df['ANIO'] < 2025].copy()
    anios_filtrables = sorted(df_historico["ANIO"].unique())
    return df, df_historico, df_2025, anios_filtrables

# =============================================
# FUNCIONES PARA CREAR GRÁFICOS
# =============================================
def crear_grafico_derivaciones(df_agg, df_comparacion_agg, df_2025_agg, anio_sel, nombre_anio_comparacion):
    fig = go.Figure()
    # --- LÍNEAS DEL AÑO SELECCIONADO ---
    fig.add_trace(go.Scatter(x=df_agg['INTENDENCIA'], y=df_agg['total_deriv'],
                             mode='lines', name=f'Derivaciones {anio_sel}',
                             line=dict(color='#FFA500', width=3),
                             hovertemplate="%{y:,.0f}"))
    # --- LÍNEAS DEL AÑO DE COMPARACIÓN ---
    fig.add_trace(go.Scatter(x=df_comparacion_agg['INTENDENCIA'], y=df_comparacion_agg['total_deriv_comp'],
                             mode='lines', name=f'Derivaciones {nombre_anio_comparacion}',
                             line=dict(color='#D3D3D3', width=1.5),
                             hovertemplate="%{y:,.0f}"))
    # --- LÍNEAS DE 2025 ---
    fig.add_trace(go.Scatter(x=df_2025_agg['INTENDENCIA'], y=df_2025_agg['total_deriv_2025'],
                             mode='lines', name='Derivaciones 2025',
                             line=dict(color='#00FFFF', width=3), visible='legendonly',
                             hovertemplate="%{y:,.0f}"))
    
    fig.update_layout(
        title='Total Derivaciones por Intendencia',
        paper_bgcolor="#2c2c2c",
        plot_bgcolor="#2c2c2c",
        font_color="white",
        height=400,
        showlegend=True,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    fig.update_yaxes(showgrid=False, showticklabels=False, title_text="")
    fig.update_xaxes(showgrid=False)
    return fig

def crear_grafico_cancelados(df_agg, df_comparacion_agg, df_2025_agg, anio_sel, nombre_anio_comparacion):
    fig = go.Figure()
    # --- LÍNEAS DEL AÑO SELECCIONADO ---
    fig.add_trace(go.Scatter(x=df_agg['INTENDENCIA'], y=df_agg['total_cobros'],
                             mode='lines', name=f'Cancelados {anio_sel}',
                             line=dict(color='#FFA500', width=3),
                             hovertemplate="%{y:,.0f}"))
    # --- LÍNEAS DEL AÑO DE COMPARACIÓN ---
    fig.add_trace(go.Scatter(x=df_comparacion_agg['INTENDENCIA'], y=df_comparacion_agg['total_cobros_comp'],
                             mode='lines', name=f'Cancelados {nombre_anio_comparacion}',
                             line=dict(color='#D3D3D3', width=1.5),
                             hovertemplate="%{y:,.0f}"))
    # --- LÍNEAS DE 2025 ---
    fig.add_trace(go.Scatter(x=df_2025_agg['INTENDENCIA'], y=df_2025_agg['total_cobros_2025'],
                             mode='lines', name='Cancelados 2025',
                             line=dict(color='#00FFFF', width=3), visible='legendonly',
                             hovertemplate="%{y:,.0f}"))

    fig.update_layout(
        title='Total Cancelados por Intendencia',
        paper_bgcolor="#2c2c2c",
        plot_bgcolor="#2c2c2c",
        font_color="white",
        height=400,
        showlegend=True,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    fig.update_yaxes(showgrid=False, showticklabels=False, title_text="")
    fig.update_xaxes(showgrid=False, tickangle=0, showticklabels=True, tickfont=dict(size=11), tickcolor='#2c2c2c', automargin=False, title_standoff=45, ticklen=10, ticks="outside")
    return fig

# =============================================
# CARGAR DATOS INICIALES
# =============================================
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "Eficiencia_cobranzaNC_2020-2025.csv")
    df_full, df_historico, df_2025, anios_filtrables = cargar_y_procesar_datos(csv_path)

except Exception as e:
    print(f"Error al cargar datos en dashboard_derivaciones: {e}")
    df_full, df_historico, df_2025, anios_filtrables = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), []


# =============================================
# ESTILOS
# =============================================
card_style = {
    'backgroundColor': '#333333', 'padding': '20px', 'borderRadius': '10px',
    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.4)', 'textAlign': 'center', 'flex': '1', 'margin': '0 10px'
}

radio_items_container_style = {
    'display': 'flex', 'justifyContent': 'center', 'gap': '20px',
    'margin': '10px 0', 'padding': '5px', 'backgroundColor': '#1a1a1a',
    'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.2)',
    'flexWrap': 'wrap'
}
radio_item_style = {
    'backgroundColor': '#333333', 'color': 'white', 'padding': '8px 15px',
    'borderRadius': '5px', 'cursor': 'pointer', 'border': '1px solid #444',
    'transition': 'all 0.2s ease-in-out',
    'flex-grow': '1', 'text-align': 'center',
    'margin-right': '10px'
}
radio_item_selected_style = {
    **radio_item_style,
    'backgroundColor': '#00FFFF', 'color': 'black', 'border': '1px solid #00FFFF'
}

# =============================================
# LAYOUT DE LA APLICACIÓN
# =============================================
def get_layout():
    layout = html.Div(
        className='dashboard-content',
        style={"backgroundColor": "#2c2c2c", "color": "white", "padding": "10px", "fontFamily": "Arial, sans-serif"},
        children=[
            dcc.Store(id='store-selected-year-derivaciones', data=anios_filtrables[0] if anios_filtrables else None),
            html.Div(
                style={
                    "backgroundColor": "#1a1a1a", "padding": "10px", "borderRadius": "10px",
                    "marginBottom": "10px", "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.3)"
                },
                children=[
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "gap": "15px", "flexWrap": "wrap"},
                        children=[
                            html.Div(
                                id='panel-anios-derivaciones',
                                style=radio_items_container_style,
                                children=[
                                    html.Button(
                                        str(anio),
                                        id={'type': 'btn-anio-derivaciones', 'index': int(anio)},
                                        n_clicks=0,
                                    ) for anio in anios_filtrables
                                ]
                            ),
                            dcc.Dropdown(
                                id="filtro-intendencia-grupo",
                                options=[
                                    {'label': 'Todas las Intendencias', 'value': 'TODAS'},
                                    {'label': 'Intendencias Regionales', 'value': 'REGIONALES'}
                                ],
                                value='TODAS',
                                clearable=False,
                                style={'color': '#000', 'backgroundColor': '#ADD8E6', 'minWidth': '200px', 'flex': '1'}
                            )
                        ]
                    )
                ]
            ),

            html.Div(style={"padding": "5px 20px"}, children=[
                html.Div(id='stats-panel-derivaciones', style={"display": "flex", "justifyContent": "center", "alignItems": "stretch", "margin": "5px 0"}),
                dcc.Graph(id='grafico-derivaciones'),
                dcc.Graph(id='grafico-cancelados')
            ])
        ]
    )
    return layout

# =============================================
# CALLBACKS
# =============================================
def register_callbacks(app):
    @app.callback(
        Output('store-selected-year-derivaciones', 'data'),
        Input({'type': 'btn-anio-derivaciones', 'index': ALL}, 'n_clicks'),
        State('store-selected-year-derivaciones', 'data'),
        prevent_initial_call=True
    )
    def update_selected_year(n_clicks, current_year):
        ctx = callback_context
        if not ctx.triggered or not ctx.triggered[0]['value']:
            return current_year

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        year = json.loads(button_id)['index']
        return year

    @app.callback(
        Output({'type': 'btn-anio-derivaciones', 'index': ALL}, 'style'),
        Input('store-selected-year-derivaciones', 'data')
    )
    def update_button_styles(selected_year):
        styles = []
        for anio in anios_filtrables:
            if anio == selected_year:
                styles.append(radio_item_selected_style)
            else:
                styles.append(radio_item_style)
        return styles

    @app.callback(
        [Output("grafico-derivaciones", "figure"),
         Output("grafico-cancelados", "figure"),
         Output('stats-panel-derivaciones', 'children')],
        [Input("store-selected-year-derivaciones", "data"),
         Input("filtro-intendencia-grupo", "value")]
    )
    def actualizar_analisis_derivaciones(anio_sel, intendencia_grupo_sel):
        fig_empty = go.Figure().update_layout(paper_bgcolor="#2c2c2c", plot_bgcolor="#2c2c2c", font_color="white")
        
        if not anio_sel:
            return fig_empty, fig_empty, []

        # Filtrar datos para el año seleccionado
        df_filtered_by_year = df_full[df_full["ANIO"] == anio_sel].copy()

        # Determinar el año de comparación
        if anio_sel == anios_filtrables[0]:
            anio_comparacion = df_full['ANIO'].max()
            nombre_anio_comparacion = f'Actual ({anio_comparacion})'
        else:
            anio_comparacion = anio_sel - 1
            nombre_anio_comparacion = f'Anterior ({anio_comparacion})'

        df_comparacion_raw = df_full[df_full["ANIO"] == anio_comparacion].copy()

        # Aplicar filtro de intendencia
        if intendencia_grupo_sel == 'REGIONALES':
            df_filt = df_filtered_by_year[df_filtered_by_year['INTENDENCIA'] != 'ILM'].copy()
            df_comparacion_filt = df_comparacion_raw[df_comparacion_raw['INTENDENCIA'] != 'ILM'].copy()
        else: # 'TODAS'
            df_filt = df_filtered_by_year.copy()
            df_comparacion_filt = df_comparacion_raw.copy()

        if df_filt.empty:
            return fig_empty, fig_empty, []

        # Procesamiento de datos
        df_agg = df_filt.groupby('INTENDENCIA').agg(
            total_deriv=('DENOMINADOR', 'sum'),
            total_cobros=('NUMERADOR', 'sum')
        ).reset_index().sort_values('total_deriv', ascending=True)

        df_comparacion_agg = df_comparacion_filt.groupby('INTENDENCIA').agg(
            total_deriv_comp=('DENOMINADOR', 'sum'),
            total_cobros_comp=('NUMERADOR', 'sum')
        ).reset_index()
        df_comparacion_agg = pd.merge(df_agg[['INTENDENCIA']], df_comparacion_agg, on='INTENDENCIA', how='left').fillna(0)

        df_2025_agg = df_2025.groupby('INTENDENCIA').agg(
            total_deriv_2025=('DENOMINADOR', 'sum'),
            total_cobros_2025=('NUMERADOR', 'sum')
        ).reset_index()
        df_2025_agg = pd.merge(df_agg[['INTENDENCIA']], df_2025_agg, on='INTENDENCIA', how='left').fillna(0)

        # Crear figuras
        fig_derivaciones = crear_grafico_derivaciones(df_agg, df_comparacion_agg, df_2025_agg, anio_sel, nombre_anio_comparacion)
        fig_cancelados = crear_grafico_cancelados(df_agg, df_comparacion_agg, df_2025_agg, anio_sel, nombre_anio_comparacion)

        # Calcular estadísticas
        total_deriv = df_filt['DENOMINADOR'].sum()
        total_cobro = df_filt['NUMERADOR'].sum()
        prom_eficiencia = (total_cobro / total_deriv * 100) if total_deriv > 0 else 0

        stats_cards = [
            html.Div(style=card_style, children=[
                html.H4(f"{total_deriv:,.0f}", style={"margin": "0", "fontSize": "36px", "color": "#00FFFF"}),
                html.P(f"Total Derivaciones", style={"margin": "5px 0 0 0", "fontSize": "14px"})
            ]),
            html.Div(style=card_style, children=[
                html.H4(f"{total_cobro:,.0f}", style={"margin": "0", "fontSize": "36px", "color": "#FEF7F5"}),
                html.P(f"Total Cancelados", style={"margin": "5px 0 0 0", "fontSize": "14px"})
            ]),
            html.Div(style=card_style, children=[
                html.H4(f"{prom_eficiencia:.1f}%", style={"margin": "0", "fontSize": "36px", "color": "#00FFFF"}),
                html.P(f"Promedio Eficiencia", style={"margin": "5px 0 0 0", "fontSize": "14px"})
            ])
        ]
        
        return fig_derivaciones, fig_cancelados, stats_cards
