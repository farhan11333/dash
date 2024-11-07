# lead_analysis.py

import dash
from dash import html, dcc, callback, Output, Input, State, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc

# Read the data from 'Leads_Info.xlsx'
df_leads = pd.read_excel('./data/Leads_Info.xlsx')

# Strip spaces from column names
df_leads.columns = df_leads.columns.str.strip()

# Data Preprocessing
df_leads['Creation Date'] = pd.to_datetime(df_leads['Creation Date'], errors='coerce')
df_leads['Request Date'] = pd.to_datetime(df_leads['Request Date'], errors='coerce')
df_leads['Budget From'] = pd.to_numeric(df_leads['Budget From'], errors='coerce')
df_leads['Budget To'] = pd.to_numeric(df_leads['Budget To'], errors='coerce')
df_leads.fillna({'Budget From': 0, 'Budget To': 0}, inplace=True)

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

# Calculate KPIs
total_leads = len(df_leads)
leads_by_status = df_leads['Lead Status'].value_counts()
leads_by_source = df_leads['Lead Source'].value_counts().reset_index()
leads_by_source.columns = ['Lead Source', 'count']
average_budget_from = df_leads['Budget From'].mean()
average_budget_to = df_leads['Budget To'].mean()

# Prepare data for initial charts
# Sunburst Chart
sunburst_data = df_leads.groupby(['Lead Source', 'Lead Status']).size().reset_index(name='count')
fig_sunburst = px.sunburst(
    sunburst_data,
    path=['Lead Source', 'Lead Status'],
    values='count',
    title='Lead Source and Status Breakdown'
)
fig_sunburst.update_layout(template=chart_template)

# Heatmap Chart (Budget vs. Property Type)
heatmap_data = df_leads.pivot_table(
    index='Property Type',
    columns='Lead Status',
    values='Budget From',
    aggfunc='mean'
)
fig_heatmap = px.imshow(
    heatmap_data,
    labels=dict(x="Lead Status", y="Property Type", color="Average Budget"),
    title="Average Budget Heatmap"
)
fig_heatmap.update_layout(template=chart_template)

# Bubble Chart (Budget vs. Property Type)
bubble_data = df_leads.copy()
bubble_data['Budget Average'] = (bubble_data['Budget From'] + bubble_data['Budget To']) / 2
fig_bubble = px.scatter(
    bubble_data,
    x='Budget Average',
    y='Property Type',
    size='Budget Average',
    color='Lead Status',
    hover_name='Lead Name',
    title='Budget vs. Property Type Bubble Chart'
)
fig_bubble.update_layout(template=chart_template)

# Treemap Chart (Leads by District and Property Type)
treemap_data = df_leads.groupby(['District Name', 'Property Type']).size().reset_index(name='count')
fig_treemap = px.treemap(
    treemap_data,
    path=['District Name', 'Property Type'],
    values='count',
    title='Leads Distribution Treemap'
)
fig_treemap.update_layout(template=chart_template)

# Funnel Chart (Lead Conversion Funnel)
funnel_stages = df_leads['Lead Status'].value_counts().reset_index()
funnel_stages.columns = ['Stage', 'Number of Leads']
fig_funnel = go.Figure(go.Funnel(
    y=funnel_stages['Stage'],
    x=funnel_stages['Number of Leads'],
    textinfo="value+percent initial"
))
fig_funnel.update_layout(template=chart_template, title='Lead Conversion Funnel')

# Calendar Heatmap (Leads per Day)
heatmap_counts = df_leads.copy()
heatmap_counts['Date'] = heatmap_counts['Creation Date'].dt.date
heatmap_counts = heatmap_counts.groupby('Date').size().reset_index(name='Leads')
fig_calendar_heatmap = px.density_heatmap(
    heatmap_counts,
    x='Date',
    y='Leads',
    nbinsx=30,
    title='Leads per Day Heatmap'
)
fig_calendar_heatmap.update_layout(template=chart_template)

# Define the layout variable
layout = dbc.Container([
    html.H1("Lead Analysis Dashboard", 
            className="text-center my-4", 
            style={'color': theme_colors['accent1'], 'font-family': 'Roboto', 'font-weight': '300'}),
    
    # Tabs with futuristic styling
    dbc.Tabs([
        dbc.Tab(label='Overview', children=[
            # KPIs Row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H3(f"{total_leads:,}", 
                                   className="text-center", 
                                   style={'color': theme_colors['accent1'], 'font-size': '2.5rem'}),
                            html.P("Total Leads", 
                                  className="text-center mb-0",
                                  style={'color': theme_colors['text']})
                        ])
                    ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["accent1"]}'})
                ], width=12, md=3, className="mb-4"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H3(f"${average_budget_from:,.0f} - ${average_budget_to:,.0f}", 
                                   className="text-center", 
                                   style={'color': theme_colors['accent1'], 'font-size': '2.5rem'}),
                            html.P("Average Budget Range", 
                                  className="text-center mb-0",
                                  style={'color': theme_colors['text']})
                        ])
                    ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["accent1"]}'})
                ], width=12, md=3, className="mb-4"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H3(f"{leads_by_status.idxmax()}", 
                                   className="text-center", 
                                   style={'color': theme_colors['accent1'], 'font-size': '2.5rem'}),
                            html.P("Most Common Lead Status", 
                                  className="text-center mb-0",
                                  style={'color': theme_colors['text']})
                        ])
                    ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["accent1"]}'})
                ], width=12, md=3, className="mb-4"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H3(f"{leads_by_source.iloc[0]['Lead Source']}", 
                                   className="text-center", 
                                   style={'color': theme_colors['accent1'], 'font-size': '2.5rem'}),
                            html.P("Top Lead Source", 
                                  className="text-center mb-0",
                                  style={'color': theme_colors['text']})
                        ])
                    ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["accent1"]}'})
                ], width=12, md=3, className="mb-4"),
            ]),
            
            # Filters Card
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label('Filter by Lead Status:', 
                                     className="mb-2",
                                     style={'color': theme_colors['text']}),
                            dcc.Dropdown(
                                options=[{'label': status, 'value': status} for status in df_leads['Lead Status'].unique()],
                                value=[],
                                multi=True,
                                id='status-filter',
                                style={'background': theme_colors['card_bg']}
                            )
                        ], md=4),
                        dbc.Col([
                            html.Label('Filter by Lead Source:', 
                                     className="mb-2",
                                     style={'color': theme_colors['text']}),
                            dcc.Dropdown(
                                options=[{'label': source, 'value': source} for source in df_leads['Lead Source'].unique()],
                                value=[],
                                multi=True,
                                id='source-filter',
                                style={'background': theme_colors['card_bg']}
                            )
                        ], md=4),
                        dbc.Col([
                            html.Label('Select Date Range:', 
                                     className="mb-2",
                                     style={'color': theme_colors['text']}),
                            dcc.DatePickerRange(
                                id='date-picker-range',
                                start_date=df_leads['Creation Date'].min(),
                                end_date=df_leads['Creation Date'].max(),
                                display_format='Y-MM-DD'
                            )
                        ], md=4),
                    ])
                ])
            ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["grid"]}', 'margin-bottom': '2rem'}),
            
            # Charts
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='sunburst-chart', figure=fig_sunburst)
                        ])
                    ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["grid"]}'})
                ], width=12, lg=6, className="mb-4"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='heatmap-chart', figure=fig_heatmap)
                        ])
                    ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["grid"]}'})
                ], width=12, lg=6, className="mb-4"),
            ]),
        ]),
        
        dbc.Tab(label='Detailed Analysis', children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='bubble-chart', figure=fig_bubble)
                        ])
                    ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["grid"]}'})
                ], width=12, lg=6, className="mb-4"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='treemap-chart', figure=fig_treemap)
                        ])
                    ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["grid"]}'})
                ], width=12, lg=6, className="mb-4"),
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='funnel-chart', figure=fig_funnel)
                        ])
                    ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["grid"]}'})
                ], width=12, lg=6, className="mb-4"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='calendar-heatmap', figure=fig_calendar_heatmap)
                        ])
                    ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["grid"]}'})
                ], width=12, lg=6, className="mb-4"),
            ]),
        ]),
        
        dbc.Tab(label='Data Table', children=[
            dbc.Card([
                dbc.CardBody([
                    html.H3("Leads Data Table", 
                           className="mb-4", 
                           style={'color': theme_colors['accent1']}),
                    dbc.Input(
                        id="search-input",
                        type="text", 
                        placeholder="Search leads...",
                        className="mb-3",
                        style={'background': theme_colors['card_bg'], 'color': theme_colors['text']}
                    ),
                    dash_table.DataTable(
                        id='data-table',
                        columns=[{"name": i, "id": i} for i in df_leads.columns],
                        data=df_leads.to_dict('records'),
                        style_table={'overflowX': 'auto'},
                        style_header={
                            'backgroundColor': theme_colors['primary'],
                            'color': theme_colors['text'],
                            'fontWeight': 'bold',
                            'textAlign': 'center',
                            'padding': '12px'
                        },
                        style_cell={
                            'backgroundColor': theme_colors['card_bg'],
                            'color': theme_colors['text'],
                            'textAlign': 'left',
                            'padding': '12px',
                            'fontSize': '14px'
                        },
                        style_data_conditional=[{
                            'if': {'row_index': 'odd'},
                            'backgroundColor': theme_colors['background']
                        }],
                        page_size=10,
                        filter_action="native",
                        sort_action="native",
                        sort_mode="multi",
                        page_action="native"
                    )
                ])
            ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["grid"]}'})
        ])
    ], className="mb-4")
], fluid=True, style={'backgroundColor': theme_colors['background'], 'minHeight': '100vh', 'padding': '20px'})

# Callback to update charts based on filters
@callback(
    Output('sunburst-chart', 'figure'),
    Output('heatmap-chart', 'figure'),
    Output('bubble-chart', 'figure'),
    Output('treemap-chart', 'figure'),
    Output('funnel-chart', 'figure'),
    Output('calendar-heatmap', 'figure'),
    Output('data-table', 'data'),
    Input('status-filter', 'value'),
    Input('source-filter', 'value'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
    Input('search-input', 'value')
)
def update_charts(selected_statuses, selected_sources, start_date, end_date, search_value):
    # Filter data based on selections
    filtered_df = df_leads.copy()
    if selected_statuses:
        filtered_df = filtered_df[filtered_df['Lead Status'].isin(selected_statuses)]
    if selected_sources:
        filtered_df = filtered_df[filtered_df['Lead Source'].isin(selected_sources)]
    if start_date and end_date:
        filtered_df = filtered_df[(filtered_df['Creation Date'] >= start_date) & (filtered_df['Creation Date'] <= end_date)]
    if search_value:
        filtered_df = filtered_df[filtered_df['Lead Name'].str.contains(search_value, case=False, na=False)]
    
    # Update charts with filtered data
    # Sunburst Chart
    sunburst_data = filtered_df.groupby(['Lead Source', 'Lead Status']).size().reset_index(name='count')
    fig_sunburst = px.sunburst(
        sunburst_data,
        path=['Lead Source', 'Lead Status'],
        values='count',
        title='Lead Source and Status Breakdown'
    )
    fig_sunburst.update_layout(template=chart_template)
    
    # Heatmap Chart
    heatmap_data = filtered_df.pivot_table(
        index='Property Type',
        columns='Lead Status',
        values='Budget From',
        aggfunc='mean'
    )
    fig_heatmap = px.imshow(
        heatmap_data,
        labels=dict(x="Lead Status", y="Property Type", color="Average Budget"),
        title="Average Budget Heatmap"
    )
    fig_heatmap.update_layout(template=chart_template)
    
    # Bubble Chart
    bubble_data = filtered_df.copy()
    bubble_data['Budget Average'] = (bubble_data['Budget From'] + bubble_data['Budget To']) / 2
    fig_bubble = px.scatter(
        bubble_data,
        x='Budget Average',
        y='Property Type',
        size='Budget Average',
        color='Lead Status',
        hover_name='Lead Name',
        title='Budget vs. Property Type Bubble Chart'
    )
    fig_bubble.update_layout(template=chart_template)
    
    # Treemap Chart
    treemap_data = filtered_df.groupby(['District Name', 'Property Type']).size().reset_index(name='count')
    fig_treemap = px.treemap(
        treemap_data,
        path=['District Name', 'Property Type'],
        values='count',
        title='Leads Distribution Treemap'
    )
    fig_treemap.update_layout(template=chart_template)
    
    # Funnel Chart
    funnel_stages = filtered_df['Lead Status'].value_counts().reset_index()
    funnel_stages.columns = ['Stage', 'Number of Leads']
    fig_funnel = go.Figure(go.Funnel(
        y=funnel_stages['Stage'],
        x=funnel_stages['Number of Leads'],
        textinfo="value+percent initial"
    ))
    fig_funnel.update_layout(template=chart_template, title='Lead Conversion Funnel')
    
    # Calendar Heatmap
    heatmap_counts = filtered_df.copy()
    heatmap_counts['Date'] = heatmap_counts['Creation Date'].dt.date
    heatmap_counts = heatmap_counts.groupby('Date').size().reset_index(name='Leads')
    fig_calendar_heatmap = px.density_heatmap(
        heatmap_counts,
        x='Date',
        y='Leads',
        nbinsx=30,
        title='Leads per Day Heatmap'
    )
    fig_calendar_heatmap.update_layout(template=chart_template)
    
    return fig_sunburst, fig_heatmap, fig_bubble, fig_treemap, fig_funnel, fig_calendar_heatmap, filtered_df.to_dict('records')
