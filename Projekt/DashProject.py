from dash import Dash,html, dcc, Output, Input
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import dash_bootstrap_components as dbc
import hashlib
from dash_bootstrap_templates import load_figure_template

load_figure_template("flatly")

# Loading the data
athlete_events_df = pd.read_csv('../Data/athlete_events.csv')

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

    # Dropdown menu for selecting sport
    dcc.Dropdown(
        id='sport-dropdown',
        options=sports_options,
        value='Judo',
        style={'width': '50%'}
    ),

    # Displayed content
    html.Div(id='output-container'),

    # Age distribution in the sport
    dcc.Graph(id='first-figure', style={'display': 'none'}),
        
    # Medal distribution between the countries
    dcc.Graph(id='second-figure', style={'display': 'none'}),
        
    # Distribution of age to gender 
    dcc.Graph(id='third-figure', style={'display': 'none'}),
        
    # Number of events in the sport
    dcc.Graph(id='fourth-figure', style={'display': 'none'}),
   
    # Graphing up a sunburst chart or bar graph with consecutive wins
    dcc.Graph(id='fifth-figure', style={'display': 'none'}),
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

        # Sunburst chart showing the year, medal and which country won
        sunburst_chart_figure = px.sunburst(
            sport_df.dropna(subset=['Medal']),
            path=['Year', 'Medal', 'NOC'],
            title='Medal Distribution in ' + selected_sport + ' by Year and Country',
            color='Medal'
        )

        # Outputting the graphs into the dashboard
        return [
            html.Div(f"Displaying data for {selected_sport} Statistic"),
            dcc.Graph(figure=age_distribution_figure, id='first-figure'),
            dcc.Graph(figure=medal_distribution_figure, id='second-figure'),
            dcc.Graph(figure=age_gender_distribution_figure, id='third-figure'),
            dcc.Graph(figure=events_by_year_figure, id='fourth-figure'),
            dcc.Graph(figure=sunburst_chart_figure, id='fifth-figure')
        ]

    else:
        #Filter for canadian gold and count how many by event
        canada_gold = athlete_events_df.query("NOC=='CAN' & Medal =='Gold'")
        events_by_year = canada_gold[["Event", "Year", "Sport", "Medal"]].groupby(["Event"], as_index=False).value_counts().sort_values(by=["Event", "Year"], ascending=[False, True])

        #Drop all unique rows (non-consecutive wins) + calculate difference in years between wins
        title_defences = events_by_year[events_by_year['Event'].duplicated(keep=False)]
        title_defences.loc[:,'difference'] = title_defences.groupby("Event", as_index=False)['Year'].diff()
        #Drop consecutive wins with more than 2 olympic games apart (!=4 years), drop unnecessary columns
        title_defences.drop(title_defences[(title_defences['difference'] != 4)].index, inplace=True)
        title_defences.drop(['count', "difference"], axis=1, inplace=True)
        # count amount of consecutive wins & sort
        title_defences = title_defences.value_counts().reset_index().sort_values(by=["Event", "Year"], ascending=[True, True])
        # Filtering for only Canadian athletes
        df_canada = athlete_events_df[athlete_events_df['NOC'] == 'CAN']

        # The Sports which Canadians have Most Medals
        sport_medals_canada = df_canada.groupby('Sport')['Medal'].count().sort_values(ascending=False).reset_index()
        fig_sports_canada = px.bar(sport_medals_canada, x='Sport', y='Medal',
                                   title='Sports with Most Medals in Canada', labels={'Medal': 'Number of Medals'})

        # Number of Medals per Olympics for Canadaian athletes
        medals_per_year_canada = df_canada.groupby('Year')['Medal'].count().reset_index()
        fig_year_canada = px.bar(medals_per_year_canada, x='Year', y='Medal',
                                 title='Number of Medals per Olympics in Canada', labels={'Medal': 'Number of Medals'}, color='Year')

        # Histogram of Athlete Ages in Canada
        fig_age_canada = px.histogram(df_canada, x='Age',
                                      title='Histogram of Athlete Ages in Canada', labels={'Age': 'Age'}, color='Age')

        # Number of years that canada has won 
        events_by_year_figure_canada = px.histogram(df_canada, x='Year',
                                             title='Number of Events by Year in Canada')
        events_by_year_figure_canada.update_layout(bargap=0.2)

        # Showing consecutive wins of the Candian teams
        Consecutive_wins_graph = px.bar(title_defences, x="Event", y="count", color="Year", labels=dict(count="Title defence"), hover_data=dict(count=False, Event=True, Sport=False), title="Years of consecutive gold medals of the Canadian team")
        Consecutive_wins_graph.update_layout(xaxis={'categoryorder':'total ascending'}) 

        # Outputting the graphs into the dashboard
        return [
            html.Div("Displaying data for Country Statistic"),
            dcc.Graph(figure=fig_sports_canada, id='first-figure'),
            dcc.Graph(figure=fig_year_canada, id='second-figure'),
            dcc.Graph(figure=fig_age_canada, id='third-figure'),
            dcc.Graph(figure=events_by_year_figure_canada, id='fourth-figure'),
            dcc.Graph(figure=Consecutive_wins_graph, id='fifth-figure')
        ]
    
if __name__ == '__main__':
    app.run(debug=True)