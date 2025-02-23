import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from jbi100_app.data import get_data


df = get_data()

#####
#Preprocessing
#####

sector_mapping = {
        "11": "Agriculture, Forestry, Fishing and Hunting (NAICS 11)",
        "21": "Mining, Quarrying, and Oil and Gas Extraction (NAICS 21)",
        "22": "Utilities (NAICS 22)",
        "23": "Construction (NAICS 23)",
        "31": "Manufacturing (NAICS 31)",
        "32": "Manufacturing (NAICS 32)",
        "33": "Manufacturing (NAICS 33)",
        "42": "Wholesale Trade (NAICS 42)",
        "44": "Retail Trade (NAICS 44)",
        "45": "Retail Trade (NAICS 45)",
        "48": "Transportation and Warehousing (NAICS 48)",
        "49": "Transportation and Warehousing (NAICS 49)",
        "51": "Information (NAICS 51)",
        "52": "Finance and Insurance (NAICS 52)",
        "53": "Real Estate and Rental and Leasing (NAICS 53)",
        "54": "Professional, Scientific, and Technical Services (NAICS 54)",
        "55": "Management of Companies and Enterprises (NAICS 55)",
        "56": "Administrative and Support Services (NAICS 56)",
        "61": "Educational Services (NAICS 61)",
        "62": "Health Care and Social Assistance (NAICS 62)",
        "71": "Arts, Entertainment, and Recreation (NAICS 71)",
        "72": "Accommodation and Food Services (NAICS 72)",
        "81": "Other Services (except Public Administration) (NAICS 81)",
        "92": "Public Administration (NAICS 92)"
    }

#Keep only rows where 'industry_group' is a valid key
df = df[df["industry_group"].isin(sector_mapping.keys())]

incident_mapping = {
    1: "Injury",
    2: "Skin disorder",
    3: "Respiratory condition",
    4: "Poisoning",
    5: "Hearing Loss",
    6: "All other illness"
}

incident_colors = {
    "Injury": "#1f77b4",  #Blue
    "Skin Disorder": "#ff7f0e",  #Orange
    "Respiratory Condition": "#2ca02c",  #Green
    "Poisoning": "#d62728",  #Red
    "Hearing Loss": "#9467bd",  #Purple
    "Other Illness": "#8c564b"  #Brown
}

industry_options = [{"label": "Select All", "value": "all"}] + [
                    {"label": sector_mapping.get(str(code), code), "value": code}
                    for code in sorted(df["industry_group"].unique())]

incident_options = [{"label": "Select All", "value": "all"}] + [
                    {"label": "Injury", "value": 1},
                    {"label": "Skin disorder", "value": 2},
                    {"label": "Respiratory condition", "value": 3},
                    {"label": "Poisoning", "value": 4},
                    {"label": "Hearing Loss", "value": 5},
                    {"label": "All other illness", "value": 6}]

#####
#Graphing
#####

#layout for Task 2
def tab2():
    return html.Div([
        html.H1("Injury Types across Industries", style={"width": "100%","font-size": "20px","font-weight": "bold", "pointer-events":"none"}),

        html.P([
    "Explore the distribution of injuries and illnesses across different industry groups. Companies are categorized into industries using the North American Industry Classification System (NAICS). ",
    "Use the filters below to refine your view based on severity index, industry group, and incident type. More information about NAICS codes can be found on the ",
    html.A("official NAICS website", href="https://www.census.gov/naics/?58967?yearbck=2022", target="_blank"),
    "."
]),

#Filters
        html.Div([
            html.Label("Filter by Severity Index:"),
            dcc.Slider(
                id="task2-severity-slider",
                min=df["severity_index"].min(),
                max=df["severity_index"].max(),
                step=0.1,
                value=df["severity_index"].max(), #default to max severity indrx
                marks={i: f"{i:.1f}" for i in range(int(df["severity_index"].min()), int(df["severity_index"].max()) + 1)}
            ),
            html.Label("Filter by Industry Group:"),
            dcc.Dropdown(
                id="task2-industry-dropdown",
                options=industry_options,
                value=[],  
                multi=True,  #multiple selections
            ),
            html.Label("Filter by Incident Type:"),
            dcc.Dropdown(
                id="task2-incident-dropdown",
                options=incident_options,
                value=[], 
                multi=True, 
            ),
        ], style={"padding": "10px"}),

        #Stacked Bar Chart for Grouped Industries
        dcc.Graph(id="task2-main-bar-chart"),

        #Stacked Bar Chart for Sub-Industries
        dcc.Graph(id="task2-drilldown-bar-chart", style={"margin-top": "20px"})
    ])


#####
#Callbacks
#####

def register_task2_callbacks(app):

    @app.callback(
    Output("task2-industry-dropdown", "value"),
    [Input("task2-industry-dropdown", "value")]
)
    def update_industry_dropdown(selected_values):
        if "all" in selected_values:
            #Select All otion
            return [opt["value"] for opt in industry_options if opt["value"] != "all"]
        return selected_values  

    @app.callback(
        Output("task2-incident-dropdown", "value"),
        [Input("task2-incident-dropdown", "value")]
    )
    def update_incident_dropdown(selected_values):
        #Select All option
        if "all" in selected_values:
            return [opt["value"] for opt in incident_options if opt["value"] != "all"]
        return selected_values 


    @app.callback(
        Output("task2-main-bar-chart", "figure"),
        [
            Input("task2-severity-slider", "value"),
            Input("task2-industry-dropdown", "value"),
            Input("task2-incident-dropdown", "value"),
        ]
    )
    def update_main_bar_chart(severity, industry_filter, incident_filter):
        #Filter data
        filtered_df = df[df["severity_index"] <= severity]
        if industry_filter:
            filtered_df = filtered_df[filtered_df["industry_group"].isin(industry_filter)]
        if incident_filter:
            filtered_df = filtered_df[filtered_df["type_of_incident"].isin(incident_filter)]

        #Map incidents 
        #Aggregate data
        filtered_df["type_of_incident"] = filtered_df["type_of_incident"].map(incident_mapping).fillna("Unknown Incident")
        main_data = (
            filtered_df.groupby(["industry_group", "type_of_incident"])
            .size()
            .reset_index(name="count")
        )

        #Stacked bar chart
        return px.bar(
            main_data,
            x="industry_group",
            y="count",
            color="type_of_incident",
            color_discrete_map=incident_colors,
            title="Injuries and Illnesses by Industry Group",
            labels={
                "industry_group": "Industry Group",
                "count": "Incident Count",
                "type_of_incident": "Incident Type"
            }
        )

    @app.callback(
    Output("task2-drilldown-bar-chart", "figure"),
    [Input("task2-main-bar-chart", "clickData")]
)
    def update_drilldown_bar_chart(click_data):
        if not click_data:
            return px.bar(title="Click on a bar to drill down into sub-industries")
        selected_group = click_data["points"][0]["x"]

        #Filter data for the selected group
        drilldown_data = (
            df[df["industry_group"] == selected_group]
            .groupby(["naics_code", "type_of_incident"])
            .size()
            .reset_index(name="count")
        )
        drilldown_data["type_of_incident"] = drilldown_data["type_of_incident"].map(incident_mapping).fillna("Unknown Incident")
        drilldown_data["naics_code"] = drilldown_data["naics_code"].astype(str)

        #Drilldown stacked bar chart
        fig = px.bar(
            drilldown_data,
            x="naics_code",  
            y="count",
            color="type_of_incident",
            color_discrete_map=incident_colors,
            title=f"Injuries and Illnesses in Industry Group: {sector_mapping[selected_group]}",
            labels={
                "naics_code": "Sub-Industry (NAICS)",
                "count": "Incident Count",
                "type_of_incident": "Incident Type"
            }
        )

        return fig

