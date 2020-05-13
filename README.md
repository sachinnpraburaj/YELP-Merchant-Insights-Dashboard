# YELP Merchant dashboard

- Developing a dashboard for YELP merchants using insights generated from big data analytics, machine learning and deep learning techniques

- The unique value of the product is to perform time series forecasting and anomaly detection on daily checkins of YELP businesses and to provide additional insights for anomalies using NLP techniques on user reviews 

- The YELP dataset was used for the goals of this project. Link to dataset:
https://www.kaggle.com/yelp-dataset/yelp-dataset

- To explore the data science techniques involved in the making of the project, take a look at the following notebooks
    - [Time series forecasting using ARIMA, Seasonal ARIMA, SARIMA with exogenous variables and Prophet] (time_series_forecasting.ipynb)
    - [Time series forecasting with Tensorflow using Deep Neural Network] (time_series_forecasting_DNN.ipynb)
    - [Time series forecasting with Tensorflow using Recurrent Neural Network] (time_series_forecasting_RNN.ipynb) - *In Progress*


## Project achievements

-  Explored multiple forecasting techniques - ARIMA, SARIMA, SARIMAX, Prophet and Recurrent Neural Network, and tested them to find best performing forecasting technique

## Instructions

### downloading 
- Setup kaggle on local system and download the dataset using

```
kaggle datasets download -d yelp-dataset/yelp-dataset -p /data
```
- Extract the files into '[data](data)' folder
- For documentation of the data, visit:
https://www.yelp.com/dataset/documentation/main
## Project steps with logic

### dataset filter: [filter_dataset.ipynb](filter_dataset.ipynb)
- Filtered the datasets using PySpark to contain only businesses from Top 10 Canadian cities with most number business checkins
- Dataset does not have a 'Country Code' to identify Canadian cities, so explored postal codes and identified codes of lengths 3,6,7 to be Canadian and filtered them
- Number of records in the filtered dataset can be found in the notebook
- Datasets are stored in a distributed format as parquet outputs

### time_series_forecasting: [time_series_forecasting.ipynb](time_series_forecasting.ipynb), [time_series_forecasting_DNN.ipynb](time_series_forecasting_DNN.ipynb), [time_series_forecasting_RNN.ipynb](time_series_forecasting_RNN.ipynb)
-

![](/images/time_series_forecasting.png)

![](/images/time_series_forecasting_DNN.png)
