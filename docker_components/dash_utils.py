import numpy as np
import pandas as pd
import pickle
import os
import glob
import warnings
warnings.filterwarnings('ignore')

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px

class DashUtils():
    def __init__(self, city_fil):
        self.city_fil = city_fil
        comp_path = os.path.join(os.getcwd(), "dashboard_components")
        self.data_path = os.path.join(comp_path, "data")
        self.image_path = os.path.join(comp_path, "images")
        self.model_path = os.path.join(comp_path, "models")
        self.num_steps = 52
        self.anomaly_per = 25

    def import_data(self):
        self.ts_df = pd.read_csv(os.path.join(self.data_path,"time_series_df.csv"))
        self.ts_df.set_index('date',inplace=True)
        self.ts_df.index = pd.DatetimeIndex(self.ts_df.index)

    def get_city_ts(self):
        self.city_df = self.ts_df.loc[:,self.city_fil].reset_index()
        self.city_df.columns = ['ds','y']

    def get_forecast(self):
        fcast_path = os.path.join(self.data_path, \
                            self.city_fil.lower().replace(' ','_')+'_forecast.csv')
        self.fcast = pd.read_csv(fcast_path)

        self.fcast = self.fcast[['ds','yhat','yhat_lower','yhat_upper']]

    def get_anomalies(self):
        anomaly_path = os.path.join(self.data_path, \
                            self.city_fil.lower().replace(' ','_')+'_anomalies.csv')
        anomaly_df = pd.read_csv(anomaly_path)

        anomaly_df = anomaly_df.sort_values('importance',ascending=False) \
                            [:int((self.anomaly_per/100)*anomaly_df.shape[0])]
        anomaly_df['importance'] = 5 + 15*anomaly_df.importance.rank(pct=True)
        self.anomaly_pos_df = anomaly_df.loc[anomaly_df.anomaly == 1, :].copy()
        self.anomaly_neg_df = anomaly_df.loc[anomaly_df.anomaly == -1, :].copy()

    def generate_forecast_comp(self):
        self.get_city_ts()
        self.get_forecast()
        self.get_anomalies()

    def update_forecast_comp(self):
        actual = go.Scatter(
        x = self.city_df['ds'],
        y = self.city_df['y'],
        mode = 'lines',
        marker = {
            'color': 'RoyalBlue'
        },
        line = {
            'width': 3
        },
        name = 'Actual'
        )

        yhat_lower = go.Scatter(
                x = self.fcast['ds'][:-104*7],
                y = self.fcast['yhat_lower'][:-104*7],
                marker = {
                    'color': 'rgba(0,0,0,0)'
                },
                showlegend = False,
                hoverinfo = 'none',
            )

        yhat_upper = go.Scatter(
                x = self.fcast['ds'][:-104*7],
                y = self.fcast['yhat_upper'][:-104*7],
                fill='tonexty',
                fillcolor = 'LightPink',
                name = 'Confidence',
                hoverinfo = 'none',
                mode = 'none'
            )

        if self.num_steps != 104:
            fcast_df = self.fcast[:-(104-self.num_steps)*7]
        else:
            fcast_df = self.fcast

        yhat = go.Scatter(
        x = fcast_df['ds'],
        y = fcast_df['yhat'],
        mode = 'lines',
        marker = {
            'color': 'Coral',

        },
        line = {
            'width': 3
        },
        name = 'Forecast'
        )

        anomaly_pos = go.Scatter(
            x = self.anomaly_pos_df['ds'],
            y = self.anomaly_pos_df['fact'],
            mode = 'markers',
            marker = {
                'color' : 'MediumSeaGreen',
                'size' : self.anomaly_pos_df.importance,
            },
            name = '+ve Anomaly'

        )

        anomaly_neg = go.Scatter(
            x = self.anomaly_neg_df['ds'],
            y = self.anomaly_neg_df['fact'],
            mode = 'markers',
            marker = {
                'color' : 'IndianRed',
                'size' : self.anomaly_neg_df.importance,
            },
            name = '-ve Anomaly'

        )

        layout = go.Layout(
            yaxis = {
                'title': self.city_fil,
            },
            margin = {
                't': 20,
                'b': 50,
                'l': 60,
                'r': 10
            },
            legend = {
                'bgcolor': 'White'
            }
        )

        data = [yhat_lower, yhat_upper, yhat, actual, anomaly_neg, anomaly_pos]

        fig = go.Figure(dict(data = data, layout = layout))

        return fig