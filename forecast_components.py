import pandas as pd, numpy as np
import unidecode
import os, glob
import pickle
import warnings
warnings.filterwarnings('ignore')
from fbprophet import Prophet

class FcastComps():
    model_path = os.path.join(os.getcwd(), 'dashboard_components', 'models')
    data_path = os.path.join(os.getcwd(), 'dashboard_components', 'data')

    def save_ts_data(self):
        # read checkin dataset 
        check_df = pd.concat([pd.read_parquet(f) for f in glob.glob(os.getcwd() \
                            +'\\filtered_data\\checkin\\*.parquet')], ignore_index=True)
        check_df['date'] = check_df.date.apply(lambda x: x.split(','))
        check_df = check_df.explode('date').reset_index().drop('index',axis=1)
        check_df['date'] = pd.to_datetime(check_df.date)

        # read business dataset 
        bus_df = pd.concat([pd.read_parquet(f) for f in glob.glob(os.getcwd() \
                            +'\\filtered_data\\business\*.parquet')], ignore_index=True)

        bus_df['city'] = bus_df.city.apply(lambda x: unidecode.unidecode(x))
        bus_df['state'] = np.select(
            [
                bus_df['city'].isin(['Toronto', 'Richmond Hill', 'Scarborough', 'Markham', 'Mississauga', 'Brampton', 'Vaughan', 'North York']),
                bus_df['city'].isin(['Calgary']),
                bus_df['city'].isin(['Montreal']),
            ],
            [
                'ON',
                'AB',
                'QC'
            ]
        )

        # merge and pivot ts data
        df = bus_df[['business_id','city']].merge(check_df,on=['business_id'],how='inner')
        df['city'] = df.city.astype('category')
        df['date'] = df.date.dt.date

        self.pivot_df = df.pivot_table(index='date',values='business_id',columns='city',aggfunc='count', fill_value=0)
        self.pivot_df.index = pd.DatetimeIndex(self.pivot_df.index)
        
        # creating directory and saving df
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
        self.pivot_df.to_csv(os.path.join(self.data_path,'time_series_df.csv'))

    def save_prophet_model(self, city_sel):
        df = self.pivot_df.loc[:,city_sel].resample('D').sum().reset_index() \
                .rename(columns={'date':'ds',city_sel:'y'}).copy()
        
        # defining prophet model parameters and fitting the time series
        self.model = Prophet(interval_width=0.95,
                seasonality_mode='multiplicative', # trend seems to have an impact on seasonal growth
                yearly_seasonality=False,
                weekly_seasonality=False,
                daily_seasonality=False,
                ).add_country_holidays(
                    country_name='CA' # adding canadian holidays
                ).add_seasonality(
                    name='weekly',
                    period=7,
                    fourier_order=20
                ).add_seasonality(
                    name='yearly',
                    period=365.25,
                    fourier_order=20
                ).fit(df)

        # creating directory
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)

        # saving model weights
        pkl_path = os.path.join(self.model_path,city_sel.lower().replace(" ","_")+"_prophet.pkl")
        with open(pkl_path, "wb") as f:
            pickle.dump(self.model, f)
    
    def save_anomalies(self, city_sel):
        """
        - function to detect anomalies and estimate their importance
        - data points where the fact is outside the 95% confidence interval of the predictions are considered to be anomalies
        - anomaly importance is determined by how far the fact is from the boundary 
        """
        # making dataframe for prediction
        model_pd = self.model.make_future_dataframe(
        periods=0, 
        freq='D', 
        include_history=True
        )

        # getting model predictions
        pred = self.model.predict(model_pd)
        pred['fact'] = self.pivot_df[city_sel].values

        pred = pred[['ds','trend', 'yhat', 'yhat_lower', 'yhat_upper', 'fact']].copy()

        # detecting anomalies
        pred['anomaly'] = 0
        pred.loc[pred['fact'] > pred['yhat_upper'], 'anomaly'] = 1
        pred.loc[pred['fact'] < pred['yhat_lower'], 'anomaly'] = -1

        # anomaly importances
        pred['importance'] = 0
        pred.loc[pred['anomaly'] == 1, 'importance'] = \
                    (pred['fact'] - pred['yhat_upper'])
        pred.loc[pred['anomaly'] == -1, 'importance'] = \
                    (pred['yhat_lower'] - pred['fact'])
        
        # filtering anomalies
        anomaly_df = pred.loc[pred.anomaly!=0,:].copy()

        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
        anomaly_df.to_csv(os.path.join(self.data_path,city_sel.lower().replace(" ","_")+'_anomalies.csv'))

if __name__ == '__main__':
    fcast_comps = FcastComps()
    fcast_comps.save_ts_data()
    for city in fcast_comps.pivot_df.columns:
        fcast_comps.save_prophet_model(city)
        fcast_comps.save_anomalies(city)
