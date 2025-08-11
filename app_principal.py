import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Importa los módulos de los dashboards
import dashboard_derivaciones
import dashboard_eficiencia

# Crea la aplicación principal de Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Dashboard Principal"
server = app.server

# Define el layout principal con pestañas
app.layout = html.Div(style={'backgroundColor': '#2c2c2c'}, children=[
    html.H1('Panel Principal de Cobranza No Coactiva | AEI. 02.03', style={'textAlign': 'center', 'color': '#FFFFFF', 'backgroundColor': '#1a1a1a', 'padding': '20px', 'marginBottom': 0}),
    dcc.Tabs(id="tabs-principal", value='tab-derivaciones', children=[
        dcc.Tab(
            label='Análisis de Derivaciones',
            value='tab-derivaciones',
            style={'color': 'white', 'backgroundColor': '#333333', 'padding': '10px 6px', 'border': '1px solid #2c2c2c'},
            selected_style={'color': '#FFFFFF', 'backgroundColor': '#1a1a1a', 'padding': '10px 6px', 'fontWeight': 'bold', 'border': '1px solid #00FFFF'}
        ),
        dcc.Tab(
            label='Análisis de Eficiencia',
            value='tab-eficiencia',
            style={'color': 'white', 'backgroundColor': '#333333', 'padding': '10px 6px', 'border': '1px solid #2c2c2c'},
            selected_style={'color': 'FFFFFF', 'backgroundColor': '#1a1a1a', 'padding': '10px 6px', 'fontWeight': 'bold', 'border': '1px solid #00FFFF'}
        ),
    ]),
    html.Div(id='contenido-tab', style={'backgroundColor': '#2c2c2c'})
])

# Registra los callbacks de cada dashboard
dashboard_derivaciones.register_callbacks(app)
dashboard_eficiencia.register_callbacks(app)

# Callback para renderizar el contenido de la pestaña seleccionada
@app.callback(Output('contenido-tab', 'children'),
              Input('tabs-principal', 'value'))
def render_content(tab):
    if tab == 'tab-derivaciones':
        return dashboard_derivaciones.get_layout()
    elif tab == 'tab-eficiencia':
        return dashboard_eficiencia.get_layout()

# Ejecuta la aplicación
if __name__ == '__main__':
    app.run(debug=True, port=8050)