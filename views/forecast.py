import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import os
from views.helpers import load_processed_data

def render():
    st.title("📈 Storage Optimization Forecast")
    
    # Check if data has been processed or exists in outputs
    if 'processed_df' not in st.session_state:
        output_path = "outputs/processed_output.csv"
        if os.path.exists(output_path):
            try:
                df = pd.read_csv(output_path)
                st.session_state['processed_df'] = df
                st.success("✅ Loaded previously processed data from outputs directory.")
            except Exception as e:
                st.error(f"Error loading processed data: {str(e)}")
                st.warning("""
                ⚠️ No data available for forecast.
                
                To view the forecast:
                1. Go to the **Upload & Process** tab
                2. Upload your Turbonomic Excel file
                3. Process the data
                4. Return to this tab to view the forecast
                """)
                return
        else:
            st.warning("""
            ⚠️ No data available for forecast.
            
            To view the forecast:
            1. Go to the **Upload & Process** tab
            2. Upload your Turbonomic Excel file
            3. Process the data
            4. Return to this tab to view the forecast
            """)
            return

    df = st.session_state['processed_df']
    settings = st.session_state.settings

    # Add a refresh button to recalculate forecast
    if st.button("🔄 Refresh Forecast"):
        st.rerun()

    # Calculate base metrics
    total_storage_gb = df['file_size_(gb)'].sum()
    avg_storage_gb = df['file_size_(gb)'].mean()
    total_actions = len(df)
    base_actions = total_actions / df['roi_month'].nunique()  # Average actions per month from historical data
    
    # Create forecast DataFrame
    months = pd.date_range(start=datetime.today(), periods=12, freq='MS')
    forecast = pd.DataFrame({'Month': months})
    
    # Calculate actions for each phase
    implementation_months = settings['implementation_months']
    ongoing_monthly_actions = base_actions * 0.15  # 15% of historical monthly average
    
    # Initialize actions array
    actions_array = np.zeros(12)
    
    # Fill implementation phase
    if implementation_months > 0:
        monthly_implementation_actions = total_actions / implementation_months
        actions_array[:implementation_months] = monthly_implementation_actions
    
    # Fill ongoing phase with 15% of monthly average
    actions_array[implementation_months:] = ongoing_monthly_actions
    
    # Apply growth rate to ongoing phase only
    month_range = np.arange(12 - implementation_months)  # Only for ongoing phase
    growth_factor = (1 + settings['forecast_growth_rate'])
    growth_multiplier = growth_factor ** month_range
    
    # Only apply growth to ongoing phase
    if implementation_months < 12:
        actions_array[implementation_months:] *= growth_multiplier
    
    # Assign to forecast DataFrame
    forecast['Actions'] = actions_array
    
    # Calculate storage metrics
    forecast['Reclaimable Storage (GB)'] = forecast['Actions'] * avg_storage_gb
    forecast['Storage Savings (USD)'] = (
        forecast['Reclaimable Storage (GB)'] * 
        settings['cost_per_gb'] * 
        settings['implementation_months']
    )
    
    # Calculate energy metrics
    total_energy = settings['energy_kwh'] * (1 + settings['cooling'])
    forecast['Energy Savings (kWh)'] = (
        forecast['Reclaimable Storage (GB)'] * 
        settings['energy_kwh'] * 
        settings['implementation_months']
    )
    forecast['Cooling Savings (kWh)'] = (
        forecast['Reclaimable Storage (GB)'] * 
        settings['energy_kwh'] * 
        settings['cooling'] * 
        settings['implementation_months']
    )
    forecast['Carbon Savings (kg)'] = (
        forecast['Reclaimable Storage (GB)'] * 
        total_energy * 
        settings['co2_rate'] * 
        settings['implementation_months']
    )
    
    # Calculate labor savings
    forecast['Labor Hours'] = forecast['Actions'] * settings['min_minutes'] / 60
    forecast['Labor Savings (USD)'] = (
        forecast['Labor Hours'] * 
        settings['min_rate_aed'] / 
        settings['conversion_rate']
    )
    
    # Calculate automation costs
    forecast['Automation Cost (USD)'] = forecast['Actions'] * (
        (settings['turbo_pct']/100 * settings['turbo_unit_cost_usd']) + 
        ((100-settings['turbo_pct'])/100 * settings['aap_unit_cost_usd'])
    )
    
    # Calculate net savings
    forecast['Net Savings (USD)'] = (
        forecast['Storage Savings (USD)'] + 
        forecast['Labor Savings (USD)'] - 
        forecast['Automation Cost (USD)']
    )
    
    # Display source data information
    st.markdown("### 📊 Source Data Information")
    
    # Create metrics columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Average Storage per Action",
            f"{avg_storage_gb:.2f} GB",
            help="Average storage space that can be reclaimed per action"
        )
        
    with col2:
        st.metric(
            "Base Actions per Month",
            f"{base_actions:.0f}",
            help="Average number of actions per month from historical data"
        )
        
    with col3:
        st.metric(
            "Implementation Actions/Month",
            f"{(total_actions/implementation_months):.0f}",
            help="Actions per month during implementation phase"
        )
        
    with col4:
        st.metric(
            "Ongoing Actions/Month",
            f"{ongoing_monthly_actions:.0f}",
            help="Expected actions per month after implementation (15% of base)"
        )
    
    # Display forecast charts
    st.markdown("### 📈 12-Month Forecast")
    
    # Actions and Storage Chart
    fig1 = go.Figure()
    
    # Add Actions line
    fig1.add_trace(go.Scatter(
        x=forecast['Month'],
        y=forecast['Actions'],
        name='Actions',
        line=dict(color='#3498db')
    ))
    
    # Add Storage line
    fig1.add_trace(go.Scatter(
        x=forecast['Month'],
        y=forecast['Reclaimable Storage (GB)'],
        name='Reclaimable Storage (GB)',
        line=dict(color='#2ecc71'),
        yaxis='y2'
    ))
    
    # Add implementation end marker using shapes
    if implementation_months < 12:
        fig1.update_layout(
            shapes=[{
                'type': 'line',
                'yref': 'paper',
                'x0': forecast['Month'].iloc[implementation_months-1],
                'y0': 0,
                'x1': forecast['Month'].iloc[implementation_months-1],
                'y1': 1,
                'line': {
                    'color': 'gray',
                    'dash': 'dash',
                }
            }],
            annotations=[{
                'x': forecast['Month'].iloc[implementation_months-1],
                'y': 1,
                'yref': 'paper',
                'text': 'Implementation End',
                'showarrow': False,
                'yshift': 10
            }]
        )
    
    # Update layout
    fig1.update_layout(
        title='Forecasted Actions and Storage',
        xaxis_title='Month',
        yaxis_title='Number of Actions',
        yaxis2=dict(
            title='Reclaimable Storage (GB)',
            overlaying='y',
            side='right'
        ),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # Financial Impact Chart
    fig2 = go.Figure()
    
    # Add financial traces
    fig2.add_trace(go.Bar(
        x=forecast['Month'],
        y=forecast['Storage Savings (USD)'],
        name='Storage Savings',
        marker_color='#2ecc71'
    ))
    
    fig2.add_trace(go.Bar(
        x=forecast['Month'],
        y=forecast['Labor Savings (USD)'],
        name='Labor Savings',
        marker_color='#3498db'
    ))

    # Calculate and add energy cost savings (assuming $0.10 per kWh)
    energy_cost_per_kwh = 0.10  # You might want to add this to settings
    forecast['Energy Cost Savings (USD)'] = (forecast['Energy Savings (kWh)'] + forecast['Cooling Savings (kWh)']) * energy_cost_per_kwh
    
    fig2.add_trace(go.Bar(
        x=forecast['Month'],
        y=forecast['Energy Cost Savings (USD)'],
        name='Energy Savings',
        marker_color='#9b59b6'
    ))
    
    fig2.add_trace(go.Bar(
        x=forecast['Month'],
        y=-forecast['Automation Cost (USD)'],
        name='Automation Cost',
        marker_color='#e74c3c'
    ))
    
    # Update Net Savings to include energy savings
    forecast['Net Savings (USD)'] = (
        forecast['Storage Savings (USD)'] + 
        forecast['Labor Savings (USD)'] + 
        forecast['Energy Cost Savings (USD)'] - 
        forecast['Automation Cost (USD)']
    )
    
    fig2.add_trace(go.Scatter(
        x=forecast['Month'],
        y=forecast['Net Savings (USD)'],
        name='Net Savings',
        line=dict(color='#f1c40f', width=3)
    ))
    
    # Add implementation end marker using shapes
    if implementation_months < 12:
        fig2.update_layout(
            shapes=[{
                'type': 'line',
                'yref': 'paper',
                'x0': forecast['Month'].iloc[implementation_months-1],
                'y0': 0,
                'x1': forecast['Month'].iloc[implementation_months-1],
                'y1': 1,
                'line': {
                    'color': 'gray',
                    'dash': 'dash',
                }
            }],
            annotations=[{
                'x': forecast['Month'].iloc[implementation_months-1],
                'y': 1,
                'yref': 'paper',
                'text': 'Implementation End',
                'showarrow': False,
                'yshift': 10
            }]
        )
    
    # Update layout
    fig2.update_layout(
        title='Forecasted Financial Impact',
        xaxis_title='Month',
        yaxis_title='Amount (USD)',
        barmode='relative',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Add Sustainability Impact Chart
    fig3 = go.Figure()
    
    fig3.add_trace(go.Bar(
        x=forecast['Month'],
        y=forecast['Energy Savings (kWh)'],
        name='Energy Savings',
        marker_color='#3498db'
    ))
    
    fig3.add_trace(go.Bar(
        x=forecast['Month'],
        y=forecast['Cooling Savings (kWh)'],
        name='Cooling Savings',
        marker_color='#9b59b6'
    ))
    
    fig3.add_trace(go.Scatter(
        x=forecast['Month'],
        y=forecast['Carbon Savings (kg)'],
        name='Carbon Reduction',
        line=dict(color='#1abc9c', width=3),
        yaxis='y2'
    ))
    
    # Add implementation end marker
    if implementation_months < 12:
        fig3.update_layout(
            shapes=[{
                'type': 'line',
                'yref': 'paper',
                'x0': forecast['Month'].iloc[implementation_months-1],
                'y0': 0,
                'x1': forecast['Month'].iloc[implementation_months-1],
                'y1': 1,
                'line': {
                    'color': 'gray',
                    'dash': 'dash',
                }
            }],
            annotations=[{
                'x': forecast['Month'].iloc[implementation_months-1],
                'y': 1,
                'yref': 'paper',
                'text': 'Implementation End',
                'showarrow': False,
                'yshift': 10
            }]
        )
    
    fig3.update_layout(
        title='Sustainability Impact',
        xaxis_title='Month',
        yaxis_title='Energy (kWh)',
        yaxis2=dict(
            title='Carbon Reduction (kg)',
            overlaying='y',
            side='right'
        ),
        barmode='stack',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig3, use_container_width=True)
    
    # Display detailed forecast table
    st.markdown("### 📋 Detailed Forecast")
    
    # Format the forecast DataFrame for display
    display_forecast = forecast.copy()
    display_forecast['Month'] = display_forecast['Month'].dt.strftime('%Y-%m')
    
    # Round and format numeric columns
    numeric_cols = display_forecast.select_dtypes(include=['float64']).columns
    display_forecast[numeric_cols] = display_forecast[numeric_cols].round(2)
    
    # Display the table
    st.dataframe(
        display_forecast,
        use_container_width=True,
        hide_index=True
    ) 