import streamlit as st
import json

def render():
    # Custom title with consistent styling
    st.markdown('<div class="page-title">⚙️ Configuration Center</div>', unsafe_allow_html=True)
    
    # Introduction
    st.markdown("""
    <div class="welcome-banner">
        <h2>ROI Configuration Settings</h2>
        <p>Configure the parameters that will be used to calculate the ROI for storage optimization across your infrastructure.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load configuration defaults
    with open("config/config.json", "r") as f:
        config = json.load(f)

    # Initialize session state for settings if not exists
    if 'settings' not in st.session_state:
        st.session_state.settings = {
            'cost_per_gb': config['cost_per_gb_per_month_usd'],
            'retention': 6,  # Default to 6 months, will be linked to implementation period
            'conversion_rate': config['currency_conversion_rate'],
            'energy_kwh': 0.0008,
            'cooling': config['cooling_multiplier'],
            'co2_rate': config['co2_per_kwh'],
            'min_minutes': 13,
            'max_minutes': 33,
            'min_rate_aed': 100,
            'max_rate_aed': 250,
            'turbo_pct': 70,
            'turbo_unit_cost_usd': 0.25,  # Cost per action
            'aap_unit_cost_usd': 0.15,    # Cost per action
            'forecast_growth_rate': 0.15,  # 15% growth in recommendations per month
            'implementation_months': 6      # Number of months to implement all recommendations
        }
    else:
        # Ensure all required settings exist in session state
        required_settings = {
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
        
        # Add any missing settings
        for key, default_value in required_settings.items():
            if key not in st.session_state.settings:
                st.session_state.settings[key] = default_value

    # Add CSS for tabs and styling
    st.markdown("""
    <style>
    .settings-nav {
        display: flex;
        background-color: #f8f9fa;
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 1.5rem;
        border: 1px solid #e0e0e0;
    }
    
    .nav-tab {
        flex: 1;
        text-align: center;
        padding: 0.8rem 1rem;
        cursor: pointer;
        font-weight: 500;
        color: #546E7A;
        transition: all 0.2s;
    }
    
    .nav-tab:first-child {
        border-right: 1px solid #e0e0e0;
    }
    
    .nav-tab.active {
        background-color: #1976D2;
        color: white;
    }
    
    .settings-group {
        margin-bottom: 1.5rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid #f0f0f0;
    }
    
    .settings-group:last-child {
        border-bottom: none;
        margin-bottom: 0;
        padding-bottom: 0;
    }
    
    .group-title {
        font-size: 1.1rem;
        font-weight: 500;
        color: #1976D2;
        margin-bottom: 1rem;
    }
    
    .input-info {
        font-size: 0.85rem;
        color: #546E7A;
        margin-bottom: 0.5rem;
    }
    
    /* Improved ROI Summary Section */
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

    .summary-header {
        display: flex;
        align-items: center;
        margin-bottom: 1.2rem;
    }

    .summary-icon {
        font-size: 1.5rem;
        color: #1976D2;
        margin-right: 0.8rem;
    }

    .summary-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # If tab selection is not in session state, initialize it
    if 'settings_tab' not in st.session_state:
        st.session_state.settings_tab = 0
    
    # Simple two-button approach for tabs
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💰 Cost & Energy Settings", key="cost_energy_tab", 
                     use_container_width=True,
                     type="primary" if st.session_state.settings_tab == 0 else "secondary"):
            st.session_state.settings_tab = 0
            st.rerun()
    
    with col2:
        if st.button("🧑‍💻 Labor & Automation Settings", key="labor_automation_tab", 
                     use_container_width=True,
                     type="primary" if st.session_state.settings_tab == 1 else "secondary"):
            st.session_state.settings_tab = 1
            st.rerun()
    
    # Display the appropriate settings section based on selected tab
    if st.session_state.settings_tab == 0:
        render_cost_energy_settings()
    else:
        render_labor_automation_settings()
    
    # Enhanced Summary & Save Section
    st.markdown("""
    <div class="summary-container">
        <div class="summary-header">
            <div class="summary-icon">📊</div>
            <div class="summary-title">ROI Configuration Summary</div>
        </div>
    """, unsafe_allow_html=True)

    # Create customized metrics row
    st.markdown(f"""
    <div class="metrics-row">
        <div class="metric-item">
            <div class="metric-label">Storage Cost</div>
            <div class="metric-value">${st.session_state.settings['cost_per_gb']:.3f}/GB</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">Implementation</div>
            <div class="metric-value">{st.session_state.settings['implementation_months']} months</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">Automation</div>
            <div class="metric-value">{st.session_state.settings['turbo_pct']}% / {100-st.session_state.settings['turbo_pct']}%</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">Growth Rate</div>
            <div class="metric-value">{st.session_state.settings['forecast_growth_rate']*100:.1f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Add buttons using Streamlit's native buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Configuration", type="primary", key="save_config", use_container_width=True):
            st.success("✅ Configuration saved successfully! These settings will be applied to all future processing operations.")
    with col2:
        if st.button("Continue to Upload & Process →", key="continue_to_upload", use_container_width=True):
            st.session_state['current_view'] = 'upload_process'
            st.rerun()

    # Close the summary container
    st.markdown("</div>", unsafe_allow_html=True)

def render_cost_energy_settings():
    """Render the Cost & Energy settings section"""
    
    # Storage Costs Group
    st.markdown('<div class="group-title">Storage Costs</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        help_text = "Monthly cost of storing 1GB of data in your infrastructure"
        st.markdown('<div class="input-info">The monthly cost per GB affects all ROI calculations</div>', unsafe_allow_html=True)
        st.session_state.settings['cost_per_gb'] = st.number_input(
            '💵 Cost per GB (USD/month)',
            value=st.session_state.settings['cost_per_gb'],
            help=help_text,
            key="cost_per_gb"
        )
    
    with col2:
        help_text = "Exchange rate for converting USD costs to AED"
        st.markdown('<div class="input-info">Exchange rate for local reporting in AED</div>', unsafe_allow_html=True)
        st.session_state.settings['conversion_rate'] = st.number_input(
            '💱 USD to AED Rate',
            value=st.session_state.settings['conversion_rate'],
            help=help_text,
            key="conversion_rate"
        )
    
    help_text = "How long the storage would have remained if no action was taken"
    st.markdown('<div class="input-info">This value is linked to the implementation period</div>', unsafe_allow_html=True)
    st.session_state.settings['retention'] = st.slider(
        '🕒 Expected Duration Without Action (months)',
        min_value=1,
        max_value=12,
        value=st.session_state.settings['retention'],
        help=help_text,
        key="retention"
    )
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Energy & Environmental Impact Group
    st.markdown('<div class="group-title">Energy & Environmental Impact</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        help_text = "Monthly energy consumption for storing 1GB (UAE data center standard: 0.0008 kWh/GB/month)"
        st.markdown('<div class="input-info">Energy used per GB of storage per month</div>', unsafe_allow_html=True)
        st.session_state.settings['energy_kwh'] = st.number_input(
            '🔌 Energy per GB (kWh/month)',
            value=st.session_state.settings['energy_kwh'],
            min_value=0.0001,
            max_value=0.01,
            step=0.0001,
            format="%.4f",
            help=help_text,
            key="energy_kwh"
        )
    
    with col2:
        help_text = "Carbon emissions per kilowatt-hour of energy consumed"
        st.markdown('<div class="input-info">CO₂ emissions for environmental impact assessment</div>', unsafe_allow_html=True)
        st.session_state.settings['co2_rate'] = st.number_input(
            '🌍 CO₂ per kWh (kg)',
            value=st.session_state.settings['co2_rate'],
            help=help_text,
            key="co2_rate"
        )
    
    help_text = "Additional energy needed for cooling (e.g., 0.5 means 50% more energy for cooling)"
    st.markdown('<div class="input-info">Factor to account for data center cooling requirements</div>', unsafe_allow_html=True)
    st.session_state.settings['cooling'] = st.slider(
        '❄️ Cooling Multiplier',
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.settings['cooling'],
        step=0.1,
        help=help_text,
        key="cooling"
    )

def render_labor_automation_settings():
    """Render the Labor & Automation settings section"""
    
    # Manual Labor Costs Group
    st.markdown('<div class="group-title">Manual Labor Costs</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="input-info">Time range for manual operations</div>', unsafe_allow_html=True)
        help_text = "Minimum time needed for manual storage management tasks"
        st.session_state.settings['min_minutes'] = st.number_input(
            '⏱️ Min Manual Time per Action (min)',
            value=st.session_state.settings['min_minutes'],
            min_value=1,
            max_value=60,
            help=help_text,
            key="min_minutes"
        )
        
        help_text = "Maximum time needed for manual storage management tasks"
        st.session_state.settings['max_minutes'] = st.number_input(
            '⏱️ Max Manual Time per Action (min)',
            value=st.session_state.settings['max_minutes'],
            min_value=1,
            max_value=120,
            help=help_text,
            key="max_minutes"
        )
    
    with col2:
        st.markdown('<div class="input-info">Cost range for staff performing actions</div>', unsafe_allow_html=True)
        help_text = "Minimum hourly rate for storage management staff"
        st.session_state.settings['min_rate_aed'] = st.number_input(
            '💵 Min Hourly Rate (AED)',
            value=st.session_state.settings['min_rate_aed'],
            min_value=50,
            max_value=200,
            help=help_text,
            key="min_rate_aed"
        )
        
        help_text = "Maximum hourly rate for storage management staff"
        st.session_state.settings['max_rate_aed'] = st.number_input(
            '💵 Max Hourly Rate (AED)',
            value=st.session_state.settings['max_rate_aed'],
            min_value=100,
            max_value=500,
            help=help_text,
            key="max_rate_aed"
        )
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Automation Platform Costs Group
    st.markdown('<div class="group-title">Automation Platform Costs</div>', unsafe_allow_html=True)
    
    help_text = "Percentage of actions handled by Turbonomic"
    st.markdown('<div class="input-info">Distribution of automated tasks between platforms</div>', unsafe_allow_html=True)
    st.session_state.settings['turbo_pct'] = st.slider(
        '⚙️ Turbonomic Execution %',
        min_value=0,
        max_value=100,
        value=st.session_state.settings['turbo_pct'],
        help=help_text,
        key="turbo_pct"
    )
    aap_pct = 100 - st.session_state.settings['turbo_pct']
    st.write(f"AAP Execution: **{aap_pct}%**")
    
    col1, col2 = st.columns(2)
    with col1:
        help_text = "Cost per action when executed by Turbonomic"
        st.markdown('<div class="input-info">Unit cost for Turbonomic actions</div>', unsafe_allow_html=True)
        st.session_state.settings['turbo_unit_cost_usd'] = st.number_input(
            '💰 Turbo Cost per Action (USD)',
            value=st.session_state.settings['turbo_unit_cost_usd'],
            min_value=0.01,
            max_value=1.0,
            step=0.01,
            help=help_text,
            key="turbo_unit_cost_usd"
        )
    
    with col2:
        help_text = "Cost per action when executed by AAP"
        st.markdown('<div class="input-info">Unit cost for AAP actions</div>', unsafe_allow_html=True)
        st.session_state.settings['aap_unit_cost_usd'] = st.number_input(
            '💵 AAP Cost per Action (USD)',
            value=st.session_state.settings['aap_unit_cost_usd'],
            min_value=0.01, 
            max_value=1.0,
            step=0.01,
            help=help_text,
            key="aap_unit_cost_usd"
        )
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Forecast Parameters Section
    st.markdown('<div class="group-title">Forecast Parameters</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        help_text = "Expected monthly growth in recommendations"
        st.markdown('<div class="input-info">Projected increase in recommendations per month</div>', unsafe_allow_html=True)
        growth_rate_pct = st.number_input(
            '📈 Monthly Growth Rate (%)',
            value=st.session_state.settings['forecast_growth_rate'] * 100,
            min_value=0.0,
            max_value=100.0,
            step=0.1,
            format="%.1f",
            help=help_text,
            key="forecast_growth_rate_pct"
        )
        # Convert percentage to decimal
        st.session_state.settings['forecast_growth_rate'] = growth_rate_pct / 100
    
    with col2:
        help_text = "Number of months to implement all recommendations"
        st.markdown('<div class="input-info">Timeline for implementing all recommendations</div>', unsafe_allow_html=True)
        st.session_state.settings['implementation_months'] = st.number_input(
            '⏱️ Implementation Period (months)',
            value=st.session_state.settings['implementation_months'],
            min_value=1,
            max_value=12,
            help=help_text,
            key="implementation_months"
        )
        
        # Link retention period to implementation period
        st.session_state.settings['retention'] = st.session_state.settings['implementation_months']