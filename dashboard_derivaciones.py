import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
# FUNCIÓN PARA CREAR GRÁFICO DE DERIVACIONES Y EFICIENCIA
# =============================================
def crear_grafico_derivaciones_eficiencia(df_anio):
    if 'DENOMINADOR' not in df_anio.columns or 'NUMERADOR' not in df_anio.columns or 'EFICIENCIA' not in df_anio.columns:
        return go.Figure().update_layout(title='Columnas necesarias no encontradas', paper_bgcolor="#2c2c2c", plot_bgcolor="#2c2c2c", font_color="white"), 0, 0, 0

    # Suma total de derivaciones y cobros para el año seleccionado
    total_derivaciones_anio = df_anio['DENOMINADOR'].sum()
    total_cobros_anio = df_anio['NUMERADOR'].sum()

    # Agrupar por intendencia y sumar derivaciones, cobros y calcular eficiencia promedio
    df_agg = df_anio.groupby('INTENDENCIA').agg(
        total_deriv=('DENOMINADOR', 'sum'),
        total_cobros=('NUMERADOR', 'sum'),
        eficiencia_promedio=('EFICIENCIA', 'mean')
    ).reset_index()

    # Ordenar por total_derivaciones de forma ascendente
    df_agg = df_agg.sort_values('total_deriv', ascending=True)

    # Calcular promedio de eficiencia para el año
    promedio_eficiencia_anio = df_agg['eficiencia_promedio'].mean()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=False, vertical_spacing=0.1, 
                        subplot_titles=('Total Derivaciones por Intendencia', 'Total Cancelados por Intendencia'))

    # Subplot 1: Total Derivaciones
    fig.add_trace(go.Bar(x=df_agg['INTENDENCIA'], y=df_agg['total_deriv'], name='Derivaciones', marker_color='#2196F3',
                         text=df_agg['total_deriv'].apply(lambda x: f'{x:,.0f}'), textposition='outside',
                         hovertemplate="<b>%{x}</b><extra></extra>"), row=1, col=1)
    fig.update_yaxes(title_text="", showticklabels=False, row=1, col=1)
    fig.update_xaxes(showticklabels=False, row=1, col=1) # Eliminar eje x

    # Subplot 2: Total Cancelados por Intendencia
    max_value = df_agg['total_cobros'].max()
    textpositions = ['outside' if v < 0.1 * max_value else 'inside' for v in df_agg['total_cobros']]

    fig.add_trace(go.Bar(x=df_agg['INTENDENCIA'], y=df_agg['total_cobros'], name='Cancelados', marker_color='#FF5722',
                         text=df_agg['total_cobros'].apply(lambda x: f'<b>{x:,.0f}</b>'), textposition=textpositions, textangle=0, insidetextanchor='middle',
                         customdata=df_agg['eficiencia_promedio'], hovertemplate="Eficiencia:<br><b>%{customdata:.1f}</b><extra></extra>"), row=2, col=1)

    fig.update_yaxes(title_text="", showticklabels=False, row=2, col=1)
    fig.update_xaxes(tickangle=0, showticklabels=True, row=2, col=1, tickfont=dict(size=11), automargin=False, title_standoff=45, ticklen=10, ticks="outside") # Mostrar eje x

    fig.update_layout(paper_bgcolor="#2c2c2c", plot_bgcolor="#2c2c2c", font_color="white", height=800, showlegend=False, margin=dict(t=100))
    fig.update_yaxes(showgrid=False)

    # Actualizar anotaciones de subtítulos
    fig.update_annotations(x=0, xanchor='left', font=dict(size=16, color='white', family='Arial, sans-serif', weight='bold'))

    return fig, total_derivaciones_anio, total_cobros_anio, promedio_eficiencia_anio

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
        style={"backgroundColor": "#2c2c2c", "color": "white", "padding": "15px", "fontFamily": "Arial, sans-serif"},
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
                dcc.Graph(id='grafico-derivaciones')
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
        [Output("grafico-derivaciones", "figure"), Output('stats-panel-derivaciones', 'children')],
        [Input("store-selected-year-derivaciones", "data"),
         Input("filtro-intendencia-grupo", "value")]
    )
    def actualizar_analisis_derivaciones(anio_sel, intendencia_grupo_sel):
        fig_empty = go.Figure().update_layout(paper_bgcolor="#2c2c2c", plot_bgcolor="#2c2c2c", font_color="white")
        fig = fig_empty

        if not anio_sel:
            return fig, []

        df_filtered_by_year = df_full[df_full["ANIO"] == anio_sel].copy()

        if intendencia_grupo_sel == 'ILM':
            df_filt = df_filtered_by_year[df_filtered_by_year['INTENDENCIA'] == 'ILM'].copy()
        elif intendencia_grupo_sel == 'REGIONALES':
            df_filt = df_filtered_by_year[df_filtered_by_year['INTENDENCIA'] != 'ILM'].copy()
        else: # 'TODAS'
            df_filt = df_filtered_by_year.copy()

        if df_filt.empty:
            return fig, []

        fig, total_deriv, total_cobro, prom_eficiencia = crear_grafico_derivaciones_eficiencia(df_filt)

        stats_cards = [
            html.Div(style=card_style, children=[
                html.H4(f"{total_deriv:,.0f}", style={"margin": "0", "fontSize": "36px", "color": "#00FFFF"}),
                html.P(f"Total Derivaciones ({anio_sel})", style={"margin": "5px 0 0 0", "fontSize": "14px"})
            ]),
            html.Div(style=card_style, children=[
                html.H4(f"{total_cobro:,.0f}", style={"margin": "0", "fontSize": "36px", "color": "#FEF7F5"}),
                html.P(f"Total Cobros ({anio_sel})", style={"margin": "5px 0 0 0", "fontSize": "14px"})
            ]),
            html.Div(style=card_style, children=[
                html.H4(f"{prom_eficiencia:.1f}%", style={"margin": "0", "fontSize": "36px", "color": "#00FFFF"}),
                html.P(f"Promedio Eficiencia ({anio_sel})", style={"margin": "5px 0 0 0", "fontSize": "14px"})
            ])
        ]
        return fig, stats_cards