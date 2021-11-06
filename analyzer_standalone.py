import seaborn as sns
import pandas as pd
import numpy as np
import pandas_datareader as dr
import matplotlib.pyplot as plt

from pandas.plotting import register_matplotlib_converters
from scipy.stats import norm
from scipy import stats
from datetime import date

plt.style.use('seaborn-darkgrid')

ticker_symbol = 'SPY'
from_date = '2000-01-01'
to_date = date.today()
df = dr.data.get_data_yahoo(ticker_symbol, start=from_date, end=to_date)

df = df[~df.index.duplicated()]
print("Últimos valores del DataFrame sin duplicados:", df.tail(), sep='\n')

df['Daily Return'] = df['Adj Close'].pct_change()
df['Daily Return (%)'] = df['Daily Return'] * 100
print("Últimos valores del DataFrame incluyendo la tasa de cambio (aritmética y porcentual):", df.tail(), sep='\n')

df = df.iloc[1:]

plt.figure(figsize=(15, 8))
sns.set(color_codes=True)
ax = sns.displot(df['Daily Return'], bins=100, kde=False, hue_norm=stats.norm, color='green')

(mu, sigma) = stats.norm.fit(df['Daily Return'])

plt.title("Distribución Histórica de los Retornos Diarios", fontsize=16)
plt.ylabel("Frecuencia")
plt.legend(["Distr. normal. fit ($\\mu=${0:.2g}, $\\sigma=${1:.2f})".format(mu, sigma), "Distr. R. Aritméticos"])

# Calculamos la Tasa de Crecimiento Anual Compuesto (conocido como CAGR, del inglés).

years = len(df) / 252
cagr = (df['Adj Close'].iloc[-1] / df['Adj Close'].iloc[0]) ** (1 / years) - 1
print("> Tasa de Crecimiento Anual Compuesto (CAGR):", '%.6s' % (100 * cagr), "%")

# Calculamos el resultado de comprar y mantener.

buy_and_hold_return = ((df['Adj Close'].iloc[-1] - df['Adj Close'].iloc[0]) / df['Adj Close'].iloc[0]) * 100
print("> Buy & Hold:", '%.6s' % buy_and_hold_return, "%")

# Calculamos el Máximo Drawdown.

previous_max = df['Adj Close'].cummax()
drawdowns = ((df['Adj Close'] - previous_max) / previous_max) * 100
DD = pd.DataFrame({'Adj Close': df['Adj Close'], 'Previous Peak': previous_max, 'Drawdown': drawdowns})
print("> Máximo Drawdown Histórico:", '%.6s' % np.min(DD['Drawdown']), "%")

# Obtenemos el promedio, desviación típica, máximo y mínimo valor y número de datos analizados:

print("> Media Diaria:", '%.6s' % (df['Daily Return'].mean() * 100), "%")
print("> Desviación Típica Diaria:", '%.6s' % (df['Daily Return'].std(ddof=1) * 100), "%")
print("> Máxima Pérdida Diaria:", '%.6s' % (df['Daily Return'].min() * 100), "%")
print("> Máximo Beneficio Diario:", '%.6s' % (df['Daily Return'].max() * 100), "%")
print("> Días Analizados:", '%.6s' % df['Daily Return'].count())
print(">--------------------------------------------------")

# Coeficiente de asimetría y curtosis de la distribución.

print("> Coeficiente de Asimetría:", '%.6s' % df['Daily Return'].skew())
print("> Curtosis:", '%.6s' % df['Daily Return'].kurt())
print(">--------------------------------------------------")

# VaR Teórico obtenido a través de la distribución normal al 95% y 99% de confianza.

print("> VaR Modelo Gaussiano NC-95% :", '%.6s' % (norm.ppf(0.05, mu, sigma) * 100), "%")
print("> VaR Modelo Gaussiano NC-99% :", '%.6s' % (norm.ppf(0.01, mu, sigma) * 100), "%")
print("> VaR Modelo Gaussiano NC-99.7% :", '%.6s' % (norm.ppf(0.003, mu, sigma) * 100), "%")

# VaR histórico al 95% y 99% de confianza.

print("> VaR Modelo Histórico NC-95% :", '%.6s' % (100 * np.percentile(df['Daily Return'], 5)), "%")
print("> VaR Modelo Histórico NC-99% :", '%.6s' % (100 * np.percentile(df['Daily Return'], 1)), "%")
print("> VaR Modelo Histórico NC-99.7% :", '%.6s' % (100 * np.percentile(df['Daily Return'], .3)), "%")
print(">--------------------------------------------------")

# Registramos Matplotlib converters para adatpar la fecha -DateTime- al método de dibujo de Matplotlib

register_matplotlib_converters()

# Calculamos la volatilidad histórica de 14 días, la volatilidad anualizada y su SMA de 252 días.

df['Vol. Historica 14 Dias'] = df['Daily Return'].rolling(14).std() * 100
df['Vol. Anualizada'] = df['Vol. Historica 14 Dias'] * (252 ** 0.5)
df['SMA 126 Vol. Anualizada'] = df['Vol. Anualizada'].rolling(126).mean()

# Creamos un gráfico en el que mostramos el precio de cierre, la volatilidad anualizada y su SMA.

fig, ax1 = plt.subplots(figsize=(15, 8))
ax2 = ax1.twinx()
ax1.plot(df['Vol. Anualizada'], 'orange', linestyle='--')
ax1.plot(df['SMA 126 Vol. Anualizada'], 'green', linestyle='-')
ax2.plot(df['Adj Close'], 'black')

# Asignamos un nombre para el gráfico y para los ejes X e Y.

plt.title("Evolución Histórica del Precio y la Volatilidad", fontsize=16)
ax1.set_xlabel("Fecha")
ax1.set_ylabel("Volatilidad Anualizada", color='black')
ax2.set_ylabel("Precio de Cierre", color='black')

# Configuramos la leyenda, las líneas de cuadrícula y mostramos el gráfico.

ax1.legend(loc='upper left', frameon=True, borderpad=1)
ax1.grid(True)
ax2.grid(False)
plt.show()

# Volatilidad anualizada.

VAM = df['Daily Return'].std() * 100 * (252 ** 0.5)
print("> Volatilidad Anualizada:", '%.6s' % VAM, "%")

# Obtenemos el valor mínimo y máximo de la volatilidad anualizada
# así como las fechas en las que ambos valores son producidos.

min_vol_date = df['Vol. Anualizada'].idxmin().strftime('%Y-%m-%d')
max_vol_date = df['Vol. Anualizada'].idxmax().strftime('%Y-%m-%d')

print("> La Mínima Vol. Anualizada fue de", '%.6s' % (df['Vol. Anualizada'].min()), "%", "registrada el", min_vol_date)
print("> La Máxima Vol. Anualizada fue de", '%.6s' % (df['Vol. Anualizada'].max()), "%", "registrada el", max_vol_date)

# Obtenemos el promedio sobre el rango porcentual de los días negativos.

df['Negative Days'] = np.where(df['Daily Return'] < 0, 100 * (df['High'] - df['Low']) / df['Low'], 0)
df_negative_days = df.loc[df['Negative Days'] != 0]
ND = df_negative_days['Negative Days'].mean()
print("> Rango Medio en los días negativos:", '%.4s' % ND, "%")

# Obtenemos el promedio del rango porcentual de los días positivos.

df['Positive Days'] = np.where(df['Daily Return'] > 0, 100 * (df['High'] - df['Low']) / df['Low'], 0)
df_positive_days = df.loc[df['Positive Days'] != 0]
PD = df_positive_days['Positive Days'].mean()
print("> Rango Medio en los días positivos:", '%.4s' % PD, "%")

# Calculamos el ratio del rango entre días negativos (RDN) y positivos (RDP).

print("> Ratio RDN/RDP", '%.4s' % (ND / PD), "%")
