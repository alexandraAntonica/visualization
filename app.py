import dash
from dash import dcc, html 
from dash.dependencies import Input, Output
from jbi100_app.task1 import tab1, register_task1_callbacks
from jbi100_app.task2 import tab2, register_task2_callbacks
from jbi100_app.task3 import tab3, register_task3_callbacks
from jbi100_app.task5 import tab5, register_task5_callbacks
from jbi100_app.task6 import tab6, register_task6_callbacks
from jbi100_app.data import get_data


#Load data
df = get_data()

#Initialize app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

menu_style = {
    "display": "flex",  
    "flex-direction": "column",  
    "border": "1px solid lightgray",
    "width": "200px",  
    "height": "100vh",  
    "position": "fixed",  
    "top": "0",  
    "left": "0",  
    "padding": "20px",
    "background-color": "#f9f9f9",
    "z-index": "1000",  
    "overflow-y": "auto", 
}


title_style = {
    "top": "0",  
    "width": "100%",  #
    "background-color": "#f9f9f9",
    "padding": "15px",
    "box-shadow": "0px 4px 6px rgba(0, 0, 0, 0.1)",
    "z-index": "1000",  
}

tab_style = {
    "width": "100%",
    "padding": "10px",
    "border": "1px solid lightgray",
    "text-align": "left",
    "font-size": "14px",
    "background-color": "#f9f9f9",
    "cursor": "pointer",
}

selected_tab_style = {
    "width": "100%",
    "padding": "10px",
    "border": "1px solid lightgray",
    "text-align": "left",
    "font-size": "14px",
    "background-color": "#e6e6e6",  
    "font-weight": "bold",
    "color": "#000",
}

#layout
app.layout = html.Div([
    html.Div([
    html.Div(
        html.H1("Work Injuries Visualization Tool", style={"text-align": "center"}),
        style=title_style,
    ),

    #Main content area
    html.Div([
        #Sidebar menu
        html.Div([
            dcc.Tabs(
                id="tabs",
                value="tab1",  #Default tab
                children=[
                    dcc.Tab(label="Menu", style={"width": "100%","font-size": "20px","font-weight": "bold", "pointer-events":"none"}),
                    dcc.Tab(label="Geographical Analysis", value="tab1", style=tab_style, selected_style=selected_tab_style),
                    dcc.Tab(label="Injuries across Industries", value="tab2", style=tab_style, selected_style=selected_tab_style),
                    dcc.Tab(label="Company Size and Injuries", value="tab3", style=tab_style, selected_style=selected_tab_style),
                    dcc.Tab(label="Outlier Companies", value="tab5", style=tab_style, selected_style=selected_tab_style),
                    dcc.Tab(label="Multivariate Relationships", value="tab6", style=tab_style, selected_style=selected_tab_style),
                ],
                style=menu_style,
            ),
        ], style={"width": "220px"}),

        html.Div(
            id="content", 
            style={
                "marginLeft": "100px",  #
                "flex": 1,
                "padding": "20px",
                "minHeight": "100vh",
                "width": "calc(100% - 100px)"  
            },
        ),
    ], style={
        "display": "flex",
        "width": "100%",
        "height": "100vh",
        "margin": 0,
        "padding": 0
    })
])
])

#Callback to Render Tab Content
@app.callback(
    dash.dependencies.Output('content', 'children'),
    [dash.dependencies.Input('tabs', 'value')]
)
def render_content(tab):
    if tab == 'tab1':
        return tab1()
    elif tab == 'tab2':
        return tab2()
    elif tab == 'tab3':
        return tab3()
    elif tab == 'tab5':
        return tab5()
    elif tab == 'tab6':
        return tab6()
    elif tab == 'tab7':
        return tab7()
    
register_task1_callbacks(app)
register_task2_callbacks(app)
register_task3_callbacks(app)
register_task5_callbacks(app)
register_task6_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True, port=5050)

