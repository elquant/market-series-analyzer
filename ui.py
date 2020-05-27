import numpy as np
import analyzer as tsa
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from style import *
from datetime import datetime as dt
from plotly.subplots import make_subplots


def main_title():
    return html.H1('Analizador de Series Temporales', style=mainTitle)


def input_section_title():
    return html.H5('Ingrese símbolo, fecha de inicio y fin:', style=inputSectionTitle)


def symbol_input():
    return dbc.Input(id='ticker-input', value='SPY', type='text')


def from_date_input():
    return dcc.DatePickerSingle(id='from-date-picker', date=str(dt(2000, 1, 1)))


def to_date_input():
    return dcc.DatePickerSingle(id='to-date-picker', date=str(dt.today()))


def output_analysis_div():
    return html.Div(id='output-analysis', style=outputAnalysisDiv)


def page_layout():
    return dbc.Container(
        [
            dbc.Row(dbc.Col(main_title())),
            dbc.Row(dbc.Col(input_section_title())),
            dbc.Row(
                [
                    dbc.Col(symbol_input(), width=1),
                    dbc.Col(from_date_input(), width=1),
                    dbc.Col(to_date_input(), width=1)
                ],
                style=inputSection
            ),
            output_analysis_div()
        ],
        style=pageLayout,
        fluid=True
    )


def get_historic_prices_graph(ticker_analysis, ticker_symbol):
    return {
        'data': [
            {
                'x': ticker_analysis.index(),
                'y': ticker_analysis.adj_close(),
                'type': 'line',
                'name': ticker_symbol.upper()
            }
        ],
        'layout': {
            'title': f'Histórico del {ticker_symbol.upper()} (precio de cierre ajustado)',
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {'color': colors['blueText']}
        }
    }


def get_statistic_results(ticker_analysis):
    rounding = 4

    rows = [
        html.Tr([html.Td("Tasa de Crecimiento Anual Compuesto (CAGR)"), html.Td(f"{round(ticker_analysis.cagr, rounding)} %")]),
        html.Tr([html.Td("Retorno de comprar y mantener"), html.Td(f"{round(ticker_analysis.buy_and_hold_return, rounding)} %")]),
        html.Tr([html.Td("Máximo Drawdown Histórico"), html.Td(f"{round(ticker_analysis.max_dd, rounding)} %")]),
        html.Tr([html.Td("Media Diaria"), html.Td(f"{round(ticker_analysis.mean_daily_return, rounding)} %")]),
        html.Tr([html.Td("Desviación Típica Diaria"), html.Td(f"{round(ticker_analysis.std_daily_return, rounding)} %")]),
        html.Tr([html.Td("Máxima Pérdida Diaria"), html.Td(f"{round(ticker_analysis.min_return, rounding)} %")]),
        html.Tr([html.Td("Máximo Beneficio Diario"), html.Td(f"{round(ticker_analysis.max_return, rounding)} %")]),
        html.Tr([html.Td("Número de Días Analizados"), html.Td(f"{ticker_analysis.trading_days}")]),
        html.Tr([html.Td("Coeficiente de Asimetría"), html.Td(f"{round(ticker_analysis.skewness, rounding)}")]),
        html.Tr([html.Td("Curtosis"), html.Td(f"{round(ticker_analysis.kurtosis, rounding)}")]),
        html.Tr([html.Td("VaR Modelo Gaussiano NC-95%"), html.Td(f"{round(ticker_analysis.var_gauss_95, rounding)} %")]),
        html.Tr([html.Td("VaR Modelo Gaussiano NC-99%"), html.Td(f"{round(ticker_analysis.var_gauss_99, rounding)} %")]),
        html.Tr([html.Td("VaR Modelo Gaussiano NC-99.7%"), html.Td(f"{round(ticker_analysis.var_gauss_99_7, rounding)} %")]),
        html.Tr([html.Td("VaR Modelo Histórico NC-95%"), html.Td(f"{round(ticker_analysis.var_historic_95, rounding)} %")]),
        html.Tr([html.Td("VaR Modelo Histórico NC-99%"), html.Td(f"{round(ticker_analysis.var_historic_99, rounding)} %")]),
        html.Tr([html.Td("VaR Modelo Histórico NC-99.7%"), html.Td(f"{round(ticker_analysis.var_historic_99_7, rounding)} %")]),
        html.Tr([html.Td("Volatilidad Anualizada"), html.Td(f"{round(ticker_analysis.vam, rounding)} %")]),
        html.Tr([html.Td(f"Mínima volatilidad anualizada registrada el {ticker_analysis.min_vol_date()}"), html.Td(f"{round(ticker_analysis.historic_vol_14_days_annualized().min(), rounding)} %")]),
        html.Tr([html.Td(f"Máxima volatilidad anualizada registrada el {ticker_analysis.max_vol_date()}"), html.Td(f"{round(ticker_analysis.historic_vol_14_days_annualized().max(), rounding)} %")]),
        html.Tr([html.Td("Rango Medio días Negativos"), html.Td(f"{round(ticker_analysis.dn, rounding)} %")]),
        html.Tr([html.Td("Rango Medio días Positivos"), html.Td(f"{round(ticker_analysis.dp, rounding)} %")]),
        html.Tr([html.Td("Ratio RDN/RDP"), html.Td(f"{round(ticker_analysis.pos_neg_days_ratio(), rounding)} %")])
    ]

    return dbc.Table([html.Tbody(rows)], bordered=True, dark=True, hover=True, responsive=True, striped=True)


def get_distplot_daily_returns(ticker_analysis):
    (mu, sigma) = ticker_analysis.mu, ticker_analysis.sigma
    distplot_daily_returns = go.Figure()
    distplot_daily_returns.add_trace(
        go.Histogram(x=ticker_analysis.daily_return(),
                     histnorm='probability density',
                     name="Retornos diarios",
                     xbins=dict(start=-1, end=1, size=0.00025)
                     )
    )
    distplot_daily_returns.add_trace(
        go.Histogram(x=np.random.normal(mu, sigma, 100000),
                     histnorm='probability density',
                     name="Distribución normal (\u03BC={0:.2g}, \u03C3={1:.2f})".format(mu, sigma),
                     xbins=dict(start=-1, end=1, size=0.00025),
                     opacity=0.5
                     )
    )

    distplot_daily_returns.update_xaxes(title_text="Retorno diario", showgrid=False)
    distplot_daily_returns.update_yaxes(title_text="Frecuencia", showgrid=False)
    distplot_daily_returns.update_layout(
        {
            'title': 'Distribución de los retornos diarios',
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {'color': colors['blueText']},
            'bargap': 0.02
        }
    )

    return distplot_daily_returns


def get_vol_price_evolution(ticker_analysis):
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
            x=ticker_analysis.index(),
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

    vol_price_evolution.update_xaxes(title_text="Fecha", showgrid=False)
    vol_price_evolution.update_yaxes(title_text="Volatilidad anualizada", showgrid=False, secondary_y=False)
    vol_price_evolution.update_yaxes(title_text="Precio de cierre", showgrid=False, secondary_y=True)
    vol_price_evolution.update_layout({
        'title': 'Evolución histórica del precio y la volatilidad',
        'plot_bgcolor': colors['background'],
        'paper_bgcolor': colors['background'],
        'font': {'color': colors['blueText']}
    })

    return vol_price_evolution


def build_results_page(ticker_symbol, from_date, to_date):
    ticker_analysis = tsa.TimeSeriesAnalyzer(ticker_symbol, from_date, to_date)
    historical_prices = get_historic_prices_graph(ticker_analysis, ticker_symbol)
    statistic_results = get_statistic_results(ticker_analysis)
    distplot_daily_returns = get_distplot_daily_returns(ticker_analysis)
    vol_price_evolution = get_vol_price_evolution(ticker_analysis)

    return [
        dbc.Row(dbc.Col(dcc.Graph(id='historical_prices', figure=historical_prices), width=12)),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(id='distplot_daily_returns', figure=distplot_daily_returns),
                        dcc.Graph(id='vol_price_evolution', figure=vol_price_evolution)
                    ],
                    width=8
                ),
                dbc.Col(
                    [
                        html.H5('Estadísticos del análisis', style=statisticResultsTitles),
                        html.Div(children=statistic_results)
                    ],
                    width=3
                )
            ]
        )
    ]
