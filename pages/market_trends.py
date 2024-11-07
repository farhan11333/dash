# pages/sales_dashboard.py

import pandas as pd
from dash import html, dcc, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc

# Load and preprocess data
df = pd.read_excel('data/Prime_TCR.xls')

# Data Preprocessing
df.columns = df.columns.str.strip()
df['Contracted Date'] = pd.to_datetime(df['Contracted Date'], errors='coerce')
df['Lead Creation Date'] = pd.to_datetime(df['Lead Creation Date'], errors='coerce')
df['Time to Contract'] = (df['Contracted Date'] - df['Lead Creation Date']).dt.days
df['Commission Ratio'] = pd.to_numeric(df['Commission Ratio'], errors='coerce')
df['Sales Volume'] = pd.to_numeric(df['Sales Volume'], errors='coerce')

# Theme colors matching agent_performance
theme_colors = {
    'primary': '#1A237E',  # Deep indigo
    'secondary': '#00BFA5', # Teal accent
    'background': '#0A192F', # Dark blue background
    'text': '#FFFFFF',      # White text
    'accent1': '#64FFDA',   # Bright teal accent
    'accent2': '#7C4DFF',   # Purple accent
    'card_bg': '#172A45',   # Slightly lighter blue for cards
    'grid': '#233554'       # Grid lines color
}

# Enhanced chart template
chart_template = {
    'layout': {
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {'color': theme_colors['text'], 'family': 'Roboto'},
        'title': {
            'font': {'size': 24, 'color': theme_colors['accent1']},
            'x': 0.5,
            'xanchor': 'center'
        },
        'xaxis': {
            'gridcolor': theme_colors['grid'],
            'linecolor': theme_colors['grid'],
            'zerolinecolor': theme_colors['grid']
        },
        'yaxis': {
            'gridcolor': theme_colors['grid'],
            'linecolor': theme_colors['grid'],
            'zerolinecolor': theme_colors['grid']
        }
    }
}

# Define the layout
layout = dbc.Container([
    html.H1("Sales Transaction Dashboard", 
            className="text-center my-4",
            style={'color': theme_colors['accent1']}),

    # Filters
    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label('Select Owner:', className="fw-bold mb-2", style={'color': theme_colors['text']}),
                    dcc.Dropdown(
                        id='owner-filter',
                        options=[{'label': owner, 'value': owner} for owner in df['Owner'].dropna().unique()],
                        value=[],
                        multi=True,
                        className="w-100"
                    )
                ], width=6),
                dbc.Col([
                    html.Label('Select Date Range:', className="fw-bold mb-2", style={'color': theme_colors['text']}),
                    dcc.DatePickerRange(
                        id='date-filter',
                        start_date=df['Contracted Date'].min(),
                        end_date=df['Contracted Date'].max(),
                        className="w-100"
                    )
                ], width=6)
            ])
        ])
    ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["grid"]}'}, className="mb-4"),

    # KPIs
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody(id='total-sales')
            ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["accent1"]}'}, className="text-center h-100")
        ], width=12, md=4, className="mb-4"),
        dbc.Col([
            dbc.Card([
                dbc.CardBody(id='total-transactions')
            ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["accent1"]}'}, className="text-center h-100")
        ], width=12, md=4, className="mb-4"),
        dbc.Col([
            dbc.Card([
                dbc.CardBody(id='average-commission')
            ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["accent1"]}'}, className="text-center h-100")
        ], width=12, md=4, className="mb-4")
    ]),

    # Charts
    dbc.Tabs([
        dbc.Tab(label='Sales Overview', children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='sales-over-time')
                        ])
                    ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["grid"]}'}, className="mb-4")
                ], width=12),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='top-agents')
                        ])
                    ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["grid"]}'}, className="mb-4")
                ], width=12, lg=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='sales-by-project')
                        ])
                    ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["grid"]}'}, className="mb-4")
                ], width=12, lg=6)
            ])
        ], style={'color': theme_colors['text']}),
        dbc.Tab(label='Performance Analysis', children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='commission-distribution')
                        ])
                    ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["grid"]}'}, className="mb-4")
                ], width=12, lg=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='conversion-funnel')
                        ])
                    ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["grid"]}'}, className="mb-4")
                ], width=12, lg=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='time-to-contract')
                        ])
                    ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["grid"]}'}, className="mb-4")
                ], width=12)
            ])
        ], style={'color': theme_colors['text']}),
        dbc.Tab(label='Lead Source Analysis', children=[
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='sales-by-lead-source')
                ])
            ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["grid"]}'}, className="mb-4")
        ], style={'color': theme_colors['text']}),
        dbc.Tab(label='Correlation Analysis', children=[
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='correlation-matrix')
                ])
            ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["grid"]}'}, className="mb-4")
        ], style={'color': theme_colors['text']})
    ], className="mb-4"),
], fluid=True, style={'backgroundColor': theme_colors['background'], 'minHeight': '100vh', 'padding': '20px'})

@callback(
    [Output('total-sales', 'children'),
     Output('total-transactions', 'children'),
     Output('average-commission', 'children'),
     Output('sales-over-time', 'figure'),
     Output('top-agents', 'figure'),
     Output('sales-by-project', 'figure'),
     Output('commission-distribution', 'figure'),
     Output('conversion-funnel', 'figure'),
     Output('time-to-contract', 'figure'),
     Output('sales-by-lead-source', 'figure'),
     Output('correlation-matrix', 'figure')],
    [Input('owner-filter', 'value'),
     Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date')]
)
def update_dashboard(selected_owners, start_date, end_date):
    filtered_df = df.copy()

    # Apply filters
    if selected_owners:
        filtered_df = filtered_df[filtered_df['Owner'].isin(selected_owners)]
    if start_date and end_date:
        filtered_df = filtered_df[(filtered_df['Contracted Date'] >= start_date) & (filtered_df['Contracted Date'] <= end_date)]

    # KPIs
    total_sales_value = filtered_df['Sales Volume'].sum()
    total_sales = [
        html.H3(f"{total_sales_value:,.2f}", style={'color': theme_colors['accent1']}, className="mb-0"),
        html.P("Total Sales Volume", style={'color': theme_colors['text']}, className="mb-0")
    ]

    total_transactions_value = len(filtered_df)
    total_transactions = [
        html.H3(f"{total_transactions_value}", style={'color': theme_colors['accent1']}, className="mb-0"),
        html.P("Total Transactions", style={'color': theme_colors['text']}, className="mb-0")
    ]

    average_commission_value = filtered_df['Commission Ratio'].mean()
    average_commission = [
        html.H3(f"{average_commission_value:.2%}", style={'color': theme_colors['accent1']}, className="mb-0"),
        html.P("Average Commission Ratio", style={'color': theme_colors['text']}, className="mb-0")
    ]

    # Sales Over Time
    sales_over_time = filtered_df.groupby(pd.Grouper(key='Contracted Date', freq='M'))['Sales Volume'].sum().reset_index()
    fig_sales_over_time = px.line(sales_over_time, x='Contracted Date', y='Sales Volume', 
                                 title='Sales Volume Over Time')
    fig_sales_over_time.update_layout(template=chart_template)

    # Top Agents
    top_agents = filtered_df.groupby('Owner')['Sales Volume'].sum().reset_index().sort_values(by='Sales Volume', ascending=False).head(10)
    fig_top_agents = px.bar(top_agents, x='Owner', y='Sales Volume', 
                           title='Top 10 Agents by Sales Volume')
    fig_top_agents.update_layout(template=chart_template)

    # Sales by Project
    fig_sales_by_project = px.treemap(filtered_df, path=['Developer', 'Project'], values='Sales Volume', 
                                     title='Sales Volume by Project and Developer')
    fig_sales_by_project.update_layout(template=chart_template)

    # Commission Distribution
    fig_commission_distribution = px.histogram(filtered_df, x='Commission Ratio', nbins=20, 
                                             title='Distribution of Commission Ratios')
    fig_commission_distribution.update_layout(template=chart_template)

    # Conversion Funnel
    funnel_data = filtered_df['TCR Status'].value_counts().reset_index()
    funnel_data.columns = ['TCR Status', 'Count']
    fig_conversion_funnel = px.funnel(funnel_data, x='Count', y='TCR Status', 
                                     title='Lead Conversion Funnel')
    fig_conversion_funnel.update_layout(template=chart_template)

    # Time to Contract
    fig_time_to_contract = px.box(filtered_df, y='Time to Contract', 
                                 title='Time to Contract Analysis')
    fig_time_to_contract.update_layout(template=chart_template)

    # Sales by Lead Source
    sales_by_lead_source = filtered_df.groupby('Lead Source')['Sales Volume'].sum().reset_index()
    fig_sales_by_lead_source = px.bar(sales_by_lead_source, x='Lead Source', y='Sales Volume', 
                                     title='Sales Volume by Lead Source')
    fig_sales_by_lead_source.update_layout(template=chart_template)

    # Correlation Matrix
    correlation_data = filtered_df[['Sales Volume', 'Commission Ratio', 'Time to Contract']].corr()
    fig_correlation_matrix = px.imshow(correlation_data, text_auto=True, 
                                     title='Correlation Matrix')
    fig_correlation_matrix.update_layout(template=chart_template)

    return (total_sales, total_transactions, average_commission, fig_sales_over_time, 
            fig_top_agents, fig_sales_by_project, fig_commission_distribution, 
            fig_conversion_funnel, fig_time_to_contract, fig_sales_by_lead_source, 
            fig_correlation_matrix)
