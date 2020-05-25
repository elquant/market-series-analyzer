import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import ts_analyzer as tsa
import ui

from datetime import datetime as dt
from dash.dependencies import Input, Output
from style import *


external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        dbc.Row(
            dbc.Col(
                html.H1('Analizador de Series Temporales', style={'textAlign': 'center', 'color': colors['blueText']})
            )
        ),
        dbc.Row(
            dbc.Col(
                [
                    html.H5('Seleccionar símbolo, fecha de inicio y fin:', style={'textAlign': 'left', 'color': colors['blueText']}),
                    dcc.Input(id='ticker-input', value='SPY', type='text'),
                    dcc.DatePickerSingle(id='from-date-picker', date=str(dt(1993, 1, 1)), style={'padding': '20px'}),
                    dcc.DatePickerSingle(id='to-date-picker', date=str(dt.today()))
                ]
            )
        ),
        html.Div(id='output-analysis', style={'color': colors['whiteText']})
    ],
    style={
        'backgroundColor': colors['background']
    }
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
    historical_prices = ui.get_historic_prices_graph(ticker_analysis, ticker_symbol)
    statistic_results = ui.get_statistic_results(ticker_analysis)
    distplot_daily_returns= ui.get_distplot_daily_returns(ticker_analysis)
    vol_price_evolution = ui.get_vol_price_evolution(ticker_analysis)

    return [
        dbc.Row(
            dbc.Col(
                dcc.Graph(id='historical_prices', figure=historical_prices),
                width=12
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5('Estadísticos del análisis:', style={'textAlign': 'left', 'color': colors['blueText']}),
                        html.Div(children=statistic_results)
                    ],
                    width=4
                ),
                dbc.Col(
                        html.Div(children=[
                            dcc.Graph(id='distplot_daily_returns', figure=distplot_daily_returns), 
                            dcc.Graph(id='vol_price_evolution', figure=vol_price_evolution)
                        ])
                    , width=8
                )
            ]
        )
    ]


if __name__ == '__main__':
    app.run_server(debug=True)
