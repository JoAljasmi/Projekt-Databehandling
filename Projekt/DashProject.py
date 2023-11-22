from dash import Dash,html, dcc, Output, Input
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

load_figure_template("flatly")

# Loading the data
athlete_events_df = pd.read_csv('../Data/athlete_events.csv')

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# Unique sports for dropdown
sports_options = [{'label': sport, 'value': sport} for sport in athlete_events_df['Sport'].unique()]

# Defining the layout
app.layout = dbc.Container([
    html.H1(children='Olympic Sports Data Analysis'),

    # Dropdown menu for selecting sport
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
            dcc.Graph(id='age-distribution'),
        ], width=5),

        # Medal distribution between the countries
        dbc.Col([
            dcc.Graph(id='medal-distribution'),
        ], width=5),
    ]),

    # Distribution of age to gender
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='age-gender-distribution'),
        ], width=5),

        # Number of events in the sport
        dbc.Col([
            dcc.Graph(id='events-by-year'),
        ],width=5),
    ]),
    dbc.Row([
        # Graphing up a sunburst chart
        dcc.Graph(id='sunburst-chart'),
    ]),
])

# Callback to update graphs based on selected sport
@app.callback(
    [Output('output-container', 'children'),
     Output('age-distribution', 'figure'),
     Output('medal-distribution', 'figure'),
     Output('age-gender-distribution', 'figure'),
     Output('events-by-year', 'figure'),
     Output('sunburst-chart', 'figure')],
    [Input('sport-dropdown', 'value')]
)
def update_sport(selected_sport):
    # Filter data for the selected sport
    sport_df = athlete_events_df[athlete_events_df['Sport'] == selected_sport]

    # Filtering for the medal distribution
    medal_distribution = sport_df.groupby(['NOC', 'Medal']).size().unstack(fill_value=0)

    medal_distribution = medal_distribution.reset_index().melt(id_vars=["NOC"], value_vars=["Bronze", "Silver", "Gold"])

    # Displayed content
    output_text = f"Displaying data for {selected_sport}"

    # Age distribution in the sport
    age_distribution_figure = px.histogram(sport_df, x='Age', title='Age Distribution in ' + selected_sport, color='Age')

    # Medal distribution between the countries
    medal_distribution_figure = px.bar(
        medal_distribution,
        x="NOC",
        y="value",
        labels={'x': 'Country', 'y': 'Number of Medals'},
        color= 'Medal',
        title='Medal Distribution in ' + selected_sport,
        barmode='stack'
    )

    # Distribution of age to gender
    age_gender_distribution_figure = px.box(sport_df, x='Sex', y='Age', title='Age Distribution in ' + selected_sport + ' by Gender', color= 'Sex')

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

    return output_text, age_distribution_figure, medal_distribution_figure, age_gender_distribution_figure, events_by_year_figure, sunburst_chart_figure


# Alejandro Uppgift 1 graf

# canada_gold = olympic_df.query("region=='Canada' & Medal =='Gold'")
# events_by_year = canada_gold[["Event", "Year", "Sport", "Medal"]].groupby(["Event"], as_index=False).value_counts().sort_values(by=["Event", "Year"], ascending=[False, True])


# title_defences = events_by_year[events_by_year['Event'].duplicated(keep=False)]
# title_defences.loc[:,'difference'] = title_defences.groupby("Event", as_index=False)['Year'].diff()
# title_defences.drop(title_defences[(title_defences['difference'] != 4)].index, inplace=True)
# title_defences.drop(['count', "difference"], axis=1, inplace=True)
# title_defences = title_defences.value_counts().reset_index().sort_values(by=["Event", "Year"], ascending=[True, True])


# fig5 = px.bar(title_defences, x="Event", y="count", color="Year", labels=dict(count="Titelförsvar"), hover_data=dict(count=False, Event=True, Sport=False), title="År med guldmedaljer i följd")
# fig5.update_layout(xaxis={'categoryorder':'total ascending'})

# fig5.show()


# Uppgift 1 ) Antal medaljer per OS för Kanada. Kehua
#medals_per_os = df_canada.groupby(['Year', 'Medal']).size().unstack(fill_value=0).reset_index()

#fig = px.bar(
#    medals_per_os,
#   x='Year',
#   y=['Gold', 'Silver', 'Bronze'],
#   title='Antal medaljer per OS för Kanada',
#   labels={'value': 'Antal medaljer', 'variable': 'Medaljer'},
#   height=600,
#   width=800,
#   color_discrete_map={'Gold': 'gold', 'Silver': 'silver', 'Bronze': 'brown'} 
#)
#fig.show()

# Uppgift 1 ) De sporter som Kanada fått flest medaljer i.

#df_canada = merged_df[merged_df['Team'] == 'Canada']
#canada_sport_medals = df_canada.groupby('Sport')['Medal'].count().sort_values(ascending=False).head(15).reset_index()

#fig = px.bar(canada_sport_medals, 
#             x='Sport', 
#             y='Medal', 
#             title='Antal medaljer per sport för Kanada i OS',
#             labels={'Medal': 'Antal medaljer', 'Sport': 'Sport'},
#             color='Medal',
#)

#fig.update_layout(xaxis_title='Sport', yaxis_title='Antal medaljer')
#fig.show()

# Uppgift 1 ) Histogram över åldrar för Kanadas OS-deltagare.
#fig = px.histogram(df_canada, x='Age', nbins=20, 
#                   title='Histogram över åldrar för Kanadas OS-deltagare',
#                   labels={'Age': 'Ålder', 'count': 'Antal deltagare'},
#                   opacity=0.7, color_discrete_sequence=['blue'])

#fig.update_layout(xaxis_title='Ålder', yaxis_title='Antal deltagare', bargap=0.05)
#fig.show()

# Uppgift 2 ) Simmning: Åldersfördelning.
#swimming_age = merged_df[merged_df['Sport'] == 'Swimming']['Age'].value_counts().head(30).reset_index()
#swimming_age.columns = ['Ålder', 'Antal deltagare']

#fig = px.bar(swimming_age, x='Ålder', y='Antal deltagare', 
#             title='Åldersfördelning i simning',
#             labels={'Ålder': 'Ålder', 'Antal deltagare': 'Antal deltagare'},
#)
#fig.update_layout(xaxis_title='Ålder', yaxis_title='Antal deltagare')
#fig.show()

# Uppgift 2 ) Simmning: Medaljfördelning mellan länder.
#swimming_medal = merged_df[merged_df['Sport'] == 'Swimming'].groupby('region')['Medal'].count().sort_values(ascending=False).head(10).reset_index()
#swimming_medal.columns = ['Land', 'Antal medaljer']

#fig = px.bar(swimming_medal, x='Land', y='Antal medaljer',
#             title='Medaljfördelning mellan länder i simning',
#             labels={'Land': 'Land', 'Antal medaljer': 'Antal medaljer'},
#)

#fig.update_layout(xaxis_title='Land', yaxis_title='Antal medaljer')
#fig.show()
if __name__ == '__main__':
    app.run_server(debug=True)
    