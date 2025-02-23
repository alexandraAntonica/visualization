import dash
import plotly.express as px
from dash import dcc, html, Input, Output
from jbi100_app.data import get_data
from dash import callback_context

df = get_data()

#####
#Preprocessing
#####

#Outlier removal 
def remove_outliers(group, col):
    Q1 = group[col].quantile(0.25)
    Q3 = group[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return group[(group[col] >= lower_bound) & (group[col] <= upper_bound)]

df = df.groupby('state', group_keys=False).apply(lambda g: remove_outliers(g, 'incident_rate'))
df = df.groupby('state', group_keys=False).apply(lambda g: remove_outliers(g, 'severity_index'))

#####
#Graphing
#####

#Layout for task 1
def tab1(prefix="task1"):
    return html.Div([
        html.H1("Geographical Analysis", style={"width": "100%","font-size": "20px","font-weight": "bold", "pointer-events":"none"}),
        html.P([
    "This page provides a geographical analysis of workplace incidents and industry-related data across different U.S. states. ",
    "The dropdown menu can be used to select different variables for analysis, including incident rate, severity index, employee exposure rate, and the number of companies in each state. ",
    "The interactive choropleth map displays the selected variable across states, offering insights into regional trends and patterns. "
]),

        #Dropdown menu
        html.Div([
            html.Label("Select a variable to visualize:"),
            dcc.Dropdown(
                id=f"task1-variable-dropdown",  
                options=[
                    {"label": "Incident Rate", "value": "incident_rate"},
                    {"label": "Severity Index", "value": "severity_index"},
                    {"label": "Employee Exposure Rate", "value": "employee_exposure_rate"},
                    {"label": "Number of Companies", "value": "num_companies_in_state"},
                ],
                value="incident_rate",  
                style={"width": "80%"}
            ),
        ], style={"padding": "10px"}),

        #Map container
        html.Div([
            dcc.Graph(
                id="task1-choropleth-map",
                style={
                    "height": "100vh",
                    "width": "100%"
                }
            )
        ], style={
            "padding": "10px",
            "margin": "5px",
            "height": "100vh"
        })
    ], style={
        "display": "flex",
        "flexDirection": "column",
        "height": "100vh",
        "width": "100%"
    }) 


#####
#Callbacks
#####

def register_task1_callbacks(app):
    @app.callback(
        Output('task1-choropleth-map', 'figure'),
        [Input('task1-variable-dropdown', 'value')]
    )
    def update_task1_map(selected_variable):
        try:
            #Data aggregation
            state_level_data = df.groupby('state').agg({
                'incident_rate': 'mean',
                'severity_index': 'mean',
                'employee_exposure_rate': 'mean',
                'num_companies_in_state': 'first',
                'state_full_name': 'first'
            }).reset_index()

            #Choropleth map
            fig = px.choropleth(
                state_level_data,
                locations="state",  #State codes
                locationmode="USA-states",  #State-level boundaries
                color=selected_variable,  #Variable to visualize
                scope="usa",  #Map of USA
                hover_data=["state_full_name"], 
                labels={
                    "incident_rate": "Incident Rate",
                    "severity_index": "Severity Index",
                    "employee_exposure_rate": "Employee Exposure Rate",
                    "num_companies_in_state": "Number of Companies",
                    "state_full_name": "State"
                }
            )

            #Update map layout
            fig.update_layout(
                geo=dict(
                    projection_scale=1,  
                    showframe=False,  
                    showcoastlines=True,  
                    center=dict(lat=37.0902, lon=-95.7129),  
                ),
                margin={"r": 0, "t": 30, "l": 0, "b": 0},  #Margins around the map
            )

            return fig

        except Exception as e:
            print(f"Error in callback: {str(e)}")
            return px.choropleth(scope="usa")

