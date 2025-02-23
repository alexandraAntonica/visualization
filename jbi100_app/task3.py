import plotly.express as px
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output
from jbi100_app.data import get_data



#Remove outliers since they heavily skew the plots
def remove_outliers(group):
    Q1 = group['incident_rate'].quantile(0.25)
    Q3 = group['incident_rate'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return group[
        (group['incident_rate'] >= lower_bound) & (group['incident_rate'] <= upper_bound)
    ]

#Get data
df_task3 = get_data()
df_task3 = df_task3.groupby('size_category', group_keys=False).apply(remove_outliers)
df_task3["year_month"] = df_task3["date_of_incident"].dt.to_period("M").astype(str)

incident_type_map = {
    1: "Injury",
    2: "Skin Disorder",
    3: "Respiratory Condition",
    4: "Poisoning",
    5: "Hearing Loss",
    6: "Other Illness"
}
#Fixed Colors for each Incident Type
incident_colors = {
    "Injury": "#1f77b4",  #Blue
    "Skin Disorder": "#ff7f0e",  #Orange
    "Respiratory Condition": "#2ca02c",  #Green
    "Poisoning": "#d62728",  #Red
    "Hearing Loss": "#9467bd",  #Purple
    "Other Illness": "#8c564b"  #Brown
}

df_task3["incident_type_label"] = df_task3["type_of_incident"].map(incident_type_map)

#####
#Graphing
#####

#Box and Whisker Plot
Violin = px.violin(
    df_task3,
    title="Distribution of Incident Rates by Establishment Size",
    x="size_category",
    y="incident_rate",
    color="size_category",
    hover_data=["company_name", "establishment_id", "state"],
    points=False,
    box=True,
    labels={
        "size_category": "Establishment Size Category",
        "incident_rate": "Incident Rate"
    }
)
Violin.update_layout(
    width=1200,
    height=700,
    margin=dict(l=40, r=40, t=60, b=40),
    paper_bgcolor="#f9f9f9",
    plot_bgcolor="white",
    xaxis=dict(categoryorder="category ascending")
)

#Different Bins
size_order = ["Small (0-19)", "Medium (20-99)", "Large (100-249)", "Huge (250+)"]
unique_sizes = [sz for sz in size_order if sz in df_task3["size_category"].unique()]

def tab3():
    return html.Div([
        html.H1("Company Size and Injuries", style={"width": "100%","font-size": "20px","font-weight": "bold", "pointer-events":"none"}),
        html.P(["Use the Violin plot to view the distribution of incident rates. Select a bin size to see the frequency of each incident type and how they changed over time."
]),
        html.Div(dcc.Graph(id="incident-rate-boxplot", figure=Violin), style={"text-align": "center"}),
        
        html.Div([
            html.Label("Select Establishment Size Category:", 
               style={"font-size": "20px", "font-weight": "bold", "margin-top": "20px"}),
            dcc.RadioItems(
                id="size-category-selector",
                options=[{"label": cat, "value": cat} for cat in unique_sizes],
                value=unique_sizes[0], 
                labelStyle={"display": "inline-block", "margin-right": "15px"}
            )
        ], style={"text-align": "center", "margin-top": "20px", "margin-bottom": "20px", "padding": "10px"
                  }),
        
        html.Div(dcc.Graph(id="incident-type-histogram"), style={"text-align": "center", "margin-top": "20px", "margin-bottom": "50px"}),
        
        html.Div(dcc.Graph(id="incident-trend-chart"), style={"text-align": "center", "margin-bottom": "50px"}),

        
    ])

#####
#Callbacks
#####

def register_task3_callbacks(app):
    @app.callback(
        Output("incident-type-histogram", "figure"),
        Input("size-category-selector", "value")
    )
    def update_histogram(selected_size):
        filtered_df = df_task3[df_task3["size_category"] == selected_size]

        #Count frequency of different incident types and sort them
        incident_counts = filtered_df["incident_type_label"].value_counts().reset_index()
        incident_counts.columns = ["Incident Type", "Count"]
        incident_counts = incident_counts.sort_values(by="Count", ascending=False) 

        #Graph Histogram
        fig = px.bar(
            incident_counts,
            x="Incident Type",
            y="Count",
            text="Count",
            title=f"Frequency of Incident Types in '{selected_size}' Category",
            color="Incident Type",
            color_discrete_map=incident_colors
        )
        fig.update_traces(texttemplate="%{text}", textposition="outside")
        fig.update_layout(
            xaxis_title="Incident Type",
            yaxis_title=" Incident Count",
            xaxis=dict(
                tickangle=-30,
                tickfont=dict(size=12),
                categoryorder="total descending"
            ),
            margin=dict(l=40, r=40, t=60, b=120),
            height=600,
            paper_bgcolor="#f9f9f9",
            plot_bgcolor="white"
        )
        return fig

    @app.callback(
        Output("incident-trend-chart", "figure"),
        Input("size-category-selector", "value")
    )
    def update_trend_chart(selected_size):
        filtered_df = df_task3[df_task3["size_category"] == selected_size]
        incident_trends = filtered_df.groupby(["year_month", "incident_type_label"]).size().reset_index(name="count")

        #Graph Line Chart
        fig = px.line(
            incident_trends,
            x="year_month",
            y="count",
            color="incident_type_label",
            title=f"Trend of Incident Types Over Time in '{selected_size}' Category",
            markers=True,
            color_discrete_map=incident_colors,
            labels={"year_month": "Incident Date", "count": "Incident Count", "incident_type_label": "Incident Type"}
        )
        fig.update_layout(
            xaxis_title="Incident Date",
            yaxis_title="Incident Count",
            margin=dict(l=40, r=40, t=60, b=120),
            height=600,
            paper_bgcolor="#f9f9f9",
            plot_bgcolor="white",
        )
        return fig
