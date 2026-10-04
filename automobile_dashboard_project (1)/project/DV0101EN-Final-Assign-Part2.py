"""
Final Assignment: Part 2 - Create Dashboard with Plotly and Dash
Automobile Sales Statistics Dashboard

Run:  python DV0101EN-Final-Assign-Part2.py
Open: http://127.0.0.1:8050
"""

import io

import pandas as pd
import requests
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# ---------------------------------------------------------------------------
# Load the data
# ---------------------------------------------------------------------------
URL = ("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
       "IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/"
       "historical_automobile_sales.csv")

try:
    response = requests.get(URL, timeout=30)
    response.raise_for_status()
    data = pd.read_csv(io.StringIO(response.text))
except requests.RequestException:
    # Fallback: use a local copy of the file if the download fails
    data = pd.read_csv("historical_automobile_sales.csv")

# The unemployment column is spelled 'unemployment_rate' in some copies of the
# file and 'Unemployment_Rate' in others, so normalise it once here.
data = data.rename(columns={"unemployment_rate": "Unemployment_Rate"})

# ---------------------------------------------------------------------------
# Initialize the Dash app
# ---------------------------------------------------------------------------
app = dash.Dash(__name__)
app.title = "Automobile Statistics Dashboard"

# Dropdown options
dropdown_options = [
    {"label": "Yearly Statistics", "value": "Yearly Statistics"},
    {"label": "Recession Period Statistics", "value": "Recession Period Statistics"},
]

# List of years
year_list = [i for i in range(1980, 2024, 1)]

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
app.layout = html.Div([
    # TASK 2.1: Title of the dashboard
    html.H1(
        "Automobile Sales Statistics Dashboard",
        style={"textAlign": "center", "color": "#503D36", "fontSize": 24},
    ),

    html.Div([
        # TASK 2.2: Dropdown to select the report type
        html.Label("Select Statistics:"),
        dcc.Dropdown(
            id="dropdown-statistics",
            options=dropdown_options,
            value="Select Statistics",
            placeholder="Select a report type",
            style={"width": "80%", "padding": "3px", "fontSize": "20px",
                   "textAlignLast": "center"},
        ),
    ]),

    html.Div(
        # TASK 2.2: Dropdown to select the year
        dcc.Dropdown(
            id="select-year",
            options=[{"label": i, "value": i} for i in year_list],
            placeholder="Select-year",
            value="Select-year",
            style={"width": "80%", "padding": "3px", "fontSize": "20px",
                   "textAlignLast": "center"},
        )
    ),

    # TASK 2.3: Output container for the graphs
    html.Div([
        html.Div(
            id="output-container",
            className="chart-grid",
            style={"display": "flex", "flexDirection": "column"},
        )
    ]),
])


# ---------------------------------------------------------------------------
# TASK 2.4: Callback to enable/disable the year dropdown
# ---------------------------------------------------------------------------
@app.callback(
    Output(component_id="select-year", component_property="disabled"),
    Input(component_id="dropdown-statistics", component_property="value"),
)
def update_input_container(selected_statistics):
    # Year selection is only meaningful for "Yearly Statistics"
    if selected_statistics == "Yearly Statistics":
        return False
    return True


# ---------------------------------------------------------------------------
# TASK 2.5 / 2.6: Callback that creates the graphs
# ---------------------------------------------------------------------------
@app.callback(
    Output(component_id="output-container", component_property="children"),
    [Input(component_id="dropdown-statistics", component_property="value"),
     Input(component_id="select-year", component_property="value")],
)
def update_output_container(selected_statistics, input_year):
    # ------------------------- Recession Report ---------------------------
    if selected_statistics == "Recession Period Statistics":
        # Data for recession periods only
        recession_data = data[data["Recession"] == 1]

        # Plot 1: Line chart - average automobile sales fluctuation over
        # the recession years
        yearly_rec = (recession_data.groupby("Year")["Automobile_Sales"]
                      .mean().reset_index())
        R_chart1 = dcc.Graph(
            figure=px.line(
                yearly_rec, x="Year", y="Automobile_Sales",
                title="Average Automobile Sales fluctuation over Recession Period",
            )
        )

        # Plot 2: Bar chart - average number of vehicles sold by vehicle type
        average_sales = (recession_data.groupby("Vehicle_Type")["Automobile_Sales"]
                         .mean().reset_index())
        R_chart2 = dcc.Graph(
            figure=px.bar(
                average_sales, x="Vehicle_Type", y="Automobile_Sales",
                title="Average Number of Vehicles Sold by Vehicle Type "
                      "during Recession",
            )
        )

        # Plot 3: Pie chart - total expenditure share by vehicle type
        exp_rec = (recession_data.groupby("Vehicle_Type")["Advertising_Expenditure"]
                   .sum().reset_index())
        R_chart3 = dcc.Graph(
            figure=px.pie(
                exp_rec, values="Advertising_Expenditure", names="Vehicle_Type",
                title="Total Advertising Expenditure Share by Vehicle Type "
                      "during Recession",
            )
        )

        # Plot 4: Bar chart - effect of unemployment rate on vehicle type
        # and sales
        unemp_data = (recession_data
                      .groupby(["Unemployment_Rate", "Vehicle_Type"])
                      ["Automobile_Sales"].mean().reset_index())
        R_chart4 = dcc.Graph(
            figure=px.bar(
                unemp_data, x="Unemployment_Rate", y="Automobile_Sales",
                color="Vehicle_Type",
                labels={"Unemployment_Rate": "Unemployment Rate",
                        "Automobile_Sales": "Average Automobile Sales"},
                title="Effect of Unemployment Rate on Vehicle Type and Sales",
            )
        )

        return [
            html.Div(className="chart-item",
                     children=[html.Div(children=R_chart1),
                               html.Div(children=R_chart2)],
                     style={"display": "flex"}),
            html.Div(className="chart-item",
                     children=[html.Div(children=R_chart3),
                               html.Div(children=R_chart4)],
                     style={"display": "flex"}),
        ]

    # --------------------------- Yearly Report ----------------------------
    elif (input_year in year_list) and (selected_statistics == "Yearly Statistics"):
        yearly_data = data[data["Year"] == input_year]

        # Plot 1: Line chart - yearly average automobile sales (all years)
        yas = data.groupby("Year")["Automobile_Sales"].mean().reset_index()
        Y_chart1 = dcc.Graph(
            figure=px.line(
                yas, x="Year", y="Automobile_Sales",
                title="Yearly Average Automobile Sales (1980 - 2023)",
            )
        )

        # Plot 2: Line chart - total monthly automobile sales for the year
        mas = yearly_data.groupby("Month")["Automobile_Sales"].sum().reset_index()
        Y_chart2 = dcc.Graph(
            figure=px.line(
                mas, x="Month", y="Automobile_Sales",
                title=f"Total Monthly Automobile Sales in {input_year}",
            )
        )

        # Plot 3: Bar chart - average vehicles sold by vehicle type in the year
        avr_vdata = (yearly_data.groupby("Vehicle_Type")["Automobile_Sales"]
                     .mean().reset_index())
        Y_chart3 = dcc.Graph(
            figure=px.bar(
                avr_vdata, x="Vehicle_Type", y="Automobile_Sales",
                title=f"Average Vehicles Sold by Vehicle Type in the year "
                      f"{input_year}",
            )
        )

        # Plot 4: Pie chart - total advertisement expenditure by vehicle type
        exp_data = (yearly_data.groupby("Vehicle_Type")["Advertising_Expenditure"]
                    .sum().reset_index())
        Y_chart4 = dcc.Graph(
            figure=px.pie(
                exp_data, values="Advertising_Expenditure", names="Vehicle_Type",
                title=f"Total Advertisement Expenditure for Each Vehicle "
                      f"in {input_year}",
            )
        )

        return [
            html.Div(className="chart-item",
                     children=[html.Div(children=Y_chart1),
                               html.Div(children=Y_chart2)],
                     style={"display": "flex"}),
            html.Div(className="chart-item",
                     children=[html.Div(children=Y_chart3),
                               html.Div(children=Y_chart4)],
                     style={"display": "flex"}),
        ]

    # Nothing selected yet
    return None


# ---------------------------------------------------------------------------
# Run the app
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
