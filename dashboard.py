import pandas as pd
import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Load and prepare data
df = pd.read_csv('data/supply_chain_data.csv')

# Calculate additional metrics
df['efficiency_score'] = (100 - df['Defect rates'] * 20 - df['Lead time'] / 30 * 100).clip(0, 100)
df['cost_effectiveness'] = (df['Revenue generated'] / df['Manufacturing costs']).clip(0, 100)

# Custom dark theme
dark_theme = {
    'background': '#1f2630',
    'text': '#ffffff',
    'grid': '#374151',
    'paper': '#283442'
}

# Initialize Dash app
app = dash.Dash(__name__)

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Supply Chain Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background-color: #1f2630;
                color: white;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            .dropdown-dark .Select-control {
                background-color: #2e2e2e;
                border-color: #444;
            }
            .dropdown-dark .Select-menu-outer .Select-option {
                background-color: #2e2e2e;
                color: white;
            }
            .kpi-card {
                background: linear-gradient(145deg, #2e2e2e, #3a3a3a);
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), inset 0 2px 4px rgba(255, 255, 255, 0.05);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                text-align: center;
            }
            .kpi-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 12px rgba(0, 0, 0, 0.2), inset 0 2px 6px rgba(255, 255, 255, 0.1);
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Layout
app.layout = html.Div([
    html.H1('Supply Chain Analytics Dashboard', 
            style={'textAlign': 'center', 'color': dark_theme['text'], 'padding': '20px'}),
    
    # Filters
    html.Div([
        html.Label('Product Type', style={'color': dark_theme['text']}),
        dcc.Dropdown(
            id='product-filter',
            options=[{'label': x, 'value': x} for x in df['Product type'].unique()],
            value=df['Product type'].unique()[0],
            style={'backgroundColor': dark_theme['paper'], 'color': 'black'}
        ),
    ], style={'width': '30%', 'margin': '20px auto'}),
    
    # KPI Cards
    html.Div([
        html.Div([
            html.H4('Total Revenue', style={'color': '#63b3ed'}),
            html.H2(id='total-revenue', style={'color': '#90cdf4'})
        ], className='kpi-card', style={'width': '23%', 'display': 'inline-block', 'margin': '1%', 'padding': '15px'}),
        
        html.Div([
            html.H4('Average Lead Time', style={'color': '#f6ad55'}),
            html.H2(id='avg-lead-time', style={'color': '#fbd38d'})
        ], className='kpi-card', style={'width': '23%', 'display': 'inline-block', 'margin': '1%', 'padding': '15px'}),
        
        html.Div([
            html.H4('Efficiency Score', style={'color': '#68d391'}),
            html.H2(id='efficiency-score', style={'color': '#9ae6b4'})
        ], className='kpi-card', style={'width': '23%', 'display': 'inline-block', 'margin': '1%', 'padding': '15px'}),
        
        html.Div([
            html.H4('Cost Effectiveness', style={'color': '#fc8181'}),
            html.H2(id='cost-effectiveness', style={'color': '#feb2b2'})
        ], className='kpi-card', style={'width': '23%', 'display': 'inline-block', 'margin': '1%', 'padding': '15px'})
    ], style={'textAlign': 'center', 'margin': '20px 0'}),
    
    # Charts Row 1
    html.Div([
        html.Div([
            dcc.Graph(id='gauge-chart')
        ], style={'width': '33%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='spider-chart')
        ], style={'width': '33%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='defect-trend')
        ], style={'width': '33%', 'display': 'inline-block'})
    ]),
    
    # Charts Row 2
    html.Div([
        html.Div([
            dcc.Graph(id='revenue-location')
        ], style={'width': '50%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='supplier-performance')
        ], style={'width': '50%', 'display': 'inline-block'})
    ])
])

# Callbacks
@callback(
    [Output('total-revenue', 'children'),
     Output('avg-lead-time', 'children'),
     Output('efficiency-score', 'children'),
     Output('cost-effectiveness', 'children')],
    [Input('product-filter', 'value')]
)
def update_kpis(selected_product):
    filtered_df = df[df['Product type'] == selected_product]
    
    revenue = f"${filtered_df['Revenue generated'].sum():,.0f}"
    lead_time = f"{filtered_df['Lead time'].mean():.1f} days"
    efficiency = f"{filtered_df['efficiency_score'].mean():.1f}%"
    cost_effect = f"{filtered_df['cost_effectiveness'].mean():.1f}x"
    
    return revenue, lead_time, efficiency, cost_effect

@callback(
    Output('gauge-chart', 'figure'),
    [Input('product-filter', 'value')]
)
def update_gauge(selected_product):
    filtered_df = df[df['Product type'] == selected_product]
    efficiency = filtered_df['efficiency_score'].mean()
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = efficiency,
        title = {'text': "Overall Efficiency"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "#63b3ed"},
            'bgcolor': dark_theme['paper'],
            'borderwidth': 2,
            'bordercolor': dark_theme['text'],
            'steps': [
                {'range': [0, 33], 'color': '#fc8181'},
                {'range': [33, 66], 'color': '#f6ad55'},
                {'range': [66, 100], 'color': '#68d391'}
            ]
        }
    ))
    
    fig.update_layout(
        paper_bgcolor = dark_theme['background'],
        font = {'color': dark_theme['text']},
        height = 300
    )
    return fig

@callback(
    Output('spider-chart', 'figure'),
    [Input('product-filter', 'value')]
)
def update_spider(selected_product):
    filtered_df = df[df['Product type'] == selected_product]
    metrics = ['Availability', 'Lead time', 'Defect rates', 'Manufacturing costs', 'Shipping costs']
    
    # Normalize values between 0 and 1
    values = [
        filtered_df['Availability'].mean() / 100,
        1 - (filtered_df['Lead time'].mean() / filtered_df['Lead time'].max()),
        1 - filtered_df['Defect rates'].mean(),
        1 - (filtered_df['Manufacturing costs'].mean() / filtered_df['Manufacturing costs'].max()),
        1 - (filtered_df['Shipping costs'].mean() / filtered_df['Shipping costs'].max())
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r = values,
        theta = metrics,
        fill = 'toself',
        fillcolor = 'rgba(99, 179, 237, 0.3)',
        line = {'color': '#63b3ed'}
    ))
    
    fig.update_layout(
        polar = {
            'radialaxis': {'showline': False, 'visible': True, 'range': [0, 1]},
            'bgcolor': dark_theme['paper']
        },
        paper_bgcolor = dark_theme['background'],
        font = {'color': dark_theme['text']},
        title = 'Performance Metrics',
        height = 300
    )
    return fig

@callback(
    Output('defect-trend', 'figure'),
    [Input('product-filter', 'value')]
)
def update_defect_trend(selected_product):
    filtered_df = df[df['Product type'] == selected_product]
    
    fig = go.Figure()
    fig.add_trace(go.Box(
        y = filtered_df['Defect rates'],
        x = filtered_df['Supplier name'],
        marker_color = '#63b3ed'
    ))
    
    fig.update_layout(
        paper_bgcolor = dark_theme['background'],
        plot_bgcolor = dark_theme['paper'],
        font = {'color': dark_theme['text']},
        title = 'Defect Rates by Supplier',
        height = 300,
        xaxis = {'gridcolor': dark_theme['grid']},
        yaxis = {'gridcolor': dark_theme['grid']}
    )
    return fig

@callback(
    Output('revenue-location', 'figure'),
    [Input('product-filter', 'value')]
)
def update_revenue_location(selected_product):
    filtered_df = df[df['Product type'] == selected_product]
    location_revenue = filtered_df.groupby('Location')['Revenue generated'].sum().reset_index()
    
    fig = px.bar(
        location_revenue,
        x = 'Location',
        y = 'Revenue generated',
        title = 'Revenue by Location',
        color_discrete_sequence=['#63b3ed']
    )
    
    fig.update_layout(
        paper_bgcolor = dark_theme['background'],
        plot_bgcolor = dark_theme['paper'],
        font = {'color': dark_theme['text']},
        height = 400,
        xaxis = {'gridcolor': dark_theme['grid']},
        yaxis = {'gridcolor': dark_theme['grid']}
    )
    return fig

@callback(
    Output('supplier-performance', 'figure'),
    [Input('product-filter', 'value')]
)
def update_supplier_performance(selected_product):
    filtered_df = df[df['Product type'] == selected_product]
    supplier_metrics = filtered_df.groupby('Supplier name').agg({
        'efficiency_score': 'mean',
        'cost_effectiveness': 'mean'
    }).reset_index()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Bar(
            x=supplier_metrics['Supplier name'],
            y=supplier_metrics['efficiency_score'],
            name="Efficiency",
            marker_color='#63b3ed'
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=supplier_metrics['Supplier name'],
            y=supplier_metrics['cost_effectiveness'],
            name="Cost Effectiveness",
            line=dict(color='#68d391')
        ),
        secondary_y=True
    )
    
    fig.update_layout(
        paper_bgcolor = dark_theme['background'],
        plot_bgcolor = dark_theme['paper'],
        font = {'color': dark_theme['text']},
        title = 'Supplier Performance Metrics',
        height = 400,
        xaxis = {'gridcolor': dark_theme['grid']},
        yaxis = {'gridcolor': dark_theme['grid']},
        yaxis2 = {'gridcolor': dark_theme['grid']}
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)