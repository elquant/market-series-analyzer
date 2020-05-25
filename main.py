import dash
import pandas as pd
import numpy as np
import pandas_datareader as dr
import dash_core_components as dcc
import dash_html_components as html
import ts_analyzer as tsa
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from plotly.subplots import make_subplots
from scipy import stats
from datetime import datetime as dt
from dash.dependencies import Input, Output


external_stylesheets = [dbc.themes.BOOTSTRAP]

colors = {
    'background': '#111111',
    'text': '#7FDBFF',
    'whiteText': '#FFFFFF'
}

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        dbc.Row(
            dbc.Col(
                html.H1('Analizador de Series Temporales', style={'textAlign': 'center', 'color': colors['text']})
            )
        ),
        dbc.Row(
            dbc.Col(
                [
                    html.H5('Seleccionar símbolo, fecha de inicio y fin:', style={'textAlign': 'left', 'color': colors['text']}),
                    dcc.Input(id='ticker-input', value='SPY', type='text'),
                    dcc.DatePickerSingle(id='from-date-picker', date=str(dt(1993, 1, 1)), style={'padding': '20px'}),
                    dcc.DatePickerSingle(id='to-date-picker', date=str(dt.today()))
                ]
            )
        ),
        html.Div(id='output-analysis', style={'color': colors['whiteText']})
    ],
    style={'backgroundColor': colors['background']}
)


@app.callback(
    Output(component_id='output-analysis', component_property='children'),
    [
        Input(component_id='ticker-input', component_property='value'),
        Input(component_id='from-date-picker', component_property='date'),
        Input(component_id='to-date-picker', component_property='date')
    ]
)
def update_analysis_results(ticker_symbol, from_date, to_date):
    if len(ticker_symbol) < 3:
        return

    ticker_analysis = tsa.TimeSerieAnalyzer(ticker_symbol, from_date, to_date)

    # Price Graph ----------------------------------------------------------------

    historical_prices = {
        'data': [
            {
                'x': ticker_analysis.index(),
                'y': ticker_analysis.adj_close(),
                'type': 'line',
                'name': ticker_symbol.upper()
            }
        ],
        'layout': {
            'title': f'Histórico del {ticker_symbol.upper()} - Precio Ajustado',
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {'color': colors['text']}
        }
    }

    # Statistic Results ----------------------------------------------------------

    statistic_results = [
        html.P(
            f"Tasa de Crecimiento Anual Compuesto (CAGR): {round(ticker_analysis._cagr, 2)} %"),
        html.P(
            f"Retorno de comprar y mantener: {round(ticker_analysis._buy_and_hold_return, 2)} %"),
        html.P(
            f"Máximo Drawdown Histórico: {round(ticker_analysis._max_dd, 2)} %"),
        html.P(
            f"Media Diaria: {round(ticker_analysis._mean_daily_return, 2)} %"),
        html.P(
            f"Desviación Típica Diaria: {round(ticker_analysis._std_daily_return, 2)} %"),
        html.P(
            f"Máxima Pérdida Diaria: {round(ticker_analysis._min_return, 2)} %"),
        html.P(
            f"Máximo Beneficio Diario: {round(ticker_analysis._max_return, 2)} %"),
        html.P(f"Número de Días Analizados: {ticker_analysis._trading_days}"),
        html.P(
            f"Coeficiente de Asimetría: {round(ticker_analysis._skewness, 2)}"),
        html.P(f"Curtosis: {round(ticker_analysis._kurtosis, 2)}"),
        html.P(
            f"VaR Modelo Gaussiano NC-95%: {round(ticker_analysis._var_gauss_95, 2)} %"),
        html.P(
            f"VaR Modelo Gaussiano NC-99%: {round(ticker_analysis._var_gauss_99, 2)} %"),
        html.P(
            f"VaR Modelo Gaussiano NC-99.7%: {round(ticker_analysis._var_gauss_99_7, 2)} %"),
        html.P(
            f"VaR Modelo Historico NC-95%: {round(ticker_analysis._var_historic_95, 2)} %"),
        html.P(
            f"VaR Modelo Historico NC-99%: {round(ticker_analysis._var_historic_99, 2)} %"),
        html.P(
            f"VaR Modelo Historico NC-99.7%: {round(ticker_analysis._var_historic_99_7, 2)} %"),
        html.P(f"Volatilidad Anualizada: {round(ticker_analysis._VAM, 2)} %"),
        html.P(
            f"La mínima volatilidad anualizada fue de {round(ticker_analysis.historic_vol_14_days_annualized().min(), 2)} % registrada el {ticker_analysis.min_vol_date()}"),
        html.P(
            f"La máxima volatilidad anualizada fue de {round(ticker_analysis.historic_vol_14_days_annualized().max(), 2)} % registrada el {ticker_analysis.max_vol_date()}"),
        html.P(
            f"Rango Medio días Negativos: {round(ticker_analysis._DN, 2)} %"),
        html.P(
            f"Rango Medio días Positivos: {round(ticker_analysis._DP, 2)} %"),
        html.P(
            f"Ratio RDN/RDP: {round(ticker_analysis.pos_neg_days_ratio(), 2)} %")
    ]

    # Distribution Plot of Daily Returns -----------------------------------------

    x0 = ticker_analysis.daily_return()
    x1 = np.random.randn(ticker_analysis.count())

    distplot_daily_returns = go.Figure()
    distplot_daily_returns.add_trace(go.Histogram(x=x0))
    distplot_daily_returns.add_trace(go.Scatter(x=x1, y=x1**2))

    distplot_daily_returns.update_layout(barmode='overlay')
    distplot_daily_returns.update_traces(opacity=0.75)

    distplot_daily_returns.update_layout({
        'title': 'Distribución de los retornos diarios',
        'plot_bgcolor': colors['background'],
        'paper_bgcolor': colors['background'],
        'font': {'color': colors['text']}
    })

    # Volatility and Price Evolution Plot ----------------------------------------

    vol_price_evolution = make_subplots(specs=[[{"secondary_y": True}]])

    vol_price_evolution.add_trace(
        go.Scatter(
            x=ticker_analysis.index(),
            y=ticker_analysis.historic_vol_14_days_annualized(),
            name="Volatilidad anualizada",
            mode='lines'),
        secondary_y=False
    )

    vol_price_evolution.add_trace(
        go.Scatter(
            x=ticker_analysis._data.index,
            y=ticker_analysis.historic_vol_sma_126(),
            name="Volatilidad anualizada SMA[126]",
            mode='lines'),
        secondary_y=False
    )

    vol_price_evolution.add_trace(
        go.Scatter(
            x=ticker_analysis.index(),
            y=ticker_analysis.adj_close(),
            name="Precio de cierre ajustado",
            mode='lines'),
        secondary_y=True
    )

    vol_price_evolution.update_xaxes(title_text="<b>Fecha</b>")
    vol_price_evolution.update_yaxes(
        title_text="<b>Volatilidad anualizada</b>", secondary_y=False)
    vol_price_evolution.update_yaxes(
        title_text="<b>Precio de cierre</b>", secondary_y=True)

    vol_price_evolution.update_layout({
        'title': 'Evolucion histórica del precio y la volatilidad',
        'plot_bgcolor': colors['background'],
        'paper_bgcolor': colors['background'],
        'font': {'color': colors['text']}
    })

    return [
            
            dbc.Row(
                dbc.Col(
                    dcc.Graph(id='historical_prices', figure=historical_prices), width=12
                )
            ),
            dbc.Row([
                dbc.Col(
                    [
                        html.H5('Estadísticos del análisis:', style={'textAlign': 'left', 'color': colors['text']}),
                        html.Div(children=statistic_results)
                    ], width=4
                ),
                dbc.Col(
                    [
                        html.Div(children=[
                            dcc.Graph(id='distplot_daily_returns', figure=distplot_daily_returns),
                            dcc.Graph(id='vol_price_evolution', figure=vol_price_evolution)
                        ])   
                    ], width=8
                )
            ])
            ]


if __name__ == '__main__':
    app.run_server(debug=True)