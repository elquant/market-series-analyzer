import numpy as np
import pandas as pd
import pandas_datareader as dr

from scipy.stats import norm
from scipy import stats


class TimeSerieAnalyzer:

    def __init__(self, ticker_symbol, from_date, to_date):
        self._ticker_symbol = ticker_symbol
        self._from_date = from_date
        self._to_date = to_date
        self.perform_analysis()

    def perform_analysis(self):
        df = dr.data.get_data_yahoo(self._ticker_symbol, start=self._from_date, end=self._to_date)
        df = df[~df.index.duplicated()]
        df["Daily Return"] = df["Adj Close"].pct_change()
        df = df.iloc[1:]
        
        years = df["Daily Return"].count() / 252
        self._cagr = ((df['Adj Close'].iloc[-1] / df['Adj Close'].iloc[0]) ** (1 / years) - 1) * 100
        self._buy_and_hold_return = ((df['Adj Close'].iloc[-1] - df['Adj Close'].iloc[0]) / df['Adj Close'].iloc[0]) * 100

        previous_maximum = df["Adj Close"].cummax()
        drawdowns = ((df["Adj Close"] - previous_maximum) / previous_maximum) * 100
        DD = pd.DataFrame({"Adj Close": df["Adj Close"], "Previous Peak": previous_maximum, "Drawdown": drawdowns})
        self._max_dd = np.min(DD['Drawdown'])

        self._mean_daily_return = df["Daily Return"].mean() * 100
        self._std_daily_return = df["Daily Return"].std(ddof=1) * 100
        self._min_return = df["Daily Return"].min() * 100
        self._max_return = df["Daily Return"].max() * 100
        self._trading_days = df["Daily Return"].count()

        self._skewness = df["Daily Return"].skew()
        self._kurtosis = df["Daily Return"].kurt()

        (mu, sigma) = stats.norm.fit(df['Daily Return'])
        self._var_gauss_95 = norm.ppf(0.05, mu, sigma) * 100
        self._var_gauss_99 = norm.ppf(0.01, mu, sigma) * 100
        self._var_gauss_99_7 = norm.ppf(0.003, mu, sigma) * 100

        self._var_historic_95 = np.percentile(df["Daily Return"], 5) * 100
        self._var_historic_99 = np.percentile(df["Daily Return"], 1) * 100
        self._var_historic_99_7 = np.percentile(df["Daily Return"], .3) * 100

        df['Volatilidad_Historica_14_Dias'] = df["Daily Return"].rolling(14).std() * 100
        df['Volatilidad_14_Dias_Anualizada'] = df['Volatilidad_Historica_14_Dias'] * (252 ** 0.5)
        df['SMA_126_Volatilidad_Anualizada'] = df['Volatilidad_14_Dias_Anualizada'].rolling(126).mean()

        self._VAM = df["Daily Return"].std() * 100 * (252 ** 0.5)

        df['DiasNegativos'] = np.where(df['Daily Return'] < 0, 100*(df['High']-df['Low'])/df['Low'], 0)
        df_dias_negativos = df.loc[df['DiasNegativos'] != 0]
        self._DN = df_dias_negativos['DiasNegativos'].mean()

        df['DiasPositivos'] = np.where(df['Daily Return'] > 0, 100*(df['High']-df['Low'])/df['Low'], 0)
        df_dias_positivos = df.loc[df['DiasPositivos'] != 0]
        self._DP = df_dias_positivos['DiasPositivos'].mean()

        self._data = df
    
    def pos_neg_days_ratio(self):
        return self._DN / self._DP

    def daily_return(self):
        return self._data['Daily Return']

    def count(self):
        return len(self._data)

    def index(self):
        return self._data.index
    
    def adj_close(self):
        return self._data['Adj Close']
    
    def historic_vol_14_days(self):
        return self._data['Volatilidad_Historica_14_Dias']
    
    def historic_vol_14_days_annualized(self):
        return self._data['Volatilidad_14_Dias_Anualizada']

    def historic_vol_sma_126(self):
        return self._data['SMA_126_Volatilidad_Anualizada']

    def min_vol_date(self):
        return self._data.Volatilidad_14_Dias_Anualizada[self._data.Volatilidad_14_Dias_Anualizada == self._data['Volatilidad_14_Dias_Anualizada'].min()].index.strftime('%Y-%m-%d').tolist()[0]

    def max_vol_date(self):
        return self._data.Volatilidad_14_Dias_Anualizada[self._data.Volatilidad_14_Dias_Anualizada == self._data['Volatilidad_14_Dias_Anualizada'].max()].index.strftime('%Y-%m-%d').tolist()[0]