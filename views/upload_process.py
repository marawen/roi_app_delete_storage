import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os
from views.helpers import initialize_settings, calculate_financial_metrics

def render():
    st.title("📁 Upload & Process")
    st.markdown("Upload your Turbonomic Delete Storage recommendation Excel file and customize ROI parameters.")

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
            'turbo_unit_cost_usd': 0.25,
            'aap_unit_cost_usd': 0.15,
            'forecast_growth_rate': 0.15,
            'implementation_months': 6
        }
        
        # Add any missing settings
        for key, default_value in required_settings.items():
            if key not in st.session_state.settings:
                st.session_state.settings[key] = default_value

    # Create main tabs
    tab1, tab2 = st.tabs(["⚙️ Settings", "📤 Upload & Process"])

    # Settings tab content
    with tab1:
        st.markdown("### ⚙️ ROI Configuration Settings")
        st.markdown("Configure the parameters that will be used to calculate the ROI for storage optimization.")

        # Create subtabs for different setting categories
        settings_tab1, settings_tab2 = st.tabs([
            "💰 Cost & Energy", 
            "🧑‍💻 Labor & Automation"
        ])

        with settings_tab1:
            st.markdown("#### Storage and Energy Cost Parameters")
            st.markdown("These parameters define the cost structure of your storage infrastructure and its environmental impact.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### Storage Costs")
                with st.expander("ℹ️ About Storage Costs", expanded=False):
                    st.markdown("""
                    - **Cost per GB**: The monthly cost of storing 1GB of data
                    - **Retention Period**: How long data is typically stored before deletion
                    - **Currency Rate**: Converts USD costs to AED for local reporting
                    """)
                
                st.session_state.settings['cost_per_gb'] = st.number_input(
                    '💵 Cost per GB (USD/month)',
                    value=st.session_state.settings['cost_per_gb'],
                    help="Monthly cost of storing 1GB of data in your infrastructure"
                )
                st.session_state.settings['retention'] = st.number_input(
                    '🕒 Expected Duration Without Action (months)',
                    value=st.session_state.settings['retention'],
                    help="How long the storage would have remained if no action was taken"
                )
                st.session_state.settings['conversion_rate'] = st.number_input(
                    '💱 USD to AED Rate',
                    value=st.session_state.settings['conversion_rate'],
                    help="Exchange rate for converting USD costs to AED"
                )

            with col2:
                st.markdown("##### Energy & Environmental Impact")
                with st.expander("ℹ️ About Energy Impact", expanded=False):
                    st.markdown("""
                    - **Energy per GB**: Power consumption for storing 1GB
                    - **Cooling Multiplier**: Additional energy needed for cooling
                    - **CO₂ Rate**: Carbon emissions per kWh of energy
                    """)
                
                st.session_state.settings['energy_kwh'] = st.number_input(
                    '🔌 Energy per GB (kWh/month)',
                    value=st.session_state.settings['energy_kwh'],
                    min_value=0.0001,
                    max_value=0.01,
                    step=0.0001,
                    format="%.4f",
                    help="Monthly energy consumption for storing 1GB (UAE data center standard: 0.0008 kWh/GB/month)"
                )
                st.session_state.settings['cooling'] = st.number_input(
                    '❄️ Cooling Multiplier',
                    value=st.session_state.settings['cooling'],
                    help="Additional energy needed for cooling (e.g., 0.5 means 50% more energy for cooling)"
                )
                st.session_state.settings['co2_rate'] = st.number_input(
                    '🌍 CO₂ per kWh (kg)',
                    value=st.session_state.settings['co2_rate'],
                    help="Carbon emissions per kilowatt-hour of energy consumed"
                )

        with settings_tab2:
            st.markdown("#### Labor and Automation Parameters")
            st.markdown("Define the costs and efficiencies of manual operations versus automated solutions.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### Manual Labor Costs")
                with st.expander("ℹ️ About Labor Costs", expanded=False):
                    st.markdown("""
                    - **Time per Action**: Range of time needed for manual operations
                    - **Hourly Rates**: Cost of labor in AED per hour
                    - These parameters help calculate potential labor savings
                    """)
                
                st.session_state.settings['min_minutes'] = st.number_input(
                    '⏱️ Min Manual Time per Action (min)',
                    value=st.session_state.settings['min_minutes'],
                    help="Minimum time needed for manual storage management tasks"
                )
                st.session_state.settings['max_minutes'] = st.number_input(
                    '⏱️ Max Manual Time per Action (min)',
                    value=st.session_state.settings['max_minutes'],
                    help="Maximum time needed for manual storage management tasks"
                )
                st.session_state.settings['min_rate_aed'] = st.number_input(
                    '💵 Min Hourly Rate (AED)',
                    value=st.session_state.settings['min_rate_aed'],
                    help="Minimum hourly rate for storage management staff"
                )
                st.session_state.settings['max_rate_aed'] = st.number_input(
                    '💵 Max Hourly Rate (AED)',
                    value=st.session_state.settings['max_rate_aed'],
                    help="Maximum hourly rate for storage management staff"
                )

            with col2:
                st.markdown("##### Automation Platform Costs")
                with st.expander("ℹ️ About Automation Costs", expanded=False):
                    st.markdown("""
                    - **Turbonomic/AAP Split**: Distribution of automated tasks
                    - **Cost per Action**: Cost of automated solutions
                    """)
                
                st.session_state.settings['turbo_pct'] = st.slider(
                    '⚙️ Turbonomic Execution %',
                    min_value=0,
                    max_value=100,
                    value=st.session_state.settings['turbo_pct'],
                    help="Percentage of actions handled by Turbonomic"
                )
                aap_pct = 100 - st.session_state.settings['turbo_pct']
                
                st.session_state.settings['turbo_unit_cost_usd'] = st.number_input(
                    '💰 Turbo Cost per Action (USD)',
                    value=st.session_state.settings['turbo_unit_cost_usd'],
                    min_value=0.01,
                    step=0.01,
                    help="Cost per action when executed by Turbonomic"
                )
                st.session_state.settings['aap_unit_cost_usd'] = st.number_input(
                    '💵 AAP Cost per Action (USD)',
                    value=st.session_state.settings['aap_unit_cost_usd'],
                    min_value=0.01,
                    step=0.01,
                    help="Cost per action when executed by AAP"
                )

                # Add forecast parameters
                st.markdown("##### Forecast Parameters")
                with st.expander("ℹ️ About Forecast Parameters", expanded=False):
                    st.markdown("""
                    - **Growth Rate**: Expected monthly growth in recommendations
                    - **Implementation Period**: Time to implement all recommendations (also sets the expected duration without action)
                    """)
                
                st.session_state.settings['forecast_growth_rate'] = st.number_input(
                    '📈 Monthly Growth Rate (%)',
                    value=st.session_state.settings['forecast_growth_rate'] * 100,
                    min_value=0.0,
                    max_value=100.0,
                    step=0.1,
                    format="%.1f",
                    help="Expected monthly growth in recommendations"
                ) / 100  # Convert percentage to decimal
                
                st.session_state.settings['implementation_months'] = st.number_input(
                    '⏱️ Implementation Period (months)',
                    value=st.session_state.settings['implementation_months'],
                    min_value=1,
                    max_value=12,
                    help="Number of months to implement all recommendations"
                )
                
                # Link retention period to implementation period
                st.session_state.settings['retention'] = st.session_state.settings['implementation_months']

    # Upload & Process tab content
    with tab2:
        uploaded_file = st.file_uploader("Upload Turbonomic Excel File (.xlsx)", type=["xlsx"])

        if uploaded_file:
            try:
                # Read the Excel file
                df = pd.read_excel(uploaded_file)
                df = df.replace(r'^\s*$', pd.NA, regex=True)
                df.columns = (
                    df.columns.str.strip()
                              .str.lower()
                              .str.replace(' ', '_')
                              .str.replace('-', '_')
                )
                df = df.dropna(axis=1, how='all')

                # Clean last_modified_on column
                if 'last_modified_on' in df.columns:
                    df['last_modified_on'] = df['last_modified_on'].astype(str).str.strip().str.replace('"', '', regex=False)

                # 📅 Enhanced Date Feature Engineering
                today = pd.Timestamp(datetime.today().date())

                # Date Created
                df['date_created_parsed'] = pd.to_datetime(df['date_created'], errors='coerce')
                df['age_days'] = (today - df['date_created_parsed']).dt.days
                df['created_year'] = df['date_created_parsed'].dt.year
                df['created_month'] = df['date_created_parsed'].dt.month
                df['created_day'] = df['date_created_parsed'].dt.day

                # Last Modified
                df['last_modified_parsed'] = pd.to_datetime(df['last_modified_on'], format='%d/%m/%Y', errors='coerce')
                df['last_access_age_days'] = (today - df['last_modified_parsed']).dt.days
                df['last_modified_year'] = df['last_modified_parsed'].dt.year
                df['last_modified_month'] = df['last_modified_parsed'].dt.month
                df['last_modified_day'] = df['last_modified_parsed'].dt.day
                df['detach_days'] = df['container_cluster'].str.extract(r'(\d+)').astype(float)

                # Update location inference
                df['location_info'] = df['name'].apply(extract_location_code)
                df['inferred_location'] = df['location_info'].apply(lambda x: x[0])
                df['location_type'] = df['location_info'].apply(lambda x: x[1])
                df = df.drop('location_info', axis=1)

                # Create a more descriptive location label
                df['location_label'] = df.apply(
                    lambda row: f"{row['inferred_location']} ({row['location_type']})" 
                    if pd.notna(row['inferred_location']) and row['inferred_location'] is not None
                    else 'Unknown Location', 
                    axis=1
                )

                # Confidence & ROI score
                df['confidence_score'] = df['risk'].apply(
                    lambda x: 1.0 if 'accepted and executed immediately' in str(x).lower() else 0.5
                )

                df['roi_score'] = (
                    (df['file_size_(gb)'] * 2) +
                    (df['age_days'].fillna(0) / 365) +
                    (df['detach_days'].fillna(0) / 365) +
                    (df['confidence_score'] * 5)
                )

                # 📊 Monthly Aggregation Summary (Rounded)
                df['roi_month'] = df['created_year'].astype(str) + '-' + df['created_month'].astype(str).str.zfill(2)
                
                # Calculate all financial metrics using our centralized function
                results = calculate_financial_metrics(df, st.session_state.settings)
                
                if results is not None:
                    # Store processed data
                    processed_df = results['processed_df']
                    monthly_metrics = results['monthly_metrics']
                    totals = results['totals']
                    
                    # Save processed data
                    os.makedirs('outputs', exist_ok=True)
                    processed_df.to_csv('outputs/processed_data.csv', index=False)
                    st.session_state['processed_df'] = processed_df
                    
                    # Display success message with summary
                    st.success(f"""
                    ✅ Data processed successfully!
                    
                    Summary:
                    - Total Actions: {len(processed_df):,}
                    - Total Storage: {totals['storage_savings_usd']:,.2f} GB
                    - Estimated Savings: ${totals['net_savings_usd']:,.2f}
                    """)
                    
                    # Display monthly summary
                    st.markdown("### 📊 Monthly Summary")
                    styled_monthly = style_monthly_summary(monthly_metrics)
                    st.dataframe(styled_monthly, use_container_width=True, hide_index=True)
                    
                else:
                    st.error("Error processing financial metrics")
            
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")

def infer_platform(x):
    if 'win' in x:
        return 'Windows'
    elif '.vmx' in x or '.vmdk' in x:
        return 'Linux'
    elif 'veeam' in x:
        return 'Veeam'
    return 'Unknown'

def extract_location_code(filename):
    """
    Extract location code from filename using specific patterns.
    Returns tuple of (location_code, location_type)
    """
    # Common location patterns
    data_centers = {'AUH', 'DXB', 'AJM'}
    
    # Try to find location code in the filename
    # Pattern 1: Look for 3-letter codes that match our data centers
    for dc in data_centers:
        if dc in str(filename).upper():
            return dc, 'Data Center'
    
    # Pattern 2: Look for other business domain codes (3-4 uppercase letters)
    import re
    match = re.search(r'[/_-]([A-Z]{3,4})[/_-]', f"_{str(filename).upper()}_")
    if match:
        code = match.group(1)
        if code in data_centers:
            return code, 'Data Center'
        return code, 'Business Domain'
    
    return None, 'Unknown'

def style_monthly_summary(df):
    """Apply styling to monthly summary dataframe."""
    return df.style.format({
        'storage_cost_usd': '${:,.2f}',
        'storage_cost_aed': 'AED {:,.2f}',
        'energy_savings': '{:,.2f} kWh',
        'cooling_savings': '{:,.2f} kWh',
        'carbon_savings': '{:,.2f} kg',
        'labor_cost_usd': '${:,.2f}',
        'automation_cost_usd': '${:,.2f}',
        'net_savings_usd': '${:,.2f}',
        'file_size_(gb)': '{:,.2f} GB'
    }).set_table_styles([{
        'selector': 'th',
        'props': [
            ('background-color', '#f0f0f0'),
            ('font-weight', 'bold'),
            ('text-align', 'center')
        ]
    }])