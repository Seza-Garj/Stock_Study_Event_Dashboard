import dash
#import dash_core_components as dcc
#import dash_html_components as html
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import linregress
#import scipy.stats
from scipy import stats
import plotly.graph_objs as go
#import pandas_datareader.data as web
import datetime as dt
#import pandas_datareader


# Define a function to calculate the abnormal returns
def calculate_abnormal_returns(stock_returns, market_returns, window):
    rolling_stock = stock_returns.rolling(window=window).mean()
    rolling_market = market_returns.rolling(window=window).mean()
    beta, alpha = np.polyfit(rolling_market, rolling_stock, deg=1)
    expected_return = beta * rolling_market + alpha
    abnormal_returns = stock_returns - expected_return
    return abnormal_returns


# Define the app and the layout
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1('Event Stock Study', style={'font-family': 'Garamond'}),
    html.Div([
        html.Div([
            html.Label('Stock', style={'font-family': 'Garamond', 'text-decoration': 'underline', "font-size": 20}),
            dcc.Dropdown(
                id='stock',
                options=[
                    {'label': 'Apple', 'value': 'AAPL'},
                    {'label': 'Microsoft', 'value': 'MSFT'},
                    {'label': 'Amazon', 'value': 'AMZN'},
                    {'label': 'Google', 'value': 'GOOGL'},
                    {'label': 'Facebook', 'value': 'FB'}
                ],
                value='AAPL'
            )
        ], style={'width': '33%', 'display': 'inline-block', 'font-family': 'Garamond'}),
        html.Div([
            html.Label('Market', style={'font-family': 'Garamond', 'text-decoration': 'underline', "font-size": 20}),
            dcc.Dropdown(
                id='market',
                options=[
                    {'label': 'S&P 500', 'value': '^GSPC'},
                    {'label': 'Dow Jones', 'value': '^DJI'},
                    {'label': 'Nasdaq', 'value': '^IXIC'}
                ],
                value='^GSPC'
            )
        ], style={'width': '33%', 'display': 'inline-block', 'font-family': 'Garamond'}),
        html.Div([
            html.Label('Date Range ',
                       style={'font-family': 'Garamond', 'text-decoration': 'underline', "font-size": 20}),
            dcc.DatePickerRange(
                id='date_range',
                start_date=pd.to_datetime('2015-01-01'),
                end_date=pd.Timestamp.today()
            )
        ], style={'width': '33%', 'display': 'inline-block', 'font-family': 'Garamond', 'margin-bottom': "50px"})
    ]),
    html.Button('Submit', id='submit-button', n_clicks=0,
                style={'height': '50px', 'width': '80px', 'font-family': 'Garamond', "margin-top": "20px"}),
    dcc.Graph(id='graph', style={'font-family': 'Garamond'})
])


# Define the callback for the graph
@app.callback(
    Output('graph', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('stock', 'value'),
     State('market', 'value'),
     State('date_range', 'start_date'),
     State('date_range', 'end_date')]
)
def update_graph(n_clicks, stock_ticker, market_ticker, start_date, end_date):
    # Convert start and end dates to datetime objects
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Fetch data
    stock_data = yf.download(stock_ticker, start=start_date, end=end_date)
    market_data = yf.download(market_ticker, start=start_date, end=end_date)

    # Convert the index to UTC time zone
    stock_data.index = stock_data.index.tz_localize('UTC')
    market_data.index = market_data.index.tz_localize('UTC')

    # Compute returns
    stock_returns = (stock_data['Close'] - stock_data['Open']) / stock_data['Open']
    stock_returns = stock_returns.sort_index()

    market_returns = (market_data['Close'] - market_data['Open']) / market_data['Open']
    market_returns = market_returns.sort_index()

    # Compute linear regression
    slope, intercept, r_value, p_value, std_err = linregress(market_returns, stock_returns)
    regression_line = slope * market_returns + intercept

    # Format the dates to match yfinance date format
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Create figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=market_returns, y=stock_returns, mode='markers', marker=dict(color='lightblue')))
    fig.add_trace(go.Scatter(x=market_returns, y=regression_line, mode='lines', name='Regression Line'))

    if (start_date >= pd.Timestamp('2020-02-20')) and (end_date <= pd.Timestamp('2021-09-01')):
        fig.update_layout(
            title={
                'text': f'Returns of ({start_date_str} - {end_date_str}) - Abnormal',
                'x': 0.5,
                'y': 0.95,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis_title=f'{market_ticker} Returns',
            yaxis_title=f'{stock_ticker} Returns',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family='Garamond'
        )
    else:
        fig.update_layout(
            title={
                'text': f'Returns of ({start_date_str} - {end_date_str}) - Normal',
                'x': 0.5,
                'y': 0.95,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 22}
            },

            xaxis_title={
                'text': f'{market_ticker} Returns',
                'font': {'family': 'Times New Roman', 'size': 18}
            },
            yaxis_title={
                'text': f'{stock_ticker} Returns',
                'font': {'family': 'Times New Roman', 'size': 18}
            },
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False,

            title_x=0.5,  # center the title,
            font_family='Garamond'
        )

    return fig

if __name__ == '__main__':
    app.run_server()
