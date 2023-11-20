from dash import Dash,html, dcc, Output, Input
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np
import dash_bootstrap_components as dbc

# Loading the data
noc_region_df = pd.read_csv('../Data/noc_regions.csv')
athlete_events_df = pd.read_csv('../Data/athlete_events.csv')

# Merging the dataframes together
merged_df = pd.merge(athlete_events_df, noc_region_df, how='inner', on='NOC')

# Filtering data for Ice Hockey
ice_hockey_df = merged_df[merged_df['Sport'] == 'Ice Hockey']
#ice_hockey_df['Medal'] = ice_hockey_df['Medal'].replace('nan', np.nan)
# Taking out all of the Nan variables
ice_hockey_non_nan_df = ice_hockey_df.dropna(subset=['Medal'])

# Filtering for the medal distrubution
medal_distribution = ice_hockey_df.groupby(['region', 'Medal']).size().unstack(fill_value=0)

# Initialize the Dash app
app = Dash(__name__)

# Defining the layout
app.layout = dbc.Container([
    html.H1(children='Ice Hockey Data Analysis'),
    dbc.Row([
        dbc.Col([
            # Age distribution in the sport
            dcc.Graph(
                id='age-distribution',
                figure={
                    'data': [
                        {'x': ice_hockey_df['Age'], 'type': 'histogram', 'bins': 20, 'name': 'Age Distribution'},
                    ],
                    'layout': {
                        'title': 'Age Distribution in Ice Hockey',
                        'xaxis': {'title': 'Age'},
                        'yaxis': {'title': 'Count'},
                    }
                }
            ),
        ],width=5),

# Medal distribution between the countries
        dbc.Col([
            dcc.Graph(
                id='medal-distribution',
                figure={
                    'data': [
                        {'x': medal_distribution.index, 'y': medal_distribution[medal], 'type': 'bar', 'name': medal}
                        for medal in medal_distribution.columns
                    ],
                    'layout': {
                        'title': 'Medal Distribution in Ice Hockey',
                        'xaxis': {'title': 'Country'},
                        'yaxis': {'title': 'Number of Medals'},
                        'barmode': 'stack',
                    }
                }
            ),
        ],width = 5),
    ]),

# Distribution of age to gender
    dcc.Graph(
        id='age-gender-distribution',
        figure={
            'data': [
                {'x': ice_hockey_df['Sex'], 'y': ice_hockey_df['Age'], 'type': 'box', 'name': 'Age Distribution by Gender'},
            ],
            'layout': {
                'title': 'Age Distribution in Ice Hockey by Gender',
                'xaxis': {'title': 'Gender'},
                'yaxis': {'title': 'Age'},
            }
        }
    ),

# Number of events in ice hockey
    dcc.Graph(
        id='events-by-year',
        figure={
            'data': [
                {'x': ice_hockey_df['Year'], 'type': 'count', 'marker': {'color': 'viridis'}}
            ],
            'layout': {
                'title': 'Number of Ice Hockey Events by Year',
                'xaxis': {'title': 'Year'},
                'yaxis': {'title': 'Number of Events'},
                'xaxis_tickangle': 45,
            }
        }
    ),

# Graphing up a sunburst chart
    dcc.Graph(
        id='sunburst-chart',
        figure=px.sunburst(
            ice_hockey_non_nan_df,
            path=['Year', 'Medal', 'region'],
            title='Medal Distribution in Ice Hockey by Year and Country',
            color='Medal'
        )
    )
])
app.run(debug=True)