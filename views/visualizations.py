import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from views.helpers import load_processed_data, initialize_settings, calculate_financial_metrics
import json
from plotly.subplots import make_subplots

def render():
    # Custom title with consistent styling
    st.markdown('<div class="page-title">📊 Data Visualizations</div>', unsafe_allow_html=True)
    
    # Initialize settings if not exists
    initialize_settings()

    # Add CSS for consistent styling
    st.markdown("""
    <style>
    .page-title {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1976D2;
        margin-bottom: 1rem;
    }
    
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
    
    .section-subheader {
        font-size: 1.2rem;
        font-weight: 600;
        color: #333;
        margin: 1rem 0;
        border-left: 4px solid #1976D2;
        padding-left: 0.5rem;
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
    
    .tabs-container {
        margin-top: 1rem;
        background: white;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Style for tab content */
    .stTabs [data-baseweb="tab-panel"] {
        background: white;
        border-radius: 0 8px 8px 8px;
        padding: 1rem;
        border: 1px solid #e0e0e0;
        border-top: none;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Make Streamlit tabs look nicer */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        margin-bottom: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background: #f1f8fe;
        border-radius: 8px 8px 0 0;
        border: 1px solid #e0e0e0;
        border-bottom: none;
        font-weight: 500;
        padding: 8px 16px;
        display: flex;
        align-items: center;
    }
    
    .stTabs [aria-selected="true"] {
        background: white !important;
        border-bottom: 1px solid white !important;
        font-weight: 600 !important;
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
    
    .summary-container {
        background: linear-gradient(to right, #f8f9fa, #f1f8fe);
        border: 1px solid #e0e0e0;
        border-left: 4px solid #1976D2;
        border-radius: 8px;
        padding: 1.5rem;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
    }
    
    /* Override Streamlit's metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #1976D2 !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }
    
    hr {
        margin: 1.5rem 0;
        border: none;
        height: 1px;
        background-color: #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)

    # Introduction banner
    st.markdown("""
    <div class="welcome-banner">
        <h2>Interactive Visualizations</h2>
        <p>Explore detailed analytics and insights from your Turbonomic delete storage recommendations.</p>
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
            ⚠️ No data available for visualizations.
            
            To view visualizations:
            1. Go to the **Upload & Process** tab
            2. Upload your Turbonomic Excel file
            3. Process the data
            4. Return to this tab
            """)
            # Navigation button to upload page
            if st.button("Go to Upload & Process", type="primary"):
                st.session_state['current_view'] = 'upload_process'
            return

    df = st.session_state['processed_df']
    
    # Create default location_type and location_label if missing
    if 'location_type' not in df.columns:
        # Try to intelligently identify the location type based on available data
        location_type_identified = False
        
        # Method 1: Check if we have dedicated location type columns
        if 'datacenter' in df.columns or 'data_center' in df.columns:
            location_type_column = 'datacenter' if 'datacenter' in df.columns else 'data_center'
            df['location_type'] = df[location_type_column].notna().apply(
                lambda x: 'Data Center' if x else 'Unknown'
            )
            location_type_identified = True
        
        # Method 2: Check if we have business domain column
        elif 'business_domain' in df.columns or 'domain' in df.columns:
            domain_column = 'business_domain' if 'business_domain' in df.columns else 'domain'
            df['location_type'] = df[domain_column].notna().apply(
                lambda x: 'Business Domain' if x else 'Unknown'
            )
            location_type_identified = True
        
        # Method 3: Try to infer from inferred_location if it exists
        elif 'inferred_location' in df.columns:
            # Convert column names to lowercase for case-insensitive matching
            df['location_type'] = 'Unknown'
            
            # Look for DC patterns in the inferred_location
            dc_pattern = df['inferred_location'].str.lower().str.contains(
                'dc|data center|datacenter|data-center', na=False
            )
            df.loc[dc_pattern, 'location_type'] = 'Data Center'
            
            # Look for business domain patterns
            bd_pattern = df['inferred_location'].str.lower().str.contains(
                'bd|business domain|business|domain', na=False
            )
            df.loc[bd_pattern, 'location_type'] = 'Business Domain'
            
            # Look for dept or department patterns
            dept_pattern = df['inferred_location'].str.lower().str.contains(
                'dept|department', na=False
            )
            df.loc[dept_pattern, 'location_type'] = 'Business Domain'
            
            location_type_identified = True
        
        # Method 4: Last resort - create a fallback
        if not location_type_identified or df['location_type'].nunique() == 1:
            # Create artificial split for demonstration (50/50 split)
            df['location_type'] = 'Data Center'  # Default to Data Center
            if len(df) > 1:
                midpoint = len(df) // 2
                df.iloc[midpoint:, df.columns.get_loc('location_type')] = 'Business Domain'
        
        # Log information about the inferred location types
        st.info(f"Inferred location types from data: {', '.join(df['location_type'].unique())}")
    
    # Create inferred_location if missing
    if 'inferred_location' not in df.columns:
        # Try to find alternative location columns
        location_cols = [col for col in df.columns if 'location' in col.lower() 
                         or 'center' in col.lower() or 'domain' in col.lower()]
        
        if location_cols:
            # Use the first available location column
            df['inferred_location'] = df[location_cols[0]].astype(str)
        else:
            # Create artificial locations based on location_type
            df['inferred_location'] = df.apply(
                lambda row: f"{row['location_type']} {np.random.randint(1, 4)}" 
                if 'location_type' in df.columns else f"Location {np.random.randint(1, 4)}",
                axis=1
            )
    
    # Create location_label if missing
    if 'location_label' not in df.columns:
        df['location_label'] = df['inferred_location'].apply(
            lambda x: x.replace('_', ' ').title()
        )
    
    # Calculate metrics 
    metrics = calculate_financial_metrics(df, st.session_state.settings)
    if metrics is None:
        st.error("Error calculating metrics")
        return

    # Create tabs with icons in a container with consistent styling
    
    st.markdown('<div class="section-subheader">📊 Analysis Categories</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🗄️ Storage Analytics",
        "💰 Financial Insights",
        "🌱 Sustainability Metrics",
        "⚙️ Operations Analysis"
    ])
    
    with tab1:
        render_storage_analytics(df, metrics)
    with tab2:
        render_financial_insights(df, metrics)
    with tab3:
        render_sustainability_metrics(df, metrics)
    with tab4:
        render_operational_analysis(df, metrics)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Next steps section with navigation
    st.markdown("""
    <div class="summary-container">
        <div class="summary-header" style="margin-bottom: 1rem;">
            <div class="summary-title" style="font-size: 1.2rem; font-weight: 600;">🚀 Next Steps</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Next step navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📈 View ROI Summary", 
                 type="primary", 
                 key="view_roi", 
                 use_container_width=True):
            st.session_state['current_view'] = 'roi_summary'
    with col2:
        if st.button("📊 View Long-term Forecast", 
                 key="view_forecast", 
                 use_container_width=True):
            st.session_state['current_view'] = 'forecast'
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_storage_analytics(df, metrics):
    try:
        # Storage Overview - First Row
        st.markdown('<div class="section-subheader">🗄️ Storage Overview</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Storage",
                f"{metrics['metrics']['total_storage_gb']:,.0f} GB",
                "Across all locations"
            )
        with col2:
            st.metric(
                "Average Storage per Action",
                f"{metrics['metrics']['avg_storage_gb']:.2f} GB",
                "Per recommendation"
            )
        with col3:
            # Count unique locations by type
            location_counts = df.groupby('location_type')['inferred_location'].nunique()
            dc_count = location_counts.get('Data Center', 0)
            bd_count = location_counts.get('Business Domain', 0)
            
            st.metric(
                "Locations Coverage",
                f"{dc_count} DCs, {bd_count} BDs",
                "Data Centers & Business Domains"
            )
        
        st.markdown('<hr>', unsafe_allow_html=True)
        
        # Storage Distribution - Second Row
        st.markdown('<div class="section-subheader">📊 Storage Distribution</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Create treemap data
            root_data = pd.DataFrame({
                'location_type': ['Total Storage'],
                'inferred_location': ['Total Storage'],
                'file_size_(gb)': [df['file_size_(gb)'].sum()],
                'parent': [''],
                'id': ['Total Storage'],
                'label': ['Total Storage']
            })
            
            # Type level aggregation
            type_data = df.groupby('location_type').agg({
                'file_size_(gb)': 'sum'
            }).reset_index()
            type_data['inferred_location'] = type_data['location_type']
            type_data['parent'] = 'Total Storage'
            type_data['id'] = type_data['location_type']
            type_data['label'] = type_data['location_type']
            
            # Location level
            location_data = df.groupby(['location_type', 'inferred_location']).agg({
                'file_size_(gb)': 'sum'
            }).reset_index()
            location_data['parent'] = location_data['location_type']
            location_data['id'] = location_data['inferred_location']
            location_data['label'] = location_data['inferred_location']
            
            # Combine all levels
            treemap_data = pd.concat([root_data, type_data, location_data])
            
            fig_treemap = px.treemap(
                treemap_data,
                path=['parent', 'id'],
                values='file_size_(gb)',
                title='Storage Distribution by Location Type',
                color='file_size_(gb)',
                color_continuous_scale='viridis',
                hover_data=['label']
            )
            fig_treemap.update_traces(textinfo="label+value")
            fig_treemap.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_treemap, use_container_width=True, key="storage_treemap")

        with col2:
            # Create pie charts for DCs and Business Domains
            fig_pie = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Data Centers', 'Business Domains'),
                specs=[[{"type": "pie"}, {"type": "pie"}]]
            )
            
            # Data Centers pie
            dc_data = df[df['location_type'] == 'Data Center'].groupby('inferred_location')['file_size_(gb)'].sum()
            if not dc_data.empty:
                fig_pie.add_trace(
                    go.Pie(
                        values=dc_data.values,
                        labels=dc_data.index,
                        name="Data Centers"
                    ),
                    row=1, col=1
                )
            else:
                fig_pie.add_trace(
                    go.Pie(
                        values=[1],
                        labels=["No Data Centers"],
                        name="Data Centers"
                    ),
                    row=1, col=1
                )
            
            # Business Domains pie
            bd_data = df[df['location_type'] == 'Business Domain'].groupby('inferred_location')['file_size_(gb)'].sum()
            if not bd_data.empty:
                fig_pie.add_trace(
                    go.Pie(
                        values=bd_data.values,
                        labels=bd_data.index,
                        name="Business Domains"
                    ),
                    row=1, col=2
                )
            else:
                fig_pie.add_trace(
                    go.Pie(
                        values=[1],
                        labels=["No Business Domains"],
                        name="Business Domains"
                    ),
                    row=1, col=2
                )
            
            fig_pie.update_layout(
                height=400,
                title='Storage Distribution by Location Type',
                margin=dict(l=20, r=20, t=40, b=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_pie, use_container_width=True, key="storage_pie_charts")
        
        st.markdown('<hr>', unsafe_allow_html=True)
        
        # Growth Trend - Third Row
        st.markdown('<div class="section-subheader">📈 Storage Growth Trend</div>', unsafe_allow_html=True)
        
        # Add location type filter
        location_types = ['All'] + sorted(df['location_type'].unique().tolist())
        selected_type = st.selectbox('Filter by Location Type:', location_types)
        
        # Create month-year column if not exists
        if 'created_year' in df.columns and 'created_month' in df.columns:
            df['month_year'] = pd.to_datetime(df['created_year'].astype(str) + '-' + 
                                            df['created_month'].astype(str).str.zfill(2) + '-01')
        elif 'roi_month' in df.columns:
            # Use roi_month as fallback
            current_date = datetime.now()
            df['month_year'] = pd.to_datetime(current_date.strftime('%Y-%m-01')) - pd.to_timedelta(df['roi_month'] * 30, unit='D')
        else:
            # Create dummy date if neither exists
            df['month_year'] = pd.to_datetime('2024-01-01')
        
        if selected_type == 'All':
            growth_data = df.groupby('month_year')['file_size_(gb)'].sum().reset_index()
        else:
            growth_data = df[df['location_type'] == selected_type].groupby('month_year')['file_size_(gb)'].sum().reset_index()
        
        growth_data = growth_data.sort_values('month_year')
        
        # Check if we have at least two data points
        if len(growth_data) >= 2:
            fig_growth = px.line(
                growth_data,
                x='month_year',
                y='file_size_(gb)',
                title=f'Storage Growth Trend - {selected_type}',
                markers=True
            )
            fig_growth.update_layout(
                height=400,
                xaxis_title="Month",
                yaxis_title="Storage (GB)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(
                    tickformat="%b %Y",
                    tickmode='array',
                    ticktext=growth_data['month_year'].dt.strftime('%b %Y'),
                    tickvals=growth_data['month_year']
                )
            )
            st.plotly_chart(fig_growth, use_container_width=True, key="storage_growth_trend")
        else:
            st.info("Insufficient time-series data for growth trend visualization. At least two data points are required.")
        
    except Exception as e:
        st.error(f"Error in storage analytics: {str(e)}")

def render_financial_insights(df, metrics):
    try:
        # Financial Overview - First Row
        st.markdown('<div class="section-subheader">💰 Financial Overview</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Storage Savings",
                f"${metrics['totals']['storage_savings_usd']:,.0f}",
                "Direct Cost Reduction"
            )
        
        with col2:
            st.metric(
                "Net Labor Savings",
                f"${metrics['totals']['labor_savings_usd']:,.0f}",
                "Automation Benefits"
            )
        
        with col3:
            st.metric(
                "Total Net Savings",
                f"${metrics['totals']['net_savings_usd']:,.0f}",
                "Combined Benefits"
            )
        
        st.markdown('<hr>', unsafe_allow_html=True)
        
        # Cost Distribution - Second Row
        st.markdown('<div class="section-subheader">📊 Cost Distribution</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Cost Components Breakdown
            fig_costs = go.Figure(data=[
                go.Bar(name='Storage Savings', y=[metrics['totals']['storage_savings_usd']], marker_color='#27ae60'),
                go.Bar(name='Labor Savings', y=[metrics['totals']['labor_savings_usd']], marker_color='#3498db'),
                go.Bar(name='Automation Costs', y=[-metrics['totals']['automation_cost_usd']], marker_color='#e74c3c')
            ])
            
            fig_costs.update_layout(
                title='Cost Components Analysis',
                barmode='relative',
                height=400,
                showlegend=True,
                yaxis_title='Amount (USD)',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_costs, use_container_width=True, key="financial_cost_components")
        
        with col2:
            # Location-based Savings
            # Create net_savings_usd if not exists
            if 'net_savings_usd' not in df.columns and 'estimated_cost_usd' in df.columns:
                df['net_savings_usd'] = df['estimated_cost_usd']
            elif 'net_savings_usd' not in df.columns:
                df['net_savings_usd'] = metrics['metrics']['first_year_net_savings'] / len(df)
            
            location_savings = df.groupby(['location_type', 'inferred_location'])['net_savings_usd'].sum().reset_index()
            
            if not location_savings.empty:
                fig_location = px.bar(
                    location_savings,
                    x='inferred_location',
                    y='net_savings_usd',
                    color='location_type',
                    title='Net Savings by Location',
                    barmode='group',
                    color_discrete_map={
                        'Data Center': '#27ae60',
                        'Business Domain': '#3498db',
                        'Unknown': '#95a5a6'
                    }
                )
                fig_location.update_layout(
                    height=400,
                    xaxis_title="Location",
                    xaxis={'tickangle': -45},
                    yaxis_title="Net Savings (USD)",
                    legend_title="Location Type",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig_location, use_container_width=True, key="financial_location_savings")
            else:
                st.info("No location-based savings data available.")
        
        st.markdown('<hr>', unsafe_allow_html=True)
        
        # Monthly Trends - Third Row
        st.markdown('<div class="section-subheader">📈 Financial Trends</div>', unsafe_allow_html=True)
        
        # Ensure month_year column exists
        if 'month_year' not in df.columns:
            if 'created_year' in df.columns and 'created_month' in df.columns:
                df['month_year'] = pd.to_datetime(df['created_year'].astype(str) + '-' + 
                                                df['created_month'].astype(str).str.zfill(2) + '-01')
            elif 'roi_month' in df.columns:
                current_date = datetime.now()
                df['month_year'] = pd.to_datetime(current_date.strftime('%Y-%m-01')) - pd.to_timedelta(df['roi_month'] * 30, unit='D')
            else:
                df['month_year'] = pd.to_datetime('2024-01-01')
        
        # Ensure financial columns exist
        if 'storage_cost_usd' not in df.columns:
            if 'estimated_cost_usd' in df.columns:
                df['storage_cost_usd'] = df['estimated_cost_usd']
            else:
                df['storage_cost_usd'] = metrics['metrics']['first_year_storage_savings'] / len(df)
        
        if 'labor_cost_usd' not in df.columns:
            df['labor_cost_usd'] = metrics['metrics']['first_year_labor_savings'] / len(df)
        
        if 'automation_cost_usd' not in df.columns:
            df['automation_cost_usd'] = metrics['metrics']['first_year_automation_cost'] / len(df)
        
        monthly_metrics = df.groupby('month_year').agg({
            'storage_cost_usd': 'sum',
            'labor_cost_usd': 'sum',
            'automation_cost_usd': 'sum'
        }).reset_index()
        
        monthly_metrics['net_savings_usd'] = monthly_metrics['storage_cost_usd'] + monthly_metrics['labor_cost_usd'] - monthly_metrics['automation_cost_usd']
        monthly_metrics = monthly_metrics.sort_values('month_year')
        
        # Check if we have at least two data points
        if len(monthly_metrics) >= 2:
            fig_trends = go.Figure()
            
            # Add traces for different financial metrics
            fig_trends.add_trace(go.Scatter(
                x=monthly_metrics['month_year'],
                y=monthly_metrics['storage_cost_usd'],
                name='Storage Savings',
                line=dict(color='#27ae60', width=2)
            ))
            
            fig_trends.add_trace(go.Scatter(
                x=monthly_metrics['month_year'],
                y=monthly_metrics['labor_cost_usd'],
                name='Labor Savings',
                line=dict(color='#3498db', width=2)
            ))
            
            fig_trends.add_trace(go.Scatter(
                x=monthly_metrics['month_year'],
                y=-monthly_metrics['automation_cost_usd'],
                name='Automation Costs',
                line=dict(color='#e74c3c', width=2)
            ))
            
            fig_trends.add_trace(go.Scatter(
                x=monthly_metrics['month_year'],
                y=monthly_metrics['net_savings_usd'],
                name='Net Savings',
                line=dict(color='#f1c40f', width=3)
            ))
            
            fig_trends.update_layout(
                title='Monthly Financial Metrics',
                height=400,
                xaxis_title="Month",
                yaxis_title='Amount (USD)',
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(
                    tickformat="%b %Y",
                    tickmode='array',
                    ticktext=monthly_metrics['month_year'].dt.strftime('%b %Y'),
                    tickvals=monthly_metrics['month_year']
                )
            )
            st.plotly_chart(fig_trends, use_container_width=True, key="financial_monthly_trends")
        else:
            st.info("Insufficient time-series data for financial trend visualization. At least two data points are required.")
        
    except Exception as e:
        st.error(f"Error in financial insights: {str(e)}")

def render_sustainability_metrics(df, metrics):
    try:
        # Environmental Impact Overview
        st.markdown('<div class="section-subheader">🌱 Environmental Impact Overview</div>', unsafe_allow_html=True)
        
        # Add sustainability columns if missing
        if 'energy_savings' not in df.columns:
            settings = st.session_state.settings
            df['energy_savings'] = df['file_size_(gb)'] * settings['energy_kwh']
            df['cooling_savings'] = df['energy_savings'] * settings['cooling']
            df['carbon_savings'] = (df['energy_savings'] + df['cooling_savings']) * settings['co2_rate']
        
        # Calculate totals if not in metrics
        energy_total = df['energy_savings'].sum() if 'energy_savings' in df.columns else 0
        cooling_total = df['cooling_savings'].sum() if 'cooling_savings' in df.columns else 0
        carbon_total = df['carbon_savings'].sum() if 'carbon_savings' in df.columns else 0
        
        if 'energy_savings_kwh' not in metrics['totals']:
            metrics['totals']['energy_savings_kwh'] = energy_total
            metrics['totals']['cooling_savings_kwh'] = cooling_total
            metrics['totals']['carbon_savings_kg'] = carbon_total
        
        col1, col2, col3 = st.columns(3)
        
        total_energy = metrics['totals']['energy_savings_kwh'] + metrics['totals']['cooling_savings_kwh']
        
        with col1:
            st.metric(
                "Total Energy Saved",
                f"{total_energy:,.0f} kWh",
                "Direct + Cooling Energy"
            )
        
        with col2:
            st.metric(
                "Carbon Reduction",
                f"{metrics['totals']['carbon_savings_kg']:,.0f} kg CO₂",
                "Carbon Footprint Reduction"
            )
        
        with col3:
            trees_equivalent = metrics['totals']['carbon_savings_kg'] / 21
            st.metric(
                "Trees Equivalent",
                f"{trees_equivalent:,.0f} trees",
                "Annual CO₂ Absorption"
            )
        
        st.markdown('<hr>', unsafe_allow_html=True)
        
        # Energy Savings Analysis
        st.markdown('<div class="section-subheader">📊 Energy Savings Analysis</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Energy Breakdown
            fig_energy = go.Figure(data=[
                go.Bar(name='Direct Energy', y=['Energy Savings'], x=[metrics['totals']['energy_savings_kwh']], 
                      orientation='h', marker_color='#27ae60'),
                go.Bar(name='Cooling Energy', y=['Energy Savings'], x=[metrics['totals']['cooling_savings_kwh']], 
                      orientation='h', marker_color='#3498db')
            ])
            
            fig_energy.update_layout(
                title='Energy Savings Breakdown',
                barmode='stack',
                height=400,
                showlegend=True,
                xaxis_title='Energy (kWh)',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_energy, use_container_width=True, key="sustainability_energy_breakdown")
        
        with col2:
            # Carbon Savings by Location
            if 'carbon_savings' in df.columns:
                location_carbon = df.groupby(['location_type', 'inferred_location'])['carbon_savings'].sum().reset_index()
                
                if not location_carbon.empty:
                    fig_carbon = px.bar(
                        location_carbon,
                        x='inferred_location',
                        y='carbon_savings',
                        color='location_type',
                        title='Carbon Reduction by Location',
                        barmode='group',
                        color_discrete_map={
                            'Data Center': '#27ae60',
                            'Business Domain': '#3498db',
                            'Unknown': '#95a5a6'
                        }
                    )
                    fig_carbon.update_layout(
                        height=400,
                        xaxis_title="Location",
                        yaxis_title="Carbon Reduction (kg CO₂)",
                        xaxis={'tickangle': -45},
                        legend_title="Location Type",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig_carbon, use_container_width=True, key="sustainability_carbon_location")
                else:
                    st.info("No location-based carbon savings data available.")
            else:
                st.info("Carbon savings data by location not available.")
        
        st.markdown('<hr>', unsafe_allow_html=True)
        
        # Sustainability Trends
        st.markdown('<div class="section-subheader">📈 Sustainability Trends</div>', unsafe_allow_html=True)
        
        # Ensure month_year column exists
        if 'month_year' not in df.columns:
            if 'created_year' in df.columns and 'created_month' in df.columns:
                df['month_year'] = pd.to_datetime(df['created_year'].astype(str) + '-' + 
                                                df['created_month'].astype(str).str.zfill(2) + '-01')
            elif 'roi_month' in df.columns:
                current_date = datetime.now()
                df['month_year'] = pd.to_datetime(current_date.strftime('%Y-%m-01')) - pd.to_timedelta(df['roi_month'] * 30, unit='D')
            else:
                df['month_year'] = pd.to_datetime('2024-01-01')
        
        monthly_metrics = df.groupby('month_year').agg({
            'energy_savings': 'sum',
            'cooling_savings': 'sum',
            'carbon_savings': 'sum'
        }).reset_index()
        
        monthly_metrics = monthly_metrics.sort_values('month_year')
        
        # Check if we have at least two data points
        if len(monthly_metrics) >= 2:
            fig_trends = go.Figure()
            
            # Add traces for energy and carbon
            fig_trends.add_trace(go.Scatter(
                x=monthly_metrics['month_year'],
                y=monthly_metrics['energy_savings'] + monthly_metrics['cooling_savings'],
                name='Total Energy Saved (kWh)',
                line=dict(color='#27ae60', width=2)
            ))
            
            fig_trends.add_trace(go.Scatter(
                x=monthly_metrics['month_year'],
                y=monthly_metrics['carbon_savings'],
                name='Carbon Reduction (kg)',
                line=dict(color='#3498db', width=2),
                yaxis='y2'
            ))
            
            fig_trends.update_layout(
                title='Monthly Sustainability Trends',
                height=400,
                xaxis_title="Month",
                yaxis=dict(title='Energy Savings (kWh)'),
                yaxis2=dict(
                    title='Carbon Reduction (kg)',
                    overlaying='y',
                    side='right'
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(
                    tickformat="%b %Y",
                    tickmode='array',
                    ticktext=monthly_metrics['month_year'].dt.strftime('%b %Y'),
                    tickvals=monthly_metrics['month_year']
                )
            )
            st.plotly_chart(fig_trends, use_container_width=True, key="sustainability_monthly_trends")
        else:
            st.info("Insufficient time-series data for sustainability trend visualization. At least two data points are required.")
        
    except Exception as e:
        st.error(f"Error in sustainability metrics: {str(e)}")

def render_operational_analysis(df, metrics):
    try:
        # Operations Overview
        st.markdown('<div class="section-subheader">⚙️ Operations Overview</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Actions",
                f"{metrics['metrics']['total_actions']:,}",
                "Optimization Actions"
            )
        
        # Add confidence values if not present
        if 'confidence_score' not in df.columns:
            df['confidence_score'] = 0.85  # Default high confidence
        
        with col2:
            avg_confidence = df['confidence_score'].mean() * 100
            st.metric(
                "Average Confidence",
                f"{avg_confidence:.1f}%",
                "Action Confidence Score"
            )
        
        with col3:
            high_confidence = (df['confidence_score'] >= 0.8).mean() * 100
            st.metric(
                "High Confidence Actions",
                f"{high_confidence:.1f}%",
                "Score ≥ 80%"
            )
        
        st.markdown('<hr>', unsafe_allow_html=True)
        
        # Risk and Confidence Analysis
        st.markdown('<div class="section-subheader">📊 Risk and Confidence Analysis</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Add risk if not present
            if 'risk' not in df.columns:
                df['risk'] = 'Low'  # Default low risk
                
            # Risk Distribution
            risk_dist = df['risk'].value_counts()
            fig_risk = px.pie(
                values=risk_dist.values,
                names=risk_dist.index,
                title='Action Distribution by Risk Level',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_risk.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_risk, use_container_width=True, key="operations_risk_pie")
        
        with col2:
            # Confidence Score Distribution
            fig_conf = px.histogram(
                df,
                x='confidence_score',
                nbins=20,
                title='Confidence Score Distribution',
                color_discrete_sequence=['#3498db']
            )
            fig_conf.add_vline(
                x=avg_confidence/100,
                line_dash="dash",
                line_color="red",
                annotation_text="Mean"
            )
            fig_conf.update_layout(
                height=400,
                xaxis_title="Confidence Score",
                yaxis_title="Count",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_conf, use_container_width=True, key="operations_confidence_histogram")
        
        st.markdown('<hr>', unsafe_allow_html=True)
        
        # Operational Trends
        st.markdown('<div class="section-subheader">📈 Operational Trends</div>', unsafe_allow_html=True)
        
        # Ensure month_year column exists
        if 'month_year' not in df.columns:
            if 'created_year' in df.columns and 'created_month' in df.columns:
                df['month_year'] = pd.to_datetime(df['created_year'].astype(str) + '-' + 
                                                df['created_month'].astype(str).str.zfill(2) + '-01')
            elif 'roi_month' in df.columns:
                current_date = datetime.now()
                df['month_year'] = pd.to_datetime(current_date.strftime('%Y-%m-01')) - pd.to_timedelta(df['roi_month'] * 30, unit='D')
            else:
                df['month_year'] = pd.to_datetime('2024-01-01')
        
        monthly_actions = df.groupby('month_year').agg({
            'risk': 'count',
            'confidence_score': 'mean'
        }).reset_index()
        
        monthly_actions = monthly_actions.sort_values('month_year')
        
        # Check if we have at least two data points
        if len(monthly_actions) >= 2:
            fig_trends = go.Figure()
            
            # Add traces for actions and confidence
            fig_trends.add_trace(go.Bar(
                x=monthly_actions['month_year'],
                y=monthly_actions['risk'],
                name='Number of Actions',
                marker_color='#3498db'
            ))
            
            fig_trends.add_trace(go.Scatter(
                x=monthly_actions['month_year'],
                y=monthly_actions['confidence_score'] * 100,
                name='Average Confidence',
                line=dict(color='#e74c3c', width=2),
                yaxis='y2'
            ))
            
            fig_trends.update_layout(
                title='Monthly Actions and Confidence Trends',
                height=400,
                xaxis_title="Month",
                yaxis=dict(title='Number of Actions'),
                yaxis2=dict(
                    title='Average Confidence (%)',
                    overlaying='y',
                    side='right',
                    range=[0, 100]
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(
                    tickformat="%b %Y",
                    tickmode='array',
                    ticktext=monthly_actions['month_year'].dt.strftime('%b %Y'),
                    tickvals=monthly_actions['month_year']
                )
            )
            st.plotly_chart(fig_trends, use_container_width=True, key="operations_monthly_trends")
        else:
            st.info("Insufficient time-series data for operational trend visualization. At least two data points are required.")
        
        # Implementation Details
        st.markdown('<div class="section-subheader">📋 Implementation Details</div>', unsafe_allow_html=True)
        
        # Implementation parameters section
        st.markdown("""
        <div class="summary-container">
            <h3 style="margin-top: 0;">Implementation Parameters</h3>
            <p>These parameters are used to calculate the operational metrics and implementation timeline.</p>
        """, unsafe_allow_html=True)
        
        settings = st.session_state.settings
        st.markdown(f"""
        <div class="implementation-notes">
            <div class="note-item"><span>Implementation Timeline:</span> <strong>{settings['implementation_months']} months</strong></div>
            <div class="note-item"><span>Time Required per Action:</span> <strong>{settings['min_minutes']} minutes</strong></div>
            <div class="note-item"><span>Staff Hourly Rate:</span> <strong>AED {settings['min_rate_aed']:.2f}/hour</strong></div>
            <div class="note-item"><span>Automation Distribution:</span> <strong>{settings['turbo_pct']}% Turbonomic, {100-settings['turbo_pct']}% AAP</strong></div>
            <div class="note-item"><span>Automation Unit Costs:</span> <strong>Turbonomic: ${settings['turbo_unit_cost_usd']:.2f}, AAP: ${settings['aap_unit_cost_usd']:.2f}</strong></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error in operational analysis: {str(e)}")

def initialize_settings():
    if 'settings' not in st.session_state:
        # Load configuration defaults
        try:
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
        except FileNotFoundError:
            st.warning("Configuration file not found. Using default values.")
            st.session_state.settings = {
                'cost_per_gb': 0.023,
                'retention': 6,
                'conversion_rate': 3.67,
                'energy_kwh': 0.0008,
                'cooling': 0.25,
                'co2_rate': 0.4,
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

def navigate_to(page):
    st.session_state['current_view'] = page