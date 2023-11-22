from dash import Dash,html, dcc, Output, Input
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import dash_bootstrap_components as dbc
import hashlib
from dash_bootstrap_templates import load_figure_template


def title_defences(df):
    canada_gold = df.query("Medal =='Gold'")
    events_by_year = canada_gold[["Event", "Year", "Sport", "Medal"]].groupby(["Event"], as_index=False).value_counts().sort_values(by=["Event", "Year"], ascending=[False, True])


    title_defences = events_by_year[events_by_year['Event'].duplicated(keep=False)]
    title_defences.loc[:,'difference'] = title_defences.groupby("Event", as_index=False)['Year'].diff()
    title_defences.drop(title_defences[(title_defences['difference'] != 4)].index, inplace=True)
    title_defences.drop(['count', "difference"], axis=1, inplace=True)
    title_defences = title_defences.value_counts().reset_index().sort_values(by=["Event", "Year"], ascending=[True, True])


    fig5 = px.bar(title_defences, x="Event", y="count", color="Year", labels=dict(count="Title defences"), hover_data=dict(count=False, Event=True, Sport=False), title="Successful title defences by sport")
    fig5.update_layout(xaxis={'categoryorder':'total ascending'})

    return fig5


load_figure_template("flatly")

# Loading the data
athlete_events_df = pd.read_csv('athlete_events.csv')

#Hashlibing the names of the athletes
athlete_events_df['Name'] = athlete_events_df['Name'].apply(lambda x: hashlib.sha256(x.encode()).hexdigest())

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# Unique sports for dropdown
sports_options = [{"label": "Judo", "value": "Judo"}, {"label": "Ice Hockey", "value": "Ice Hockey"}, {"label": "Swimming", "value": "Swimming"}]

# Defining the layout
app.layout = dbc.Container([
    html.H1(children='Olympic Sports Data Analysis'),

    # Dropdown menu for selecting statistic type
    dcc.Dropdown(
        id='statistic-type-dropdown',
        options=[
            {'label': 'Country Statistic', 'value': 'country'},
            {'label': 'Sport Statistic', 'value': 'sport'}
        ],
        value='country',
        style={'width': '50%'}
    ),

    # Dropdown menu for selecting sport (appears when Sport Statistic is selected)
    dcc.Dropdown(
        id='sport-dropdown',
        options=sports_options,
        value='Ice Hockey',
        style={'width': '50%'}
    ),

    # Displayed content
    html.Div(id='output-container'),

    dbc.Row([
        dbc.Col([
            # Age distribution in the sport
            dcc.Graph(id='age-distribution', style={'display': 'none'}),
        ], width=5),

        # Medal distribution between the countries
        dbc.Col([
            dcc.Graph(id='medal-distribution', style={'display': 'none'}),
        ], width=5),
    ]),

    # Distribution of age to gender
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='age-gender-distribution', style={'display': 'none'}),
        ], width=5),

        # Number of events in the sport
        dbc.Col([
            dcc.Graph(id='events-by-year', style={'display': 'none'}),
        ], width=5),
    ]),
    dbc.Row([
        # Graphing up a sunburst chart
        dcc.Graph(id='sunburst-chart', style={'display': 'none'}),
    ]),
])

# Callback to update graphs based on selected statistic type and sport
@app.callback(
    Output('output-container', 'children'),
    [Input('statistic-type-dropdown', 'value'),
     Input('sport-dropdown', 'value')]
)

def update_sport(statistic_type, selected_sport):
    if statistic_type == 'sport':
        # Filter data for the selected sport
        sport_df = athlete_events_df[athlete_events_df['Sport'] == selected_sport]

        # Filtering for the medal distribution
        medal_distribution = sport_df.groupby(['NOC', 'Medal']).size().unstack(fill_value=0)

        # Changing the wide variable 
        medal_distribution = medal_distribution.reset_index().melt(id_vars=["NOC"], value_vars=["Bronze", "Silver", "Gold"])




        # Age distribution in the sport
        age_distribution_figure = px.histogram(sport_df, x='Age', title='Age Distribution in ' + selected_sport, color='Age')

        # Medal distribution between the countries
        medal_distribution_figure = px.bar(
            medal_distribution,
            x="NOC",
            y="value",
            labels={'x': 'Country', 'y': 'Number of Medals'},
            color='Medal',
            title='Medal Distribution in ' + selected_sport,
            barmode='stack'
        )

        # Distribution of age to gender
        age_gender_distribution_figure = px.box(sport_df, x='Sex', y='Age',
                                                title='Age Distribution in ' + selected_sport + ' by Gender', color='Sex')

        # Number of events in the sport
        events_by_year_figure = px.histogram(sport_df, x='Year', color='Year',
                                             title='Number of ' + selected_sport + ' Events by Year')

        # Sunburst chart
        sunburst_chart_figure = px.sunburst(
            sport_df.dropna(subset=['Medal']),
            path=['Year', 'Medal', 'NOC'],
            title='Medal Distribution in ' + selected_sport + ' by Year and Country',
            color='Medal'
        )
        return [
            html.Div(f"Displaying data for {selected_sport} Statistic"),
            dcc.Graph(figure=age_distribution_figure, id='age-distribution'),
            dcc.Graph(figure=medal_distribution_figure, id='medal-distribution'),
            dcc.Graph(figure=age_gender_distribution_figure, id='age-gender-distribution'),
            dcc.Graph(figure=events_by_year_figure, id='events-by-year'),
            dcc.Graph(figure=sunburst_chart_figure, id='sunburst-chart')
        ]

    else:
        # Filter data for the selected country (assuming it's Canada)
        df_canada = athlete_events_df[athlete_events_df['NOC'] == 'CAN']

        # Sports with Most Medals in Canada
        sport_medals_canada = df_canada.groupby('Sport')['Medal'].count().sort_values(ascending=False).reset_index()
        fig_sports_canada = px.bar(sport_medals_canada, x='Sport', y='Medal',
                                   title='Sports with Most Medals in Canada', labels={'Medal': 'Number of Medals'})

        # Number of Medals per Olympics in Canada
        medals_per_year_canada = df_canada.groupby('Year')['Medal'].count().reset_index()
        fig_year_canada = px.bar(medals_per_year_canada, x='Year', y='Medal',
                                 title='Number of Medals per Olympics in Canada', labels={'Medal': 'Number of Medals'}, color='Year')

        # Histogram of Athlete Ages in Canada
        fig_age_canada = px.histogram(df_canada, x='Age',
                                      title='Histogram of Athlete Ages in Canada', labels={'Age': 'Age'}, color='Age')

        # Set default values for figures when Country Statistic is selected
        events_by_year_figure_canada = px.histogram(df_canada, x='Year', color='Year',
                                             title='Number of Events by Year in Canada')

        sunburst_chart_figure_canada = px.sunburst(df_canada.dropna(subset=['Medal']),
                                            path=['Year', 'Medal', 'Sport'],
                                            title='Medal Distribution in Canada by Year and Sport',
                                            color='Medal')
        
        # Canadian title defences
        title_defences_chart = title_defences(df_canada)
        

        return [
            html.Div("Displaying data for Country Statistic"),
            dcc.Graph(figure=title_defences_chart, id='title-defences-chart'),
            dcc.Graph(figure=fig_sports_canada, id='age-distribution'),
            dcc.Graph(figure=fig_year_canada, id='medal-distribution'),
            dcc.Graph(figure=fig_age_canada, id='age-gender-distribution'),
            dcc.Graph(figure=events_by_year_figure_canada, id='events-by-year'),
            dcc.Graph(figure=sunburst_chart_figure_canada, id='sunburst-chart')
        ]
    


if __name__ == '__main__':
    app.run(debug=True, port=8052)