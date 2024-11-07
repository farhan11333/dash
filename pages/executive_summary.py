import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd
import numpy as np

# Dummy data (replace with actual data loading)
df = pd.DataFrame({
    'Date': pd.date_range(start='2023-01-01', end='2023-12-31', freq='D'),
    'Leads': np.random.randint(50, 200, 365),
    'TCRs': np.random.randint(10, 50, 365),
    'Sales': np.random.randint(100000, 1000000, 365)
})

layout = html.Div([
    html.H1("Executive Summary"),
    
    # KPIs
    html.Div([
        html.Div([
            html.H3("Total Leads"),
            html.H2(f"{df['Leads'].sum():,}")
        ], className="kpi-card"),
        html.Div([
            html.H3("Total TCRs"),
            html.H2(f"{df['TCRs'].sum():,}")
        ], className="kpi-card"),
        html.Div([
            html.H3("Total Sales Volume"),
            html.H2(f"${df['Sales'].sum():,.0f}")
        ], className="kpi-card"),
    ], className="kpi-container"),
    
    # Trend Overview
    html.Div([
        dcc.Graph(
            figure=px.line(df, x='Date', y=['Leads', 'TCRs'], title="Leads and TCRs Over Time")
        ),
        dcc.Graph(
            figure=px.line(df, x='Date', y='Sales', title="Sales Volume Trend")
        )
    ], className="chart-container")
])
