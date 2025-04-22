import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from views.helpers import load_processed_data
import json

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

def render():
    st.title("📊 ROI Summary")
    
    # Initialize settings if not exists
    initialize_settings()

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

    # First Year Implementation ROI
    st.markdown("### 🎯 First Year Implementation ROI")
    st.markdown(f"*Based on {settings['implementation_months']}-month implementation period*")

    # First Year Metrics Cards
    st.markdown("#### 💰 Financial Impact")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Storage Savings",
            f"${metrics['first_year_storage_savings']:,.0f}",
            "First year implementation",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            "Labor Savings",
            f"${metrics['first_year_labor_savings']:,.0f}",
            "First year implementation",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            "Automation Cost",
            f"${metrics['first_year_automation_cost']:,.0f}",
            "First year implementation",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            "Net Savings",
            f"${metrics['first_year_net_savings']:,.0f}",
            "First year implementation",
            delta_color="normal"
        )

    # Sustainability Metrics Cards
    st.markdown("#### 🌱 Environmental Impact")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Energy Savings",
            f"{metrics['first_year_energy_savings']:,.0f} kWh",
            "First year implementation"
        )
    
    with col2:
        st.metric(
            "Cooling Savings",
            f"{metrics['first_year_cooling_savings']:,.0f} kWh",
            "First year implementation"
        )
    
    with col3:
        st.metric(
            "Carbon Reduction",
            f"{metrics['first_year_carbon_savings']:,.0f} kg CO₂",
            "First year implementation"
        )

    # First Year Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Financial Impact Breakdown
        fig_financial = go.Figure(data=[
            go.Bar(name='Storage Savings', y=[metrics['first_year_storage_savings']], marker_color=SAVINGS_COLOR),
            go.Bar(name='Labor Savings', y=[metrics['first_year_labor_savings']], marker_color=SAVINGS_COLOR),
            go.Bar(name='Automation Cost', y=[-metrics['first_year_automation_cost']], marker_color=COST_COLOR)
        ])
        fig_financial.update_layout(
            title='Financial Impact Breakdown',
            barmode='relative',
            showlegend=True,
            height=400,
            yaxis_title="Amount (USD)"
        )
        st.plotly_chart(fig_financial, use_container_width=True)
    
    with col2:
        # Environmental Impact Breakdown
        fig_environmental = go.Figure(data=[
            go.Bar(name='Energy Savings', y=[metrics['first_year_energy_savings']], marker_color=ENERGY_COLOR),
            go.Bar(name='Cooling Savings', y=[metrics['first_year_cooling_savings']], marker_color=COOLING_COLOR),
            go.Bar(name='Carbon Reduction', y=[metrics['first_year_carbon_savings']], marker_color=CARBON_COLOR)
        ])
        fig_environmental.update_layout(
            title='Environmental Impact Breakdown',
            barmode='group',
            showlegend=True,
            height=400,
            yaxis_title="Amount"
        )
        st.plotly_chart(fig_environmental, use_container_width=True)

    # Implementation Notes
    with st.expander("📘 Implementation Notes", expanded=True):
        st.markdown(f"""
        - **Implementation Period**: {settings['implementation_months']} months
        - **Total Actions**: {metrics['total_actions']:,} actions to be implemented
        - **Average Storage per Action**: {metrics['avg_storage_gb']:.2f} GB
        - **Storage Cost per GB**: ${settings['cost_per_gb']:.2f}/month
        - **Labor Rate**: AED {settings['min_rate_aed']:.2f}/hour
        - **Average Time per Action**: {settings['min_minutes']} minutes
        - **Automation Split**: {settings['turbo_pct']}% Turbonomic, {100-settings['turbo_pct']}% AAP
        - **Automation Cost per Action**: Turbonomic: ${settings['turbo_unit_cost_usd']:.2f}, AAP: ${settings['aap_unit_cost_usd']:.2f}
        - **Energy per GB**: {settings['energy_kwh']:.4f} kWh/month
        - **Cooling Multiplier**: {settings['cooling']:.2f}
        - **CO₂ per kWh**: {settings['co2_rate']:.2f} kg
        """)

    if st.button("View Forecast"):
        st.session_state['current_view'] = 'forecast'
        st.rerun()
