import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
# Removed executive_summary and client_feedback from imports
from pages import agent_performance, lead_analysis, sales_revenue, market_trends, operational_efficiency

# Initialize app with a modern theme
app = dash.Dash(__name__, 
    external_stylesheets=[dbc.themes.CYBORG], # Dark, futuristic theme
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)
server = app.server

# Modern futuristic color scheme matching agent_performance
COLORS = {
    'primary': '#1A237E',    # Deep indigo
    'secondary': '#00BFA5',  # Teal accent
    'accent': '#64FFDA',     # Bright teal accent
    'background': '#0A192F', # Dark blue background
    'text': '#FFFFFF',       # White text
    'card_bg': '#172A45',    # Slightly lighter blue for cards
    'grid': '#233554'        # Grid lines color
}

# Navigation with modern styling
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Agent Performance", href="/agent-performance",
                               className="nav-link-custom",
                               id="nav-agent-performance",
                               style={
                                   'color': COLORS['text'],
                                   'margin': '0 8px',
                                   'padding': '10px 20px',
                                   'border-radius': '8px',
                                   'transition': 'all 0.3s ease',
                                   'background-color': COLORS['primary'],
                                   'box-shadow': '0 0 15px rgba(100,255,218,0.1)',
                                   'font-weight': '500',
                                   'border': f'1px solid {COLORS["accent"]}'
                               })),
        dbc.NavItem(dbc.NavLink("Lead Analysis", href="/lead-analysis",
                               className="nav-link-custom", 
                               id="nav-lead-analysis",
                               style={
                                   'color': COLORS['text'],
                                   'margin': '0 8px',
                                   'padding': '10px 20px',
                                   'border-radius': '8px',
                                   'transition': 'all 0.3s ease',
                                   'background-color': COLORS['primary'],
                                   'box-shadow': '0 0 15px rgba(100,255,218,0.1)',
                                   'font-weight': '500',
                                   'border': f'1px solid {COLORS["accent"]}'
                               })),
        dbc.NavItem(dbc.NavLink("Geospatial Analysis", href="/sales-revenue",
                               className="nav-link-custom",
                               id="nav-sales-revenue",
                               style={
                                   'color': COLORS['text'],
                                   'margin': '0 8px',
                                   'padding': '10px 20px',
                                   'border-radius': '8px',
                                   'transition': 'all 0.3s ease',
                                   'background-color': COLORS['primary'],
                                   'box-shadow': '0 0 15px rgba(100,255,218,0.1)',
                                   'font-weight': '500',
                                   'border': f'1px solid {COLORS["accent"]}'
                               })),
        dbc.NavItem(dbc.NavLink("Transactions", href="/market-trends",
                               className="nav-link-custom",
                               id="nav-market-trends", 
                               style={
                                   'color': COLORS['text'],
                                   'margin': '0 8px',
                                   'padding': '10px 20px',
                                   'border-radius': '8px',
                                   'transition': 'all 0.3s ease',
                                   'background-color': COLORS['primary'],
                                   'box-shadow': '0 0 15px rgba(100,255,218,0.1)',
                                   'font-weight': '500',
                                   'border': f'1px solid {COLORS["accent"]}'
                               })),
        dbc.NavItem(dbc.NavLink("Contact Analysis", href="/operational-efficiency",
                               className="nav-link-custom",
                               id="nav-operational-efficiency",
                               style={
                                   'color': COLORS['text'],
                                   'margin': '0 8px',
                                   'padding': '10px 20px',
                                   'border-radius': '8px',
                                   'transition': 'all 0.3s ease',
                                   'background-color': COLORS['primary'],
                                   'box-shadow': '0 0 15px rgba(100,255,218,0.1)',
                                   'font-weight': '500',
                                   'border': f'1px solid {COLORS["accent"]}'
                               })),
    ],
    brand=html.Img(src="assets/CB.png", 
                   style={'height': '50px', 'margin-left': '20px'}),
    brand_href="/",
    color="#FFFFFF",
    dark=True,
    style={
        'padding': '15px 0',
        'box-shadow': '0 0 30px rgba(100,255,218,0.1)',
        'margin-bottom': '30px',
        'border-bottom': f'1px solid {COLORS["accent"]}'
    }
)

# Modern home page design
home_page = html.Div([
    html.Div([
        html.Div([
            html.Img(src="assets/CB.png",
                    style={
                        'height': 'min(200px, 30vw)',
                        'margin': '40px auto',
                        'display': 'block',
                        'filter': 'drop-shadow(0 0 20px rgba(100,255,218,0.3))'
                    }),
            html.H1("Welcome to Coldwell Banker Analytics",
                    style={
                        'text-align': 'center',
                        'color': COLORS['accent'],
                        'margin-bottom': '30px',
                        'font-size': 'min(3rem, 8vw)',
                        'font-weight': '700',
                        'letter-spacing': '1px',
                        'text-shadow': '0 0 10px rgba(100,255,218,0.3)'
                    }),
            html.H4("Discover insights and make data-driven decisions",
                    style={
                        'text-align': 'center',
                        'color': COLORS['secondary'],
                        'margin-bottom': '50px',
                        'font-size': 'min(1.8rem, 5vw)',
                        'font-weight': '400',
                        'opacity': '0.9'
                    })
        ], className="welcome-content",
        style={
            'background': COLORS['card_bg'],
            'padding': '40px',
            'border-radius': '15px',
            'box-shadow': '0 0 40px rgba(100,255,218,0.1)',
            'max-width': '1200px',
            'margin': '0 auto',
            'border': f'1px solid {COLORS["accent"]}'
        })
    ], style={
        'padding': '40px 20px',
        'background': COLORS['background'],
        'min-height': '90vh'
    })
])

# Layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content', style={'background': COLORS['background']})
])

# Callback to render pages
@app.callback(
    [
     Output('page-content', 'children'),
     Output('nav-agent-performance', 'style'),
     Output('nav-lead-analysis', 'style'),
     Output('nav-sales-revenue', 'style'),
     Output('nav-market-trends', 'style'),
     Output('nav-operational-efficiency', 'style')],
    Input('url', 'pathname'))
def display_page(pathname):
    # Base style for nav links
    base_style = {
        'color': COLORS['text'],
        'margin': '0 8px',
        'padding': '10px 20px',
        'border-radius': '8px',
        'transition': 'all 0.3s ease',
        'background-color': COLORS['primary'],
        'box-shadow': '0 0 15px rgba(100,255,218,0.1)',
        'font-weight': '500',
        'border': f'1px solid {COLORS["accent"]}'
    }
    
    # Active style
    active_style = base_style.copy()
    active_style.update({
        'background-color': COLORS['secondary'],
        'box-shadow': '0 0 20px rgba(0,191,165,0.3)',
        'color': COLORS['primary']
    })
    
    styles = [base_style.copy() for _ in range(5)]
    
    if pathname == '/agent-performance':
        content = agent_performance.layout
        styles[0] = active_style
    elif pathname == '/lead-analysis':
        content = lead_analysis.layout
        styles[1] = active_style
    elif pathname == '/sales-revenue':
        content = sales_revenue.layout
        styles[2] = active_style
    elif pathname == '/market-trends':
        content = market_trends.layout
        styles[3] = active_style
    elif pathname == '/operational-efficiency':
        content = operational_efficiency.layout
        styles[4] = active_style
    elif pathname == '/':
        content = home_page
    else:
        content = html.H1('404 - Page Not Found',
                         style={'text-align': 'center', 
                                'color': COLORS['accent'],
                                'margin-top': '50px',
                                'text-shadow': '0 0 10px rgba(100,255,218,0.3)'})
    
    return [content] + styles

if __name__ == '__main__':
    app.run_server(debug=True)
