import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from jbi100_app.data import get_data

#####
#Preprocessing
#####

#Get data
df = get_data()

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

df = df[df["industry_group"].isin(sector_mapping.keys())]

#Create industry dropdown options
industry_options = [{"label": sector_mapping[k], "value": k} for k in sector_mapping.keys()]

#Layout of task
def tab5():
    return html.Div([
        html.H1("Outlier Companies", style={"width": "100%","font-size": "20px","font-weight": "bold", "pointer-events":"none"}),
        html.P([
    "This page provides an analysis of outlier companies in terms of workplace incidents, grouped by industry according to the NAICS classification system. ",
    "Companies are categorized into industries based on the NAICS codes, which can be explored further at ",
    html.A("the official NAICS website", href="https://www.census.gov/naics/?58967?yearbck=2022", target="_blank"),
    ". By selecting an industry, the view can be refined to focus on certain sectors. Clicking on a company in the scatter plot reveals a historical trend of its incident rates over time."
]),

        #Industry Filter
        html.Label("Select Industry Group:"),
        dcc.Dropdown(
            id="task5-industry-dropdown",
            options=industry_options,
            value=[],  # Default choice
            multi=True
        ),

        #Scatter Plot for Outliers Only
        dcc.Graph(id="task5-outlier-plot"),

        #Line Chart
        dcc.Graph(id="task5-line-chart")
    ])

#####
#Callbacks
#####

def register_task5_callbacks(app):
    @app.callback(
        Output("task5-outlier-plot", "figure"),
        [Input("task5-industry-dropdown", "value")]
    )
    def update_outlier_plot(selected_industries):
        if not selected_industries: 
            return px.scatter(title="Select at least one industry")

        #Ensure selected_industries is always a list
        if isinstance(selected_industries, str):  
            selected_industries = [selected_industries]

        #Filter the dataset by selected industries
        filtered_df = df[df["industry_group"].isin(selected_industries)]

        #Compute percentiles for outliers
        lower_threshold = filtered_df["incident_rate"].quantile(0.05)
        upper_threshold = filtered_df["incident_rate"].quantile(0.95)

        #Keep only extreme outliers - based on percentiles
        outliers_df = filtered_df[
            (filtered_df["incident_rate"] <= lower_threshold) | 
            (filtered_df["incident_rate"] >= upper_threshold)
        ]

        #Map industry codes to names
        outliers_df["industry_name"] = outliers_df["industry_group"].map(sector_mapping)

        #graph scatter plot for outliers
        fig = px.scatter(
            outliers_df,
            x="industry_group",
            y="incident_rate",
            color="industry_name",
            title="Top 5% Outliers: Incident Rate Distribution by Industry",
            labels={"industry_group": "Industry Group", "incident_rate": "Incident Rate", "industry_name": "Industry Name", 
                    "company_name": "Company Name", "severity_index": "Severity Index"},
            hover_data=["company_name", "severity_index"]
        )
        return fig

    @app.callback(
        Output("task5-line-chart", "figure"),
        [Input("task5-outlier-plot", "clickData")]
    )
    def update_line_chart(click_data):
        if not click_data:
            return px.line(title="Select a company to view its incident rate history")

        selected_company = click_data["points"][0]["customdata"][0]  
        company_data = df[df["company_name"] == selected_company]

        #Keep only max incident rate per day
        company_data = company_data.loc[company_data.groupby("date_of_incident")['incident_rate'].idxmax()]
        company_data = company_data.sort_values(by="date_of_incident")

        #graph line chart
        fig = px.line(
            company_data,
            x="date_of_incident", 
            y="incident_rate",
            title=f"Incident Rate of {selected_company} in 2023",
            labels={"date_of_incident": "Incident Date", "incident_rate": "Incident Rate"},
            markers=True
        )
        return fig

