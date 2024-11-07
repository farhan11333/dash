# pages/contact_analysis.py

import pandas as pd
from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc
import re
import networkx as nx
import numpy as np

# Load data
df = pd.read_csv('data/Contact_With_Comments.csv')

# Modern futuristic theme matching agent_performance
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

# Data preprocessing
def extract_actions(comments):
    if pd.isna(comments):
        return []
        
    # Split comments by '||' and remove any leading/trailing whitespace
    actions = [action.strip() for action in comments.split('||') if action.strip()]
    action_types = []
    
    for action in actions:
        # Remove any HTML tags
        action = re.sub('<[^<]+?>', '', action)
        
        # Skip empty or purely descriptive comments
        if not action or action.startswith(('NA', 'F', 'in contact', 'working', 'available', 'closed', 'Template Done')):
            continue
            
        # Extract the action type
        action_lower = action.lower()
        
        if 'was created by' in action_lower:
            if 'lead ticket' in action_lower:
                action_type = 'Lead Ticket Was Created'
            elif 'call' in action_lower:
                action_type = 'Call Was Created'
            elif 'request' in action_lower:
                action_type = 'Request Was Created'
            elif 'prospect' in action_lower:
                action_type = 'Prospect Was Created'
            else:
                continue
                
        elif 'was assigned to branch' in action_lower:
            if 'lead ticket' in action_lower:
                action_type = 'Lead Ticket Was Assigned to Branch'
            elif 'call' in action_lower:
                action_type = 'Call Was Assigned to Branch'
            else:
                continue
                
        elif 'was assigned to agent' in action_lower:
            if 'lead ticket' in action_lower:
                action_type = 'Lead Ticket Was Assigned to Agent'
            elif 'call' in action_lower:
                action_type = 'Call Was Assigned to Agent'
            else:
                continue
                
        elif 'was converted to' in action_lower:
            if 'request' in action_lower:
                action_type = 'Lead Ticket Was Converted to Request'
            elif 'prospect' in action_lower:
                action_type = 'Lead Ticket Was Converted to Prospect'
            else:
                continue
                
        elif 'was rejected' in action_lower:
            action_type = 'Lead Ticket Was Rejected'
            
        elif 'was set unqualified' in action_lower:
            action_type = 'Lead Ticket Was Set Unqualified'
            
        elif 'was voided' in action_lower:
            action_type = 'Lead Ticket Was Voided'
            
        elif 'status was changed to' in action_lower:
            new_status = action_lower.split('status was changed to')[1].split('by')[0].strip()
            action_type = f'Status Changed to {new_status.title()}'
            
        else:
            continue
            
        action_types.append(action_type)
        
    return action_types

df['Action Types'] = df['Comments'].apply(extract_actions)

def map_action_to_stage(action_type):
    if 'Lead Ticket Was Created' in action_type:
        return 'Lead Created'
    elif 'Lead Ticket Was Assigned to Branch' in action_type:
        return 'Assigned to Branch'
    elif 'Lead Ticket Was Assigned to Agent' in action_type:
        return 'Assigned to Agent'
    elif 'Lead Ticket Was Converted to Request' in action_type:
        return 'Converted to Request'
    elif 'Request Was Created' in action_type:
        return 'Request Created'
    elif 'Lead Ticket Was Converted to Prospect' in action_type:
        return 'Converted to Prospect'
    elif 'Prospect Was Created' in action_type:
        return 'Prospect Created'
    elif any(x in action_type for x in ['Was Set Unqualified', 'Status Changed to Unqualified']):
        return 'Closed - Unqualified'
    elif 'Was Voided' in action_type:
        return 'Closed - Voided'
    elif 'Was Rejected' in action_type:
        return 'Closed - Rejected'
    elif 'Call Was Created' in action_type:
        return 'Call Created'
    elif 'Call Was Assigned to Branch' in action_type:
        return 'Call Assigned to Branch'
    elif 'Call Was Assigned to Agent' in action_type:
        return 'Call Assigned to Agent'
    else:
        return 'Other'

df['Stages'] = df['Action Types'].apply(lambda actions: [map_action_to_stage(a) for a in actions])

# Prepare transitions data for Sankey Diagram and Network Graph
transitions = []

for stages in df['Stages']:
    # Remove consecutive duplicate stages
    stages = [stage for i, stage in enumerate(stages) if i == 0 or stage != stages[i-1]]
    for i in range(len(stages) - 1):
        source = stages[i]
        target = stages[i + 1]
        transitions.append((source, target))

transition_counts = pd.DataFrame(transitions, columns=['source', 'target']).value_counts().reset_index(name='count')

# Generate labels and indices
all_stages = list(set([stage for stages in df['Stages'] for stage in stages]))
label_indices = {label: idx for idx, label in enumerate(all_stages)}

# Assign colors to nodes using theme colors
stage_colors = {stage: theme_colors['accent1'] for stage in all_stages}
node_colors = [stage_colors[stage] for stage in all_stages]

# Get the final stage for each contact
df['Final Stage'] = df['Stages'].apply(lambda x: x[-1] if x else 'Unknown')

# Count the number of contacts at each final stage
stage_counts = df['Final Stage'].value_counts().reset_index()
stage_counts.columns = ['Stage', 'Count']

# Flatten the list of action types
all_actions = [action for actions in df['Action Types'] for action in actions]

# Count the occurrences of each action
action_counts = pd.Series(all_actions).value_counts().reset_index()
action_counts.columns = ['Action', 'Count']

# Create a NetworkX graph for the flow diagram
G = nx.DiGraph()
for _, row in transition_counts.iterrows():
    G.add_edge(row['source'], row['target'], weight=row['count'])

# Calculate node levels based on shortest path from start
start_nodes = [node for node in G.nodes() if G.in_degree(node) == 0]
if not start_nodes:
    start_nodes = [list(G.nodes())[0]]  # Fallback if no clear start

# Assign levels to nodes
node_levels = {}
for start_node in start_nodes:
    for node in G.nodes():
        if node not in node_levels:
            try:
                level = len(nx.shortest_path(G, start_node, node)) - 1
                node_levels[node] = level
            except nx.NetworkXNoPath:
                continue

# Assign remaining nodes that weren't reached
max_level = max(node_levels.values()) if node_levels else 0
for node in G.nodes():
    if node not in node_levels:
        node_levels[node] = max_level + 1

# Explicitly add subset attribute to nodes
for node, level in node_levels.items():
    G.nodes[node]['subset'] = level

# Calculate node statistics
node_stats = {node: {
    'incoming': sum(d['weight'] for _, _, d in G.in_edges(node, data=True)),
    'outgoing': sum(d['weight'] for _, _, d in G.out_edges(node, data=True))
} for node in G.nodes()}

# Use multipartite_layout with explicit subset attribute
pos = nx.multipartite_layout(G, subset_key='subset', scale=2.0)

# Create edge traces
edge_x = []
edge_y = []
edge_texts = []
for edge in G.edges(data=True):
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])
    edge_texts.append(f"From {edge[0]} to {edge[1]}<br>Count: {edge[2]['weight']}")

# Create node traces
node_x = []
node_y = []
node_texts = []
node_labels = []
node_sizes = []
for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_labels.append(node)
    hover_text = (
        f"Stage: {node}<br>"
        f"Incoming contacts: {node_stats[node]['incoming']}<br>"
        f"Outgoing contacts: {node_stats[node]['outgoing']}<br>"
        f"Total flow: {node_stats[node]['incoming'] + node_stats[node]['outgoing']}"
    )
    node_texts.append(hover_text)
    node_sizes.append(np.sqrt(node_stats[node]['incoming'] + node_stats[node]['outgoing']) * 10)

# Layout with modern styling
layout = dbc.Container([
    html.H1("Contact Analysis Dashboard", 
            className="text-center my-4",
            style={'color': theme_colors['accent1']}),
            
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H2("Contact Stage Transitions (Sankey)", 
                                     className="text-center",
                                     style={'color': theme_colors['accent1']})),
                dbc.CardBody([
                    dcc.Graph(id='operational-sankey-diagram')
                ])
            ], style={'background': theme_colors['card_bg'], 
                     'border': f'1px solid {theme_colors["grid"]}'}, 
               className="mb-4")
        ], width=12),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H2("Contact Stage Network Flow", 
                                     className="text-center",
                                     style={'color': theme_colors['accent1']})),
                dbc.CardBody([
                    dcc.Graph(id='operational-network-diagram')
                ])
            ], style={'background': theme_colors['card_bg'], 
                     'border': f'1px solid {theme_colors["grid"]}'}, 
               className="mb-4")
        ], width=12),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H2("Contact Final Stages Funnel", 
                                     className="text-center",
                                     style={'color': theme_colors['accent1']})),
                dbc.CardBody([
                    dcc.Graph(id='operational-funnel-chart')
                ])
            ], style={'background': theme_colors['card_bg'], 
                     'border': f'1px solid {theme_colors["grid"]}'}, 
               className="mb-4")
        ], width=12, lg=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H2("Top Actions Taken", 
                                     className="text-center",
                                     style={'color': theme_colors['accent1']})),
                dbc.CardBody([
                    dcc.Graph(id='operational-action-counts-bar')
                ])
            ], style={'background': theme_colors['card_bg'], 
                     'border': f'1px solid {theme_colors["grid"]}'}, 
               className="mb-4")
        ], width=12, lg=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H2("Distribution of Number of Contacts", 
                                     className="text-center",
                                     style={'color': theme_colors['accent1']})),
                dbc.CardBody([
                    dcc.Graph(id='operational-contacts-histogram')
                ])
            ], style={'background': theme_colors['card_bg'], 
                     'border': f'1px solid {theme_colors["grid"]}'}, 
               className="mb-4")
        ], width=12)
    ])
], fluid=True)

# Callback
@callback(
    Output('operational-sankey-diagram', 'figure'),
    Output('operational-network-diagram', 'figure'),
    Output('operational-funnel-chart', 'figure'),
    Output('operational-action-counts-bar', 'figure'),
    Output('operational-contacts-histogram', 'figure'),
    Input('operational-sankey-diagram', 'id')  # Dummy input to trigger callback
)
def update_figures(_):
    # Sankey Diagram
    sankey_fig = go.Figure(data=[go.Sankey(
        arrangement = "snap",
        node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color="black", width=0.5),
            label = all_stages,
            color = node_colors,
            hovertemplate='Stage: %{label}<extra></extra>'
        ),
        link = dict(
            source = transition_counts['source'].map(label_indices),
            target = transition_counts['target'].map(label_indices),
            value = transition_counts['count'],
            color = theme_colors['accent2'],
            hovertemplate='From %{source.label} to %{target.label}<br>Count: %{value}<extra></extra>'
        )
    )])
    sankey_fig.update_layout(height=600)
    for key, value in chart_template.items():
        sankey_fig.update_layout(**{key: value})
    
    # Network Flow Diagram
    network_fig = go.Figure()
    
    # Add edges with curved paths
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color=theme_colors['accent2']),
        hoverinfo='text',
        text=edge_texts,
        mode='lines',
        hoveron='points+fills',
        hovertemplate='%{text}<extra></extra>'
    )
    
    # Add nodes with enhanced hover
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_texts,
        textposition="top center",
        hoverinfo='text',
        hovertext=node_texts,
        marker=dict(
            size=node_sizes,
            color=theme_colors['accent1'],
            line=dict(width=2, color=theme_colors['text']),
            sizemode='area',
        ),
        hovertemplate='%{hovertext}<extra></extra>'
    )
    
    network_fig.add_trace(edge_trace)
    network_fig.add_trace(node_trace)
    
    network_fig.update_layout(
        showlegend=False,
        hovermode='closest',
        height=600,
        margin=dict(b=20,l=5,r=5,t=40),
        # Add better interaction modes
        dragmode='pan',
        clickmode='event+select'
    )
    for key, value in chart_template.items():
        network_fig.update_layout(**{key: value})
    
    # Funnel Chart
    funnel_fig = go.Figure(go.Funnel(
        y=stage_counts['Stage'],
        x=stage_counts['Count'],
        textinfo="value+percent initial",
        marker={'color': theme_colors['accent1']}
    ))
    funnel_fig.update_layout(height=500)
    for key, value in chart_template.items():
        funnel_fig.update_layout(**{key: value})
    
    # Action Counts Bar Chart
    action_counts_fig = px.bar(
        action_counts.head(20),
        x='Count',
        y='Action',
        orientation='h',
        color_discrete_sequence=[theme_colors['accent1']],
        labels={'Count': 'Number of Occurrences', 'Action': 'Action Type'}
    )
    action_counts_fig.update_layout(height=500)
    for key, value in chart_template.items():
        action_counts_fig.update_layout(**{key: value})
    action_counts_fig.update_layout(yaxis={'categoryorder':'total ascending'})
    
    # Histogram of Number of Contacts
    contacts_histogram_fig = px.histogram(
        df,
        x='Number Of Contact',
        nbins=10,
        color_discrete_sequence=[theme_colors['accent1']],
        labels={'Number Of Contact': 'Number Of Contacts'}
    )
    contacts_histogram_fig.update_layout(height=400)
    for key, value in chart_template.items():
        contacts_histogram_fig.update_layout(**{key: value})
    
    return sankey_fig, network_fig, funnel_fig, action_counts_fig, contacts_histogram_fig
# End of Selection
