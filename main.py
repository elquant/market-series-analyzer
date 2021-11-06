import dash
import ui
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output

external_stylesheets = [dbc.themes.SLATE]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = 'TS Analyzer - elQuant.com'
app.layout = ui.page_layout()


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
    return ui.build_results_page(ticker_symbol, from_date, to_date)


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080, debug=True, use_reloader=True)
