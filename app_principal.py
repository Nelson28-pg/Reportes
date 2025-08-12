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
app.layout = html.Div(style={'backgroundColor': '#2c2c2c', 'margin': '0px', 'padding': '0px', 'height': '100vh'}, children=[
        html.H1('Panel de Cobranza No Coactiva', style={"fontFamily": "'Roboto', serif", 'textAlign': 'center', 'color': '#FFFFFF', 'backgroundColor': '#1a1a1a', 'padding': '25px', 'marginBottom': 0, 'marginTop': '0px'}),
    dcc.Tabs(id="tabs-principal", value='tab-derivaciones', children=[
        dcc.Tab(
            label=' | EEM Derivados y Cancelados |',
            value='tab-derivaciones',
            style={'color': 'white', 'backgroundColor': '#2c2c2c', 'padding': '10px 6px', 'border': '1px solid #2c2c2c', 'borderRadius': '1px'},
            selected_style={'color': '#FFFFFF', 'backgroundColor': '#1a1a1a', 'padding': '10px 6px', 'fontWeight': 'bold', 'border': '1px solid #00FFFF', 'borderRadius': '18px'}
        ),
        dcc.Tab(
            label='| Eficiencia de Cobranza |',
            value='tab-eficiencia',
            style={'color': 'white', 'backgroundColor': '#2c2c2c', 'padding': '10px 6px', 'border': '1px solid #2c2c2c', 'borderRadius': '1px'},
            selected_style={'color': 'FFFFFF', 'backgroundColor': '#1a1a1a', 'padding': '10px 6px', 'fontWeight': 'bold', 'border': '1px solid #00FFFF', 'borderRadius': '18px'}
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