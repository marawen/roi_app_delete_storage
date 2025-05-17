import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from views.helpers import load_processed_data
import json

def render():
    # Custom title with consistent styling
    st.markdown('<div class="page-title">📊 ROI Summary</div>', unsafe_allow_html=True)
    
    # Initialize settings if not exists
    initialize_settings()

    # Add CSS for consistent styling
    st.markdown("""
    <style>
    .welcome-banner {
        background: linear-gradient(to right, #E3F2FD, #BBDEFB);
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #1976D2;
    }
    
    .welcome-banner h2 {
        color: #1976D2;
        margin-top: 0;
    }
    
    .summary-card {
        background: white;
        padding: 1.2rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    
    .section-subheader {
        font-size: 1.2rem;
        font-weight: 600;
        color: #333;
        margin: 1rem 0;
    }
    
    .metrics-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 1.5rem;
        background: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .metric-item {
        text-align: center;
        flex: 1;
        padding: 0.5rem;
    }

    .metric-label {
        font-size: 0.85rem;
        color: #546E7A;
        margin-bottom: 0.3rem;
    }

    .metric-value {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1976D2;
    }
    
    .summary-container {
        background: linear-gradient(to right, #f8f9fa, #f1f8fe);
        border: 1px solid #e0e0e0;
        border-left: 4px solid #1976D2;
        border-radius: 8px;
        padding: 1.5rem;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
    }
    
    .implementation-notes {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
    }
    
    .implementation-notes .note-item {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .implementation-notes .note-item:last-child {
        border-bottom: none;
    }
    
    /* Override Streamlit's metric styling for consistency */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #1976D2 !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Introduction banner
    st.markdown("""
    <div class="welcome-banner">
        <h2>ROI Summary Dashboard</h2>
        <p>Comprehensive analysis of financial and environmental impacts from your Turbonomic delete storage recommendations.</p>
    </div>
    """, unsafe_allow_html=True)

    # Check if data exists either in session state or in outputs directory
    if 'processed_df' not in st.session_state:
        df = load_processed_data()
        if df is not None:
            st.session_state['processed_df'] = df
            st.success("✅ Loaded previously processed data from outputs directory.")
        else:
            st.warning("""
            ⚠️ No data available for ROI Summary.
            
            To view the ROI Summary:
            1. Go to the **Upload & Process** tab
            2. Upload your Turbonomic Excel file
            3. Process the data
            4. Return to this tab
            """)
            # Navigation button to upload page
            st.button("Go to Upload & Process", 
                     type="primary", 
                     key="go_to_upload", 
                     on_click=navigate_to, 
                     args=('upload_process',))
            return

    df = st.session_state['processed_df']
    settings = st.session_state.settings

    # Define color scheme
    SAVINGS_COLOR = '#2ecc71'  # Green
    COST_COLOR = '#e74c3c'     # Red
    ENERGY_COLOR = '#3498db'   # Blue
    COOLING_COLOR = '#9b59b6'  # Purple
    CARBON_COLOR = '#1abc9c'   # Teal

    # Calculate all metrics using cached function
    metrics = calculate_metrics(df, settings)

    # First Year Implementation ROI section header
    st.markdown('<div class="section-subheader">🎯 First Year ROI Projection</div>', unsafe_allow_html=True)
    st.markdown(f"*Based on {settings['implementation_months']}-month implementation timeline*")

    # Financial Impact - using custom metrics row
    st.markdown('<div class="section-subheader">💰 Cost Reduction & Savings</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metrics-row">
        <div class="metric-item">
            <div class="metric-label">Storage Cost Reduction</div>
            <div class="metric-value" style="color: #27ae60;">${metrics['first_year_storage_savings']:,.0f}</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">Labor Cost Avoidance</div>
            <div class="metric-value" style="color: #3498db;">${metrics['first_year_labor_savings']:,.0f}</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">Automation Investment</div>
            <div class="metric-value" style="color: #e74c3c;">${metrics['first_year_automation_cost']:,.0f}</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">Total Net Savings</div>
            <div class="metric-value" style="color: #27ae60;">${metrics['first_year_net_savings']:,.0f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Environmental Impact - using custom metrics row
    st.markdown('<div class="section-subheader">🌱 Sustainability Benefits</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metrics-row">
        <div class="metric-item">
            <div class="metric-label">Direct Energy Savings</div>
            <div class="metric-value" style="color: #3498db;">{metrics['first_year_energy_savings']:,.0f} kWh</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">Cooling Energy Reduction</div>
            <div class="metric-value" style="color: #8e44ad;">{metrics['first_year_cooling_savings']:,.0f} kWh</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">Carbon Footprint Reduction</div>
            <div class="metric-value" style="color: #16a085;">{metrics['first_year_carbon_savings']:,.0f} kg CO₂</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Charts with improved styling
    st.markdown('<div class="section-subheader">📈 Financial & Environmental Impact Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Financial Impact Breakdown with distinct colors
        fig_financial = go.Figure(data=[
            go.Bar(name='Storage Cost Reduction', y=[metrics['first_year_storage_savings']], marker_color='#27ae60'),  # Darker green
            go.Bar(name='Labor Cost Avoidance', y=[metrics['first_year_labor_savings']], marker_color='#3498db'),  # Blue
            go.Bar(name='Automation Investment', y=[-metrics['first_year_automation_cost']], marker_color='#e74c3c')  # Red
        ])
        fig_financial.update_layout(
            title='Financial ROI Components',
            barmode='relative',
            showlegend=True,
            height=400,
            xaxis_title="ROI Component",
            yaxis_title="Amount (USD)",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
            font=dict(color='#546E7A')
        )
        # Add hover template with currency formatting
        fig_financial.update_traces(
            hovertemplate='<b>%{y:$,.2f}</b><extra></extra>'
        )
        st.plotly_chart(fig_financial, use_container_width=True)
    
    with col2:
        # Environmental Impact Breakdown with more distinct colors
        fig_environmental = go.Figure(data=[
            go.Bar(name='Direct Energy Savings', y=[metrics['first_year_energy_savings']], marker_color='#3498db'),  # Blue
            go.Bar(name='Cooling Energy Reduction', y=[metrics['first_year_cooling_savings']], marker_color='#8e44ad'),  # Purple
            go.Bar(name='Carbon Footprint Reduction', y=[metrics['first_year_carbon_savings']], marker_color='#16a085')  # Teal
        ])
        fig_environmental.update_layout(
            title='Environmental Sustainability Metrics',
            barmode='group',
            showlegend=True,
            height=400,
            xaxis_title="Environment Component",
            yaxis_title="Amount (kWh / kg CO₂)",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
            font=dict(color='#546E7A')
        )
        # Add hover template with appropriate units
        fig_environmental.update_traces(
            hovertemplate='<b>%{y:,.2f}</b><extra></extra>'
        )
        st.plotly_chart(fig_environmental, use_container_width=True)

    # Implementation Notes in a consistent format
    st.markdown('<div class="section-subheader">📘 Implementation Parameters & Details</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="implementation-notes">
        <div class="note-item"><span>Implementation Timeline:</span> <strong>{settings['implementation_months']} months</strong></div>
        <div class="note-item"><span>Total Storage Actions:</span> <strong>{metrics['total_actions']:,} actions</strong></div>
        <div class="note-item"><span>Average Size per Action:</span> <strong>{metrics['avg_storage_gb']:.2f} GB</strong></div>
        <div class="note-item"><span>Monthly Storage Rate:</span> <strong>${settings['cost_per_gb']:.2f}/GB/month</strong></div>
        <div class="note-item"><span>Staff Hourly Rate:</span> <strong>AED {settings['min_rate_aed']:.2f}/hour</strong></div>
        <div class="note-item"><span>Time Required per Action:</span> <strong>{settings['min_minutes']} minutes</strong></div>
        <div class="note-item"><span>Automation Distribution:</span> <strong>{settings['turbo_pct']}% Turbonomic, {100-settings['turbo_pct']}% AAP</strong></div>
        <div class="note-item"><span>Automation Unit Costs:</span> <strong>Turbonomic: ${settings['turbo_unit_cost_usd']:.2f}, AAP: ${settings['aap_unit_cost_usd']:.2f}</strong></div>
        <div class="note-item"><span>Energy Consumption Rate:</span> <strong>{settings['energy_kwh']:.4f} kWh/GB/month</strong></div>
        <div class="note-item"><span>Cooling Efficiency Factor:</span> <strong>{settings['cooling']:.2f}</strong></div>
        <div class="note-item"><span>Carbon Emission Rate:</span> <strong>{settings['co2_rate']:.2f} kg CO₂/kWh</strong></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Next steps section with improved styling
    st.markdown("""
    <div class="summary-container">
        <div class="summary-header">
            <div class="summary-icon">🚀</div>
            <div class="summary-title">Next Steps</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Next step navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        st.button("📈 View Long-term Forecast", 
                 type="primary", 
                 key="view_forecast", 
                 on_click=navigate_to, 
                 args=('forecast',),
                 use_container_width=True)
    with col2:
        st.button("📊 Explore Visualizations", 
                 key="explore_visualizations", 
                 on_click=navigate_to, 
                 args=('visualizations',),
                 use_container_width=True)
    
    # Close the summary container
    st.markdown("</div>", unsafe_allow_html=True)

# Callback function for navigation
def navigate_to(page):
    st.session_state['current_view'] = page

def initialize_settings():
    if 'settings' not in st.session_state:
        # Load configuration defaults
        with open("config/config.json", "r") as f:
            config = json.load(f)
            
        st.session_state.settings = {
            'cost_per_gb': config['cost_per_gb_per_month_usd'],
            'retention': 6,
            'conversion_rate': config['currency_conversion_rate'],
            'energy_kwh': 0.0008,
            'cooling': config['cooling_multiplier'],
            'co2_rate': config['co2_per_kwh'],
            'min_minutes': 13,
            'max_minutes': 33,
            'min_rate_aed': 100,
            'max_rate_aed': 250,
            'turbo_pct': 70,
            'turbo_unit_cost_usd': 0.25,
            'aap_unit_cost_usd': 0.15,
            'forecast_growth_rate': 0.15,
            'implementation_months': 6
        }

@st.cache_data(ttl=3600)
def calculate_metrics(df, settings):
    # Calculate base metrics
    total_storage_gb = df['file_size_(gb)'].sum()
    avg_storage_gb = df['file_size_(gb)'].mean()
    total_actions = len(df)
    
    # Calculate first year metrics
    first_year_storage_savings = total_storage_gb * settings['cost_per_gb'] * settings['implementation_months']
    first_year_labor_savings = (total_actions * settings['min_minutes'] / 60 * settings['min_rate_aed']) / settings['conversion_rate']
    first_year_automation_cost = total_actions * (
        (settings['turbo_pct']/100 * settings['turbo_unit_cost_usd']) + 
        ((100-settings['turbo_pct'])/100 * settings['aap_unit_cost_usd'])
    )
    
    # Sustainability metrics
    total_energy = settings['energy_kwh'] * (1 + settings['cooling'])
    first_year_energy_savings = total_storage_gb * settings['energy_kwh'] * settings['implementation_months']
    first_year_cooling_savings = total_storage_gb * settings['energy_kwh'] * settings['cooling'] * settings['implementation_months']
    first_year_carbon_savings = total_storage_gb * total_energy * settings['co2_rate'] * settings['implementation_months']
    first_year_net_savings = first_year_storage_savings + first_year_labor_savings - first_year_automation_cost
    
    return {
        'total_storage_gb': total_storage_gb,
        'avg_storage_gb': avg_storage_gb,
        'total_actions': total_actions,
        'first_year_storage_savings': first_year_storage_savings,
        'first_year_labor_savings': first_year_labor_savings,
        'first_year_automation_cost': first_year_automation_cost,
        'first_year_energy_savings': first_year_energy_savings,
        'first_year_cooling_savings': first_year_cooling_savings,
        'first_year_carbon_savings': first_year_carbon_savings,
        'first_year_net_savings': first_year_net_savings
    }