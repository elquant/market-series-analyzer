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
from_date = '1993-02-01'
to_date = date.today()
df = dr.data.get_data_yahoo(ticker_symbol, start=from_date, end=to_date)

df = df[~df.index.duplicated()]
df.tail()

df["Daily Return"] = df["Adj Close"].pct_change()
df.tail()

df = df.iloc[1:]

plt.figure(figsize=(15, 8))
sns.set(color_codes=True)
ax = sns.distplot(df['Daily Return'], bins=100, kde=False, fit=stats.norm, color='green')

(mu, sigma) = stats.norm.fit(df['Daily Return'])

plt.title('Distribución Histórica de Retornos Diarios', fontsize=16)
plt.ylabel('Frecuencia')
plt.legend(["Distribución normal. fit ($\mu=${0:.2g}, $\sigma=${1:.2f})".format(mu, sigma), "Distribución R. Aritmeticos"])

# Calculamos la Tasa de Crecimiento Anual Compuesto y el resultado de Comprar y mantener.
years = df["Daily Return"].count() / 252
cagr = (df['Adj Close'].iloc[-1] / df['Adj Close'].iloc[0]) ** (1 / years) - 1
print('> Tasa de Crecimiento Anual Compuesto:', '%.6s' % (100 * cagr), '%')
print('> Buy & Hold:', '%.6s' % (100 * ((df['Adj Close'].iloc[-1] - df['Adj Close'].iloc[0]) / df['Adj Close'].iloc[0])), '%')

# Calculamos el Máximo Drawdown.
Maximo_Anterior = df["Adj Close"].cummax()
drawdowns = 100*((df["Adj Close"] - Maximo_Anterior)/Maximo_Anterior)
DD = pd.DataFrame({"Adj Close": df["Adj Close"], "Previous Peak": Maximo_Anterior, "Drawdown": drawdowns})
print('> Máximo Drawdown Histórico:', '%.6s' % np.min(DD['Drawdown']), '%')

# Obtenemos el promedio, desviación típica, máximo y mínimo valor y número de datos analizados:
print('> Media Diaria:', '%.6s' % (100 * df["Daily Return"].mean()), '%')
print('> Desviación Típica Diaria:', '%.6s' % (100 * df["Daily Return"].std(ddof=1)), '%')
print('> Máxima Pérdida Diaria:', '%.6s' % (100 * df["Daily Return"].min()), '%')
print('> Máximo Beneficio Diario:', '%.6s' % (100 * df["Daily Return"].max()), '%')
print('> Dias Analizados:', '%.6s' % df["Daily Return"].count())
print('<-------------------------------------------------->')

# Coeficiente de asimetria y curtosis de la distribución.
print('> Coeficiente de Asimetría:', '%.6s' % df["Daily Return"].skew())
print('> Curtosis:', '%.6s' % df["Daily Return"].kurt())
print('<-------------------------------------------------->')

# VaR Teórico obtenido a través de la distribución normal al 95% y 99% de confianza.
print('> VaR Modelo Gaussiano NC-95% :', '%.6s' % (100 * norm.ppf(0.05, mu, sigma)), '%')
print('> VaR Modelo Gaussiano NC-99% :', '%.6s' % (100 * norm.ppf(0.01, mu, sigma)), '%')
print('> VaR Modelo Gaussiano NC-99.7% :', '%.6s' % (100 * norm.ppf(0.003, mu, sigma)), '%')

# VaR histórico al 95% y 99% de confianza.
print('> VaR Modelo Historico NC-95% :', '%.6s' % (100 * np.percentile(df["Daily Return"], 5)), '%')
print('> VaR Modelo Historico NC-99% :', '%.6s' % (100 * np.percentile(df["Daily Return"], 1)), '%')
print('> VaR Modelo Historico NC-99.7% :', '%.6s' % (100 * np.percentile(df["Daily Return"], .3)), '%')


# Registramos Matplotlib converters para adatpar la fecha -DateTime- al método de dibujo de Matplotlib
register_matplotlib_converters()

# Calculamos la volatilidad histórica de 14 días, la volatilidad anualizada y su SMA de 252 días.
df['Volatilidad_Historica_14_Dias'] = 100*df["Daily Return"].rolling(14).std()
df['Volatilidad_14_Dias_Anualizada'] = df['Volatilidad_Historica_14_Dias'] * (252 ** 0.5)
df['SMA_126_Volatilidad_Anualizada'] = df['Volatilidad_14_Dias_Anualizada'].rolling(126).mean()

# Creamos un gráfico en el que mostramos el precio de cierre, la volatilidad anualizada y su SMA.
fig, ax1 = plt.subplots(figsize=(15, 8))
ax2 = ax1.twinx()
ax1.plot(df['Volatilidad_14_Dias_Anualizada'], 'orange', linestyle='--')
ax1.plot(df['SMA_126_Volatilidad_Anualizada'], 'Green', linestyle='-')
ax2.plot(df['Adj Close'], 'black')

# Asingamos un nombre para el gráfico y para los ejes x e y.
plt.title('Evolucion Histórica del Precio y la Volatilidad', fontsize=16)
ax1.set_xlabel('Fecha')
ax1.set_ylabel('Volatilidad Anualizada', color='black')
ax2.set_ylabel('Precio de Cierre', color='black')

# Configuramos la leyenda, las líneas de cuadrícula y mostramos el gráfico.
ax1.legend(loc='upper left', frameon=True, borderpad=1)
ax1.grid(True)
ax2.grid(False)
plt.show()

# Volatilidad anualizada.
VAM = (252**0.5)*(100 * df["Daily Return"].std())
print('> Volatilidad Anualizada:', '%.6s' % VAM, '%')

# Obtenemos el valor mínimo y máximo de la volatilidad anualizada así como las fechas
# en las que ambos valores son producidos.
Fecha_Minima_Volatilidad = df.Volatilidad_14_Dias_Anualizada[df.Volatilidad_14_Dias_Anualizada == df['Volatilidad_14_Dias_Anualizada'].min()].index.strftime('%Y-%m-%d').tolist()
Fecha_Maxima_Volatilidad = df.Volatilidad_14_Dias_Anualizada[df.Volatilidad_14_Dias_Anualizada == df['Volatilidad_14_Dias_Anualizada'].max()].index.strftime('%Y-%m-%d').tolist()

print('> La Mínima Volatilidad Anualizada fue de', '%.6s' % (df['Volatilidad_14_Dias_Anualizada'].min()), '%', 'registrada el', Fecha_Minima_Volatilidad[0])
print('> La Máxima Volatilidad Anualizada fue de', '%.6s' % (df['Volatilidad_14_Dias_Anualizada'].max()), '%', 'registrada el', Fecha_Maxima_Volatilidad[0])

# Obtenemos el promedio sobre el rango porcentual de los días negativos.
df['DiasNegativos'] = np.where(df['Daily Return'] < 0, 100*(df['High']-df['Low'])/df['Low'], 0)
df_dias_negativos = df.loc[df['DiasNegativos'] != 0]
DN = df_dias_negativos['DiasNegativos'].mean()
print('> Rango Medio días Negativos:', '%.4s' % DN, '%')

# Obtenemos el promedio del rango porcentgual de los días positivos.
df['DiasPositivos'] = np.where(df['Daily Return'] > 0, 100*(df['High']-df['Low'])/df['Low'], 0)
df_dias_positivos = df.loc[df['DiasPositivos'] != 0]
DP = df_dias_positivos['DiasPositivos'].mean()
print('> Rango Medio días Positivos:', '%.4s' % DP, '%')

# Calulamos el ratio del rango entre días positivos y negativos.
print('> Ratio RDN/RDP', '%.4s' % (DN/DP), '%')
