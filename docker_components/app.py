import numpy as np
import pandas as pd
import pickle
import os
import glob
import base64
import warnings
warnings.filterwarnings('ignore')

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px

from dash_utils import DashUtils

def generate_dashboard_components(du):
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    server = app.server

    # app layout configuration
    # Navigation bar
    logo_path = os.path.join(du.image_path,'yelp_logo.png')
    encoded_image = base64.b64encode(open(logo_path, 'rb').read())

    NAVBAR = dbc.Navbar(
        children=[
            # html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), height="30px"),
                            md=1,
                        ),
                        dbc.Col(
                            dbc.NavbarBrand("YELP Merchant Insights Dashboard", className="ml-2")
                        ),
                    ],
                    align="center",
                    no_gutters=True,
                ),
                # href="https://plot.ly",
            # )
        ],
        color="dark",
        dark=True,
        sticky="top",
    )

    # time series forecasting and anomaly detection component
    TS_FORECAST = [
        dbc.CardHeader(html.H5("Demand Forecast with anomalies")),
        dbc.CardBody(
            [
                dcc.Loading(
                    id="loading-forecast-comps",
                    children=[
                        dbc.Alert(
                            "Something's gone wrong! Give us a moment, but try loading this page again if problem persists.",
                            id="no-data-alert-forecast-comps",
                            color="warning",
                            style={"display": "none"},
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.P("Choose the city and number of forecast steps:"),
                                    md=12,
                                    ),
                                dbc.Col(
                                    [
                                        html.Label('City:'),
                                        dcc.Dropdown(
                                            id="city-dropdown",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in du.ts_df.columns
                                            ],
                                            value=du.city_fil,
                                        )
                                    ],
                                    md=4,
                                ),
                                dbc.Col(
                                    [
                                        html.Label('No. weeks to forecast:'),
                                        dcc.Slider(
                                            id="forecast-slider",
                                            min=26,
                                            max=104,
                                            step=26,
                                            value=52,
                                            marks={
                                                26: '26',
                                                52: '52',
                                                78: '78',
                                                104: '104'
                                                })
                                    ],
                                    md=4,
                                ),
                                dbc.Col(
                                    [
                                        html.Label('% of anomalies:'),
                                        dcc.Slider(
                                            id="anomaly-slider",
                                            min=25,
                                            max=100,
                                            step=25,
                                            value=25,
                                            marks={
                                                25: '25%',
                                                50: '50%',
                                                75: '75%',
                                                100: '100%'
                                                })
                                    ],
                                    md=4,
                                ),
                            ]
                        ),
                        dcc.Graph(
                            id='city-forecast',
                        ),
            ],
            type='default',)
            ],
            style={"marginTop": 0, "marginBottom": 0},
        ),
    ]

    # body layout
    BODY = dbc.Container(
        [
            dbc.Row([
                    dbc.Col(dbc.Card(TS_FORECAST))
                    ],
                    style={"marginTop": 30},
                ),
        ],
        className='mt-12',
    )

    # defining dashboard app layout
    app.layout = html.Div(children=[NAVBAR, BODY])
    
    # app callback functions
    # updating forecast component
    @app.callback(
        Output('city-forecast', 'figure'),
        [Input('city-dropdown', 'value'),
        Input('forecast-slider', 'value'),
        Input('anomaly-slider', 'value'),]
    )
    def update_business(input_city, num_steps, anomaly_per):
        ctx = dash.callback_context
        prop = ctx.triggered[0]['prop_id'].split('.')[0]
        if prop == 'forecast-slider':
            du.num_steps = num_steps
            du.get_forecast()
            return du.update_forecast_comp()
        elif prop == 'anomaly-slider':
            du.anomaly_per = anomaly_per
            du.get_anomalies()
            return du.update_forecast_comp()
        else:
            du.city_fil = input_city
            du.generate_forecast_comp()
            return du.update_forecast_comp()
    
    return app

if __name__ == '__main__':
    du = DashUtils("Toronto")
    du.import_data()
    app = generate_dashboard_components(du)
    app.run_server(host='0.0.0.0', debug=True, port=8050, use_reloader=False)