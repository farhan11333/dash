import dash
from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
import numpy as np

# Read the data from 'Agent_info.xlsx' - fixing escape sequence
df_agents = pd.read_excel('./data/Agents Info.xlsx')

# Data preprocessing
df_agents.fillna(0, inplace=True)

# Calculate conversion rate
df_agents['Conversion Rate'] = (df_agents['Number of Prime TCRs'] + df_agents['Number of Resale TCRs']) / df_agents['Number of Leads Handled'] * 100

# Calculate total and average metrics
total_leads = df_agents['Number of Leads Handled'].sum()
total_prime_tcrs = df_agents['Number of Prime TCRs'].sum()
total_resale_tcrs = df_agents['Number of Resale TCRs'].sum()
average_leads_per_agent = df_agents['Number of Leads Handled'].mean()
average_tcrs_per_agent = (df_agents['Number of Prime TCRs'] + df_agents['Number of Resale TCRs']).mean()
average_conversion_rate = df_agents['Conversion Rate'].mean()
top_conversion_rate = df_agents['Conversion Rate'].max()

# Sort agents by number of leads handled for the bar chart
df_top_agents = df_agents.sort_values(by='Number of Leads Handled', ascending=False)

# Modern futuristic theme
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

# Enhanced leads handled visualization
fig_leads_handled = go.Figure()
fig_leads_handled.add_trace(go.Bar(
    x=df_top_agents.head(15)['Agent Name'],
    y=df_top_agents.head(15)['Number of Leads Handled'],
    marker=dict(
        color=theme_colors['accent1'],
        line=dict(color=theme_colors['accent2'], width=1.5),
        pattern=dict(shape="/")
    )
))
fig_leads_handled.update_layout(
    template=chart_template,
    title='Top 15 Agents by Leads Handled',
    height=450,
    showlegend=False,
    xaxis_title="Agent",
    yaxis_title="Leads Handled",
    xaxis_tickangle=-45,
    hoverlabel={'bgcolor': theme_colors['card_bg']}
)

# Enhanced TCRs visualization
df_top_tcrs = df_agents.copy()
df_top_tcrs['Total TCRs'] = df_top_tcrs['Number of Prime TCRs'] + df_top_tcrs['Number of Resale TCRs']
df_top_tcrs = df_top_tcrs.nlargest(10, 'Total TCRs')

fig_tcrs_per_agent = go.Figure()
fig_tcrs_per_agent.add_trace(go.Bar(
    name='Prime TCRs',
    x=df_top_tcrs['Agent Name'],
    y=df_top_tcrs['Number of Prime TCRs'],
    marker=dict(
        color=theme_colors['accent1'],
        line=dict(color=theme_colors['accent2'], width=1)
    )
))
fig_tcrs_per_agent.add_trace(go.Bar(
    name='Resale TCRs',
    x=df_top_tcrs['Agent Name'],
    y=df_top_tcrs['Number of Resale TCRs'],
    marker=dict(
        color=theme_colors['accent2'],
        line=dict(color=theme_colors['accent1'], width=1)
    )
))
fig_tcrs_per_agent.update_layout(
    template=chart_template,
    barmode='stack',
    title='Top 10 Agents by TCRs Distribution',
    height=450,
    xaxis_tickangle=-45,
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="right",
        x=0.99,
        bgcolor='rgba(23, 42, 69, 0.8)'
    )
)

# Enhanced conversion rate visualization
df_conversion = df_agents.copy()
df_conversion = df_conversion.sort_values(by='Conversion Rate', ascending=False).head(10)

fig_leads_distribution = go.Figure()
fig_leads_distribution.add_trace(go.Bar(
    x=df_conversion['Agent Name'],
    y=df_conversion['Conversion Rate'],
    marker=dict(
        color=df_conversion['Conversion Rate'],
        colorscale=[[0, theme_colors['accent2']], [1, theme_colors['accent1']]],
        showscale=True,
        line=dict(color=theme_colors['text'], width=1)
    )
))
fig_leads_distribution.update_layout(
    template=chart_template,
    title='Top 10 Agents by Lead Conversion Rate',
    height=450,
    xaxis_tickangle=-45
)

# Enhanced Prime vs Resale ratio visualization using sunburst
df_ratio = df_agents.copy()
df_ratio['Prime_Resale_Ratio'] = df_ratio['Number of Prime TCRs'] / df_ratio['Number of Resale TCRs'].replace(0, 1)
df_ratio = df_ratio.sort_values(by='Prime_Resale_Ratio', ascending=False).head(10)

fig_prime_resale_ratio = go.Figure(go.Sunburst(
    labels=df_ratio['Agent Name'],
    parents=["" for _ in range(len(df_ratio))],
    values=df_ratio['Prime_Resale_Ratio'],
    marker=dict(
        colors=[theme_colors['accent1'], theme_colors['accent2'], theme_colors['primary']],
        line=dict(color=theme_colors['background'], width=2)
    ),
    hovertemplate="Agent: %{label}<br>Prime/Resale Ratio: %{value:.2f}<extra></extra>"
))
fig_prime_resale_ratio.update_layout(
    template=chart_template,
    title='Agent Prime to Resale TCR Distribution',
    height=450
)

# Enhanced correlation visualization with trend line
df_agents['Total_TCRs'] = df_agents['Number of Prime TCRs'] + df_agents['Number of Resale TCRs']
fig_correlation = go.Figure()
fig_correlation.add_trace(go.Scatter(
    x=df_agents['Number of Leads Handled'],
    y=df_agents['Total_TCRs'],
    mode='markers',
    marker=dict(
        size=12,
        color=df_agents['Total_TCRs'],
        colorscale=[[0, theme_colors['accent2']], [1, theme_colors['accent1']]],
        showscale=True,
        line=dict(color=theme_colors['background'], width=1)
    ),
    text=df_agents['Agent Name'],
    hovertemplate="<b>%{text}</b><br>Leads: %{x}<br>TCRs: %{y}<extra></extra>"
))

# Add trendline
z = np.polyfit(df_agents['Number of Leads Handled'], df_agents['Total_TCRs'], 1)
p = np.poly1d(z)
fig_correlation.add_trace(go.Scatter(
    x=df_agents['Number of Leads Handled'],
    y=p(df_agents['Number of Leads Handled']),
    mode='lines',
    line=dict(color=theme_colors['accent1'], dash='dash'),
    name='Trend'
))

fig_correlation.update_layout(
    template=chart_template,
    title='Performance Correlation Analysis',
    height=450,
    xaxis_title="Leads Handled",
    yaxis_title="Total TCRs Generated"
)

# New visualization replacing the sunburst chart
fig_performance_quadrant = go.Figure()

# Calculate averages for reference lines
avg_leads = df_agents['Number of Leads Handled'].mean()
avg_conversion = df_agents['Conversion Rate'].mean()

# Add scatter plot
fig_performance_quadrant.add_trace(go.Scatter(
    x=df_agents['Number of Leads Handled'],
    y=df_agents['Conversion Rate'],
    mode='markers',
    marker=dict(
        size=12,
        color=df_agents['Total_TCRs'],
        colorscale=[[0, theme_colors['accent2']], [1, theme_colors['accent1']]],
        showscale=True,
        colorbar=dict(title="Total TCRs")
    ),
    text=df_agents['Agent Name'],
    hovertemplate="<b>%{text}</b><br>" +
                  "Leads: %{x}<br>" +
                  "Conversion Rate: %{y:.1f}%<br>" +
                  "Quadrant: " + 
                  "<br>%{customdata}<extra></extra>",
    customdata=["High Conv, High Volume" if x > avg_leads and y > avg_conversion else
               "High Conv, Low Volume" if x <= avg_leads and y > avg_conversion else
               "Low Conv, High Volume" if x > avg_leads and y <= avg_conversion else
               "Low Conv, Low Volume" for x, y in zip(df_agents['Number of Leads Handled'], df_agents['Conversion Rate'])]
))

# Add reference lines
fig_performance_quadrant.add_hline(y=avg_conversion, line_dash="dash", line_color=theme_colors['grid'])
fig_performance_quadrant.add_vline(x=avg_leads, line_dash="dash", line_color=theme_colors['grid'])

fig_performance_quadrant.update_layout(
    template=chart_template,
    title='Agent Performance Quadrant Analysis',
    height=450,
    xaxis_title="Number of Leads Handled",
    yaxis_title="Conversion Rate (%)"
)

# Modern Futuristic Dashboard Layout
layout = dbc.Container([
    html.H1("Agent Performance Analytics", 
            className="text-center my-4", 
            style={'color': theme_colors['accent1'], 'font-family': 'Roboto', 'font-weight': '300'}),
    
    # KPI Cards Row with enhanced styling
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3(f"{total_leads:,}", 
                           className="card-title text-center", 
                           style={'color': theme_colors['accent1'], 'font-size': '2.5rem'}),
                    html.P("Total Leads Handled", 
                          className="text-center", 
                          style={'color': theme_colors['text'], 'font-size': '1.1rem'})
                ])
            ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["accent1"]}'})
        ], width=12, md=3, className="mb-4"),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3(f"{total_prime_tcrs + total_resale_tcrs:,}", 
                           className="card-title text-center", 
                           style={'color': theme_colors['accent1'], 'font-size': '2.5rem'}),
                    html.P("Total TCRs", 
                          className="text-center", 
                          style={'color': theme_colors['text'], 'font-size': '1.1rem'})
                ])
            ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["accent1"]}'})
        ], width=12, md=3, className="mb-4"),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3(f"{average_conversion_rate:.1f}%", 
                           className="card-title text-center", 
                           style={'color': theme_colors['accent1'], 'font-size': '2.5rem'}),
                    html.P("Average Conversion Rate", 
                          className="text-center", 
                          style={'color': theme_colors['text'], 'font-size': '1.1rem'})
                ])
            ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["accent1"]}'})
        ], width=12, md=3, className="mb-4"),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3(f"{top_conversion_rate:.1f}%", 
                           className="card-title text-center", 
                           style={'color': theme_colors['accent1'], 'font-size': '2.5rem'}),
                    html.P("Top Conversion Rate", 
                          className="text-center", 
                          style={'color': theme_colors['text'], 'font-size': '1.1rem'})
                ])
            ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["accent1"]}'})
        ], width=12, md=3, className="mb-4"),
    ]),
    
    # Charts with enhanced styling
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=fig_leads_handled)
                ])
            ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["grid"]}'})
        ], width=12, lg=6, className="mb-4"),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=fig_tcrs_per_agent)
                ])
            ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["grid"]}'})
        ], width=12, lg=6, className="mb-4"),
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=fig_leads_distribution)
                ])
            ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["grid"]}'})
        ], width=12, lg=6, className="mb-4"),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=fig_prime_resale_ratio)
                ])
            ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["grid"]}'})
        ], width=12, lg=6, className="mb-4"),
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=fig_correlation)
                ])
            ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["grid"]}'})
        ], width=12, className="mb-4"),
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=fig_performance_quadrant)
                ])
            ], style={'background': theme_colors['card_bg'], 'border': f'1px solid {theme_colors["grid"]}'})
        ], width=12, className="mb-4"),
    ]),
], fluid=True, style={'backgroundColor': theme_colors['background'], 'minHeight': '100vh', 'padding': '20px'})
