# pages/geospatial_analysis.py

import pandas as pd
from dash import html, dcc, callback, Output, Input,dash_table
# import dash_table
import plotly.express as px
import osmnx as ox
import geopandas as gpd
import plotly.graph_objects as go
import numpy as np
import dash_bootstrap_components as dbc
from datetime import datetime

# Read the data from 'Leads_Info.xlsx'
df_leads = pd.read_excel('./data/Leads_Info.xlsx')

# Data Preprocessing
df_leads.columns = df_leads.columns.str.strip()
df_leads['District Name'] = df_leads['District Name'].str.strip()
df_leads['Budget From'] = pd.to_numeric(df_leads['Budget From'], errors='coerce')
df_leads['Creation Date'] = pd.to_datetime(df_leads['Creation Date'])
df_leads.fillna({'Budget From': 0}, inplace=True)

# Calculate district stats
district_stats = df_leads.groupby('District Name').agg({
    'Lead ID': 'count',
    'Budget From': ['mean', 'sum'],
    'Property Type': lambda x: x.value_counts().index[0] if len(x) > 0 else 'Unknown',
    'Line of Business': lambda x: x.value_counts().index[0] if len(x) > 0 else 'Unknown',
    'Creation Date': lambda x: (datetime.now() - x.max()).days  # Days since last lead
}).round(2)

district_stats.columns = ['Lead Count', 'Avg Budget', 'Total Budget', 'Most Common Property', 'Primary Business', 'Days Since Last Lead']
district_stats = district_stats.reset_index()

# Get unique district names
districts = df_leads['District Name'].unique()

# Initialize an empty GeoDataFrame
gdf_districts = gpd.GeoDataFrame()

# Expanded district name mapping
district_mapping = {
    'new cairo': ['new cairo', 'new cairo city', 'cairo new', 'tagamoa', 'tagammoa', 'el tagamoa', 'al tagamoa'],
    'maadi': ['maadi', 'el maadi', 'al maadi', 'madi', 'el madi'],
    'nasr city': ['nasr city', 'nasr', 'nasrcity', 'madinet nasr', 'madinat nasr'],
    'heliopolis': ['heliopolis', 'misr el gedida', 'misr al gedida', 'masr el gedida'],
    'zamalek': ['zamalek', 'el zamalek', 'al zamalek'],
    'dokki': ['dokki', 'el dokki', 'al dokki', 'doqi'],
    'mohandessin': ['mohandessin', 'mohandiseen', 'mohandseen', 'el mohandessin'],
    'october': ['6th october', 'october', '6 october', 'sixth october'],
    'sheikh zayed': ['sheikh zayed', 'zayed', 'zayed city', 'el sheikh zayed'],
    'garden city': ['garden city', 'garden', 'el garden city']
}

# Enhanced district name standardization
def standardize_district(district):
    if pd.isna(district):
        return None
    district = district.lower().strip()
    # Remove common prefixes/suffixes
    prefixes = ['el ', 'al ', 'el-', 'al-']
    for prefix in prefixes:
        if district.startswith(prefix):
            district = district[len(prefix):]
    
    # Check mapping
    for standard, variations in district_mapping.items():
        if district in variations or any(var in district for var in variations):
            return standard
            
    return district

df_leads['District Name'] = df_leads['District Name'].apply(standardize_district)

# Modern futuristic theme consistent with other pages
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

# Enhanced geocoding with multiple search strategies
for district in districts:
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Expanded search variations
            place_variations = [
                f"{district.upper()}, Cairo, Egypt",
                f"{district.upper()} District, Cairo, Egypt",
                f"{district.upper()}, Egypt",
                f"District {district.upper()}, Cairo",
                f"{district.title()}, Greater Cairo"
            ]
            
            for place in place_variations:
                try:
                    gdf = ox.geocode_to_gdf(place)
                    if not gdf.empty:
                        gdf['district_name'] = district
                        gdf_districts = pd.concat([gdf_districts, gdf], ignore_index=True)
                        break
                except Exception as e:
                    continue
            
            if not gdf.empty:
                break
                
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Failed to find geometry for {district.upper()} after {max_retries} attempts: {e}")
            continue

# Layout handling with consistent theme
if gdf_districts.empty:
    layout = dbc.Container([
        html.H1("Geospatial Analysis", 
                className="text-center mt-4 mb-4",
                style={'color': theme_colors['text']}),
        dbc.Alert("No district geometries were found.", 
                 color="danger", 
                 className="text-center")
    ], fluid=True, style={'backgroundColor': theme_colors['background']})
else:
    # Merge district stats with geometries
    gdf_districts['district_name'] = gdf_districts['district_name'].str.lower()
    district_stats['District Name'] = district_stats['District Name'].str.lower()
    gdf_merged = gdf_districts.merge(district_stats, 
                                   left_on='district_name',
                                   right_on='District Name',
                                   how='left')
    
    # Fill NaN values
    numeric_columns = ['Lead Count', 'Avg Budget', 'Total Budget', 'Days Since Last Lead']
    gdf_merged[numeric_columns] = gdf_merged[numeric_columns].fillna(0)
    
    # Ensure geometries are in WGS84 coordinate reference system
    gdf_merged = gdf_merged.to_crs(epsg=4326)
    
    # Create choropleth map with consistent theme
    fig_choropleth = px.choropleth_mapbox(
        gdf_merged,
        geojson=gdf_merged.geometry.__geo_interface__,
        locations=gdf_merged.index,
        color='Lead Count',
        mapbox_style="carto-darkmatter",  # Dark theme
        zoom=10,
        center={"lat": 30.0444, "lon": 31.2357},
        opacity=0.7,
        color_continuous_scale="Viridis",
        hover_name='district_name',
        hover_data={
            'Lead Count': True,
            'Avg Budget': ':.2f',
            'Total Budget': ':.2f',
            'Most Common Property': True,
            'Primary Business': True,
            'Days Since Last Lead': True
        },
        title='District Lead Distribution',
    )
    
    # Enhanced map layout
    fig_choropleth.update_layout(
        paper_bgcolor=theme_colors['background'],
        plot_bgcolor=theme_colors['background'],
        font={'color': theme_colors['text']},
        margin={"r":0,"t":50,"l":0,"b":0},
        mapbox=dict(
            style="carto-darkmatter",
            zoom=10,
            pitch=45,
        ),
        title_x=0.5,
        title_font_size=24,
        height=600
    )

    # Property Type Distribution
    property_type_counts = df_leads['Property Type'].value_counts().reset_index()
    property_type_counts.columns = ['Property Type', 'count']
    fig_property_types = px.pie(
        property_type_counts,
        values='count',
        names='Property Type',
        title="Property Type Distribution",
        template="plotly_dark"
    ).update_layout(
        paper_bgcolor=theme_colors['background'],
        plot_bgcolor=theme_colors['card_bg'],
        font={'color': theme_colors['text']}
    )

    # Lead Source Distribution
    lead_source_counts = df_leads['Lead Source'].value_counts().head(10).reset_index()
    lead_source_counts.columns = ['Lead Source', 'count']
    fig_lead_sources = px.bar(
        lead_source_counts,
        x='Lead Source',
        y='count',
        title="Top 10 Lead Sources",
        template="plotly_dark"
    ).update_layout(
        paper_bgcolor=theme_colors['background'],
        plot_bgcolor=theme_colors['card_bg'],
        font={'color': theme_colors['text']},
        xaxis_title="Lead Source",
        yaxis_title="Count"
    )
    
    # Layout with consistent theme
    layout = dbc.Container([
        html.H1("Geospatial Analysis", 
                className="text-center mt-4 mb-4",
                style={'color': theme_colors['text']}),
        
        # Stats Summary Cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Total Districts", className="card-title text-center"),
                        html.H2(f"{len(districts)}", className="text-center")
                    ])
                ], style={'background': theme_colors['card_bg'], 
                         'color': theme_colors['text'],
                         'border': f'1px solid {theme_colors["grid"]}'})
            ], xs=12, sm=6, md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Total Leads", className="card-title text-center"),
                        html.H2(f"{district_stats['Lead Count'].sum():,.0f}", className="text-center")
                    ])
                ], style={'background': theme_colors['card_bg'], 
                         'color': theme_colors['text'],
                         'border': f'1px solid {theme_colors["grid"]}'})
            ], xs=12, sm=6, md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Average Budget", className="card-title text-center"),
                        html.H2(f"${district_stats['Avg Budget'].mean():,.2f}", className="text-center")
                    ])
                ], style={'background': theme_colors['card_bg'], 
                         'color': theme_colors['text'],
                         'border': f'1px solid {theme_colors["grid"]}'})
            ], xs=12, sm=6, md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Most Active District", className="card-title text-center"),
                        html.H2(f"{district_stats.loc[district_stats['Lead Count'].idxmax(), 'District Name'].title()}", 
                               className="text-center")
                    ])
                ], style={'background': theme_colors['card_bg'], 
                         'color': theme_colors['text'],
                         'border': f'1px solid {theme_colors["grid"]}'})
            ], xs=12, sm=6, md=3),
        ], className="mb-4"),
        
        # Map and charts
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id='district-map', figure=fig_choropleth)
                    ])
                ], style={'background': theme_colors['card_bg'], 
                         'border': f'1px solid {theme_colors["grid"]}'})
            ], xs=12, className="mb-4"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_property_types)
                    ])
                ], style={'background': theme_colors['card_bg'], 
                         'border': f'1px solid {theme_colors["grid"]}'})
            ], xs=12, md=6, className="mb-4"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_lead_sources)
                    ])
                ], style={'background': theme_colors['card_bg'], 
                         'border': f'1px solid {theme_colors["grid"]}'})
            ], xs=12, md=6, className="mb-4"),
        ]),
        
        # District Performance Table
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H3("District Performance Breakdown", 
                               className="text-center",
                               style={'color': theme_colors['text']})),
                    dbc.CardBody([
                        dash_table.DataTable(
                            id='district-stats-table',
                            columns=[
                                {"name": "District", "id": "District Name"},
                                {"name": "Lead Count", "id": "Lead Count"},
                                {"name": "Avg Budget ($)", "id": "Avg Budget"},
                                {"name": "Total Budget ($)", "id": "Total Budget"},
                                {"name": "Most Common Property", "id": "Most Common Property"},
                                {"name": "Primary Business", "id": "Primary Business"},
                                {"name": "Days Since Last Lead", "id": "Days Since Last Lead"}
                            ],
                            data=district_stats.to_dict('records'),
                            sort_action='native',
                            style_table={'overflowX': 'auto'},
                            style_cell={
                                'textAlign': 'left',
                                'padding': '10px',
                                'minWidth': '100px',
                                'maxWidth': '180px',
                                'whiteSpace': 'normal',
                                'backgroundColor': theme_colors['card_bg'],
                                'color': theme_colors['text']
                            },
                            style_header={
                                'backgroundColor': theme_colors['primary'],
                                'color': theme_colors['text'],
                                'fontWeight': 'bold',
                                'border': f'1px solid {theme_colors["grid"]}'
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': theme_colors['background']
                                }
                            ],
                            page_size=10
                        )
                    ])
                ], style={'background': theme_colors['card_bg'], 
                         'border': f'1px solid {theme_colors["grid"]}'})
            ], xs=12)
        ])
    ], fluid=True, style={'backgroundColor': theme_colors['background'], 
                         'minHeight': '100vh', 
                         'padding': '20px'})
