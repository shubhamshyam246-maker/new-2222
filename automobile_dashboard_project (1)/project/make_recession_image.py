"""
Creates RecessionReportgraphs.png - the four graphs shown by the dashboard when
'Recession Period Statistics' is selected.

Run:  python make_recession_image.py
Needs: pandas, requests, plotly, matplotlib  (kaleido + Chrome optional)

Prefer a real screenshot of the running dashboard if your course asks for one;
this script is a fallback that draws the same four graphs from the real data.
"""

import io

import pandas as pd
import requests

URL = ("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
       "IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/"
       "historical_automobile_sales.csv")
OUT = "RecessionReportgraphs.png"

r = requests.get(URL, timeout=30)
r.raise_for_status()
data = pd.read_csv(io.StringIO(r.text))
data = data.rename(columns={"unemployment_rate": "Unemployment_Rate"})
rec = data[data["Recession"] == 1]

# Same aggregations as the dashboard callback
yearly = rec.groupby("Year")["Automobile_Sales"].mean().reset_index()
by_type = rec.groupby("Vehicle_Type")["Automobile_Sales"].mean().reset_index()
adv = rec.groupby("Vehicle_Type")["Advertising_Expenditure"].sum().reset_index()
unemp = (rec.groupby(["Unemployment_Rate", "Vehicle_Type"])["Automobile_Sales"]
         .mean().reset_index())

T1 = "Average Automobile Sales fluctuation over Recession Period"
T2 = "Average Number of Vehicles Sold by Vehicle Type during Recession"
T3 = "Total Advertising Expenditure Share by Vehicle Type during Recession"
T4 = "Effect of Unemployment Rate on Vehicle Type and Sales"


def with_plotly():
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    fig = make_subplots(
        rows=2, cols=2, subplot_titles=(T1, T2, T3, T4),
        specs=[[{"type": "xy"}, {"type": "xy"}], [{"type": "domain"}, {"type": "xy"}]])
    fig.add_trace(go.Scatter(x=yearly["Year"], y=yearly["Automobile_Sales"],
                             mode="lines+markers", showlegend=False), 1, 1)
    fig.add_trace(go.Bar(x=by_type["Vehicle_Type"], y=by_type["Automobile_Sales"],
                         showlegend=False), 1, 2)
    fig.add_trace(go.Pie(labels=adv["Vehicle_Type"],
                         values=adv["Advertising_Expenditure"]), 2, 1)
    for vt, g in unemp.groupby("Vehicle_Type"):
        fig.add_trace(go.Bar(x=g["Unemployment_Rate"], y=g["Automobile_Sales"],
                             name=vt), 2, 2)
    fig.update_layout(barmode="stack",
                      title_text="Automobile Sales Statistics Dashboard - "
                                 "Recession Period Statistics",
                      height=900, width=1500)
    fig.write_image(OUT)


def with_matplotlib():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(2, 2, figsize=(16, 10))
    ax[0, 0].plot(yearly["Year"], yearly["Automobile_Sales"], marker="o")
    ax[0, 0].set(title=T1, xlabel="Year", ylabel="Automobile_Sales")
    ax[0, 1].bar(by_type["Vehicle_Type"], by_type["Automobile_Sales"])
    ax[0, 1].set(title=T2, ylabel="Automobile_Sales")
    ax[0, 1].tick_params(axis="x", rotation=20)
    ax[1, 0].pie(adv["Advertising_Expenditure"], labels=adv["Vehicle_Type"],
                 autopct="%1.1f%%")
    ax[1, 0].set_title(T3)
    pv = unemp.pivot_table(index="Unemployment_Rate", columns="Vehicle_Type",
                           values="Automobile_Sales", fill_value=0)
    bottom = pd.Series(0.0, index=pv.index)
    xs = range(len(pv))
    for col in pv.columns:
        ax[1, 1].bar(xs, pv[col], bottom=bottom.values, label=col)
        bottom += pv[col]
    ax[1, 1].set_xticks(list(xs)[::max(1, len(pv) // 10)])
    ax[1, 1].set_xticklabels(pv.index[::max(1, len(pv) // 10)], rotation=45)
    ax[1, 1].set(title=T4, xlabel="Unemployment Rate",
                 ylabel="Automobile_Sales")
    ax[1, 1].legend(fontsize=8)
    fig.suptitle("Automobile Sales Statistics Dashboard - "
                 "Recession Period Statistics", fontsize=16)
    fig.tight_layout()
    fig.savefig(OUT, dpi=110)


try:
    with_plotly()
    print(f"Saved {OUT} (plotly)")
except Exception as e:  # kaleido/Chrome missing
    print("Plotly export unavailable, using matplotlib instead.")
    with_matplotlib()
    print(f"Saved {OUT} (matplotlib)")
