import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import dcc, html, Input, Output
import os

# =============================================
# FUNCIÓN PARA LEER ARCHIVO
# =============================================
def leer_archivo(ruta_csv):
    df = pd.read_csv(ruta_csv, sep=';', encoding='latin1')
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'AÑO': 'ANIO'})

    if 'EFICIENCIA' in df.columns:
        df['EFICIENCIA'] = pd.to_numeric(df['EFICIENCIA'].astype(str).str.replace(',', '.', regex=False), errors='coerce')
    else:
        df['EFICIENCIA'] = 1.0

    df['EFICIENCIA'] = df['EFICIENCIA'].fillna(0)
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
    return df_historico, df_2025, anios_filtrables

# =============================================
# SECCIÓN DE ESTÉTICA DE GRÁFICOS
# =============================================
def crear_heatmap(df_grupo, df_2025_grupo, titulo, color_scale_2025, color_scale_prom, color_scale_hist):
    if df_grupo.empty:
        fig = go.Figure()
        fig.update_layout(title=f'{titulo} (Sin datos)', paper_bgcolor="#2c2c2c", plot_bgcolor="#2c2c2c", font_color="white")
        return fig

    pivot_historico = df_grupo.pivot_table(index="INTENDENCIA", columns="ANIO", values="EFICIENCIA", fill_value=0)
    prom_anios_ant = pivot_historico.mean(axis=1).to_frame(name='Prom. Años Anteriores')
    df_2025_grupo = df_2025_grupo.set_index('INTENDENCIA')[['EFICIENCIA']].rename(columns={'EFICIENCIA': 2025})
    df_final = prom_anios_ant.join(df_2025_grupo, how='left').fillna(0)
    orden_intendencias = df_final.sort_values(2025, ascending=True).index
    pivot_historico = pivot_historico.reindex(orden_intendencias).dropna(how='all')
    df_final = df_final.reindex(orden_intendencias).dropna(how='all')

    fig = make_subplots(
        rows=1, cols=3,
        column_widths=[0.6, 0.15, 0.15],
        horizontal_spacing=0.05,
        shared_yaxes=True
    )

    fig.add_trace(go.Heatmap(
        z=pivot_historico.values,
        x=pivot_historico.columns.astype(str),
        y=pivot_historico.index,
        colorscale=color_scale_hist, showscale=False,
        text=pivot_historico.applymap(lambda x: f'{x:.1f}'),
        texttemplate="%{text}",
        textfont=dict(size=9, color='rgba(255, 255, 255, 0.8)'),
        hovertemplate="<b>%{y}</b><br>Año: %{x}<br>Eficiencia: %{z:.1f}<extra></extra>",
        xgap=1.8, ygap=1.8
    ), row=1, col=1)

    fig.add_trace(go.Heatmap(
        z=df_final[['Prom. Años Anteriores']].values,
        x=['Prom. Años Anteriores'], y=df_final.index,
        colorscale=color_scale_prom, showscale=False,
        text=df_final[['Prom. Años Anteriores']].applymap(lambda x: f'<b>{x:.1f}</b>'),
        texttemplate="%{text}", textfont=dict(size=9, color="white"),
        hovertemplate="%{z:.1f}<extra></extra>",
        xgap=1.8, ygap=1.8
    ), row=1, col=2)

    fig.add_trace(go.Heatmap(
        z=df_final[[2025]].values,
        x=['2025'], y=df_final.index,
        colorscale=color_scale_2025, showscale=False,
        text=df_final[[2025]].applymap(lambda x: f'<b>{x:.1f}</b>'),
        texttemplate="%{text}", textfont=dict(size=11, color="white"),
        hovertemplate="%{z:.1f}<extra></extra>",
        xgap=1.8, ygap=1.8
    ), row=1, col=3)

    fig.update_layout(
        title={'text': titulo, 'x': 0.05, 'xanchor': 'left', 'font': {'size': 16, 'color': 'white'}},
        paper_bgcolor="#2c2c2c", plot_bgcolor='rgba(0,0,0,0)', font_color="white",
        height=max(300, len(df_final.index) * 40 + 120),
        margin=dict(l=120, r=100, t=140, b=80), showlegend=False
    )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    return fig

# =============================================
# CARGAR DATOS INICIALES
# =============================================
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "Eficiencia_cobranzaNC_2020-2025.csv")
    df_historico, df_2025, anios_filtrables = cargar_y_procesar_datos(csv_path)
    
    df_linea_base_source = df_historico[df_historico['ANIO'].between(2020, 2024)]
    pivot_linea_base = df_linea_base_source.pivot_table(index='INTENDENCIA', columns='ANIO', values='EFICIENCIA', fill_value=0)
    linea_base_global = pivot_linea_base.values.mean()

except Exception as e:
    print(f"Error al cargar datos en dashboard_eficiencia: {e}")
    df_historico, df_2025, anios_filtrables = pd.DataFrame(), pd.DataFrame(), []
    linea_base_global = 0

# =============================================
# ESTILOS
# =============================================
card_style = {
    'backgroundColor': '#333333',
    'padding': '20px',
    'borderRadius': '10px',
    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.4)',
    'textAlign': 'center',
    'flex': '1',
    'margin': '0 10px'
}

# =============================================
# LAYOUT DE LA APLICACIÓN
# =============================================
def get_layout():
    layout = html.Div(
        style={
            "backgroundColor": "#2c2c2c", 
            "color": "white", 
            "padding": "20px", 
            "fontFamily": "Arial, sans-serif",
            "minHeight": "100vh"
        },
        children=[
            html.Div(
                style={
                    "backgroundColor": "#1a1a1a", 
                    "padding": "20px", 
                    "borderRadius": "10px",
                    "marginBottom": "25px",
                    "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.3)"
                },
                children=[
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "gap": "15px"},
                        children=[
                            html.Label(
                                "Seleccionar Año(s) Históricos:", 
                                style={
                                    "marginBottom": "0", 
                                    "fontSize": "16px",
                                    "fontWeight": "500"
                                }
                            ),
                            dcc.Dropdown(
                                id="filtro-anio",
                                options=[{"label": str(a), "value": a} for a in anios_filtrables],
                                multi=True,
                                value=anios_filtrables,
                                style={
                                    "color": "#000", 
                                    "backgroundColor": "white",
                                    "minWidth": "300px",
                                    "flex": "1"
                                }
                            )
                        ]
                    )
                ]
            ),
            
            html.Div(
                id="stats-panel",
                style={
                    "display": "flex",
                    "justifyContent": "center",
                    "alignItems": "stretch",
                    "marginBottom": "25px"
                },
                children=[
                    html.Div(style=card_style, children=[
                        html.H4(f"{linea_base_global:.1f}%", id="linea-base-general", style={"margin": "0", "fontSize": "36px", "color": "#00FFFF"}),
                        html.P("Linea Base (Prom. 2020-2024)", style={"margin": "5px 0 0 0", "fontSize": "14px"})
                    ]),
                    html.Div(style=card_style, children=[
                        html.H4(id="anios-datos", style={"margin": "0", "fontSize": "36px", "color": "#E2EEF9"}),
                        html.P("Años de Datos Seleccionados", style={"margin": "5px 0 0 0", "fontSize": "14px"})
                    ]),
                    html.Div(style=card_style, children=[
                        html.H4(id="num-intendencias", style={"margin": "0", "fontSize": "36px", "color": "#00FFFF"}),
                        html.P("Intendencias Mostradas", style={"margin": "5px 0 0 0", "fontSize": "14px"})
                    ])
                ]
            ),
            
            html.Div(id="error-panel", style={"display": "none"}),
            
            dcc.Graph(id="heatmap-arriba"),
            dcc.Graph(id="heatmap-abajo")
        ]
    )
    return layout

# =============================================
# CALLBACKS
# =============================================
def register_callbacks(app):
    @app.callback(
        [Output("heatmap-arriba", "figure"),
         Output("heatmap-abajo", "figure"),
         Output("anios-datos", "children"),
         Output("num-intendencias", "children"),
         Output("error-panel", "children"),
         Output("error-panel", "style")],
        [Input("filtro-anio", "value")]
    )
    def actualizar_graficos(anios_sel):
        error_content = []
        error_style = {"display": "none"}

        try:
            if not anios_sel:
                df_filt = df_historico.copy()
                anios_sel = anios_filtrables
            else:
                df_filt = df_historico[df_historico["ANIO"].isin(anios_sel)].copy()

            if df_filt.empty:
                raise ValueError("No hay datos históricos para los años seleccionados.")

            df_merged = df_filt.merge(df_2025[['INTENDENCIA', 'EFICIENCIA']], on='INTENDENCIA', how='left', suffixes=['_', '_2025'])
            df_merged['EFICIENCIA_2025'] = df_merged['EFICIENCIA_2025'].fillna(0)

            intendencias_arriba = df_merged[df_merged['EFICIENCIA_2025'] >= linea_base_global]['INTENDENCIA'].unique()
            intendencias_abajo = df_merged[df_merged['EFICIENCIA_2025'] < linea_base_global]['INTENDENCIA'].unique()

            df_arriba = df_filt[df_filt['INTENDENCIA'].isin(intendencias_arriba)]
            df_abajo = df_filt[df_filt['INTENDENCIA'].isin(intendencias_abajo)]
            
            df_2025_arriba = df_2025[df_2025['INTENDENCIA'].isin(intendencias_arriba)]
            df_2025_abajo = df_2025[df_2025['INTENDENCIA'].isin(intendencias_abajo)]

            color_verde_intenso = [[0, "#4CAF50"], [1, "#1a4d1a"]]
            color_verde_medio = [[0, "#66CDAA"], [1, "#2E8B57"]]
            color_verde_suave = [[0, "#98FB98"], [1, "#558255"]]

            color_rojo_intenso = [[0, "#F44336"], [1, "#4d1a1a"]]
            color_rojo_medio = [[0, "#E9967A"], [1, "#8A3232"]]
            color_rojo_suave = [[0, "#E9967A"], [1, "#9F3E3E"]]

            fig_arriba = crear_heatmap(df_arriba, df_2025_arriba, f"<b>Intendencias con Eficiencia 2025 ≥ {linea_base_global:.1f}%</b>", color_verde_intenso, color_verde_medio, color_verde_suave)
            fig_abajo = crear_heatmap(df_abajo, df_2025_abajo, f"<b>Intendencias con Eficiencia 2025 < {linea_base_global:.1f}%</b>", color_rojo_intenso, color_rojo_medio, color_rojo_suave)
            
            anios_datos_text = f"{min(anios_sel)} - {max(anios_sel)}"
            num_intendencias_text = len(df_merged['INTENDENCIA'].unique())

            return fig_arriba, fig_abajo, anios_datos_text, num_intendencias_text, error_content, error_style

        except Exception as e:
            error_style = {"backgroundColor": "#ff4d4d", "color": "white", "padding": "15px", "borderRadius": "5px", "margin": "10px 0", "display": "block"}
            error_content = [html.H3("Error", style={"color": "white"}), html.P(str(e))]
            fig_empty = go.Figure().update_layout(paper_bgcolor="#2c2c2c", plot_bgcolor="#2c2c2c")
            return fig_empty, fig_empty, "-", "-", error_content, error_style
