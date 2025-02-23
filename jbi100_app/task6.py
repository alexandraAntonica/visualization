import dash
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output
from jbi100_app.data import get_data 

df = get_data()

#Mapping SOC codes to job categories
soc_mapping = {
    "11": "Management Occupations",
    "13": "Business and Financial Operations",
    "15": "Computer and Mathematical",
    "17": "Architecture and Engineering",
    "19": "Life, Physical, and Social Science",
    "21": "Community and Social Services",
    "23": "Legal",
    "25": "Education and Library",
    "27": "Arts, Design, Entertainment, Sports",
    "29": "Healthcare Practitioners",
    "31": "Healthcare Support",
    "33": "Protective Services",
    "35": "Food Preparation and Serving",
    "37": "Building and Grounds Cleaning",
    "39": "Personal Care and Service",
    "41": "Sales and Related",
    "43": "Office and Administrative Support",
    "45": "Farming, Fishing, and Forestry",
    "47": "Construction and Extraction",
    "49": "Installation, Maintenance, and Repair",
    "51": "Production Occupations",
    "53": "Transportation and Material Moving"
}
df["job_category_id"] = df["soc_code"].str[:2].astype(int)
df["job_category"] = df["soc_code"].str[:2].map(soc_mapping)

#Aggregate data for parallel coordinates plot
pcp_df = df.groupby("job_category").agg(
    job_category_id=("job_category_id", "first"),  
    incident_rate=("incident_rate", "mean"),
    severity_index=("severity_index", "mean"),
    employee_exposure_rate=("employee_exposure_rate", "mean")
).reset_index()

def tab6():
    return html.Div([
        html.H1("Multivariate Analysis Across Job", style={"width": "100%","font-size": "20px","font-weight": "bold", "pointer-events":"none"}),
        html.P([
    "This page provides a multivariate analysis of job categories using the Standard Occupational Classification (SOC) system. ",
    "Jobs are grouped into broader occupational categories based on SOC codes, which provide standardized occupation profiles. ",
    "For more details about SOC codes and classifications, visit ",
    html.A("the official Bureau of Labor Statistics website", href="https://www.bls.gov/oes/current/oes_stru.htm", target="_blank"),
    ". Use the dropdown menu to filter specific job categories and analyze their corresponding workplace risk factors."
]),
        html.Label("Select Job Category:"),
        dcc.Dropdown(
            id="category-dropdown",
            options=[{"label": "Select All", "value": "All"}] +
                    [{"label": v, "value": v} for v in soc_mapping.values()],
            value="All",
            multi=True
        ),
        dcc.Graph(id="pcp-graph")
    ])

#####
#Callbacks
#####

def register_task6_callbacks(app):
    @app.callback(
        Output("pcp-graph", "figure"),
        Input("category-dropdown", "value")
    )
    def update_graph(selected_categories):
        if not selected_categories or "All" in selected_categories:
            filtered_df = pcp_df.copy()
            legend_categories = list(soc_mapping.values())
        else:
            filtered_df = pcp_df[pcp_df["job_category"].isin(selected_categories)].copy()
            legend_categories = selected_categories
        
        if filtered_df.empty:
            return px.parallel_coordinates(filtered_df, dimensions=["incident_rate", "severity_index", "employee_exposure_rate"])
        
        fig = px.parallel_coordinates(
            filtered_df,
            dimensions=["incident_rate", "severity_index", "employee_exposure_rate"],
            color="job_category_id",  #Color mapping based on IDs
            color_continuous_scale=px.colors.sequential.Viridis,  
            labels={"incident_rate": "Incident Rate", "severity_index": "Severity Index", "employee_exposure_rate": "Exposure Rate",
                    "job_category_id": "Job Category"}
        )
        
        #Colorbar for job categories
        selected_category_ids = [int(k) for k, v in soc_mapping.items() if v in legend_categories]
        fig.update_layout(
            coloraxis_colorbar=dict(
                tickmode="array",
                tickvals=selected_category_ids,
                ticktext=legend_categories),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        return fig
