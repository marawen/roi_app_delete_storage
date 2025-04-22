import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import os
from views.helpers import load_processed_data, initialize_settings, calculate_financial_metrics
import json
from plotly.subplots import make_subplots

# Cache data processing functions with longer TTL
@st.cache_data(ttl=7200)
def process_location_data(df):
    # Group by both location and type
    location_data = df.groupby(['location_type', 'inferred_location']).agg({
        'file_size_(gb)': 'sum'
    }).reset_index()
    
    # Create hierarchical structure
    location_data['parent'] = location_data['location_type']
    location_data['id'] = location_data['inferred_location']
    location_data['label'] = df['location_label'].iloc[0]  # Get the formatted label
    
    # Create root and type-level entries
    root_data = pd.DataFrame({
        'location_type': ['Total Storage'],
        'inferred_location': ['Total Storage'],
        'file_size_(gb)': [location_data['file_size_(gb)'].sum()],
        'parent': [''],
        'id': ['Total Storage'],
        'label': ['Total Storage']
    })
    
    type_data = location_data.groupby('location_type').agg({
        'file_size_(gb)': 'sum'
    }).reset_index()
    type_data['inferred_location'] = type_data['location_type']
    type_data['parent'] = 'Total Storage'
    type_data['id'] = type_data['location_type']
    type_data['label'] = type_data['location_type']
    
    return pd.concat([root_data, type_data, location_data])

@st.cache_data(ttl=7200)
def process_storage_metrics(df):
    total_storage = df['file_size_(gb)'].sum()
    avg_storage = df['file_size_(gb)'].mean()
    storage_by_location = df.groupby('inferred_location')['file_size_(gb)'].sum()
    return total_storage, avg_storage, storage_by_location

@st.cache_data(ttl=7200)
def process_growth_data(df):
    return df.groupby('roi_month').agg({
        'file_size_(gb)': 'sum'
    }).reset_index()

@st.cache_data(ttl=7200)
def process_financial_metrics(df, min_rate_aed, conversion_rate):
    # Monthly savings
    monthly_savings = df.groupby('roi_month').agg({
        'estimated_cost_usd': 'sum',
        'estimated_cost_aed': 'sum'
    }).reset_index()
    
    # Total savings components
    total_storage = df['estimated_cost_usd'].sum()
    total_labor = (df['labor_hours_saved_min'].sum() * min_rate_aed) / conversion_rate
    total_automation = df['automation_cost_usd'].sum()
    
    return monthly_savings, total_storage, total_labor, total_automation

@st.cache_data(ttl=7200)
def process_cost_efficiency(df):
    cost_efficiency = df.groupby('inferred_location').agg({
        'estimated_cost_usd': 'sum',
        'file_size_(gb)': 'sum'
    }).reset_index()
    cost_efficiency['cost_per_gb'] = cost_efficiency['estimated_cost_usd'] / cost_efficiency['file_size_(gb)']
    return cost_efficiency

@st.cache_data(ttl=7200)
def process_pareto(df):
    df_sorted = df.sort_values('estimated_cost_usd', ascending=False)
    df_sorted['cumulative_savings'] = df_sorted['estimated_cost_usd'].cumsum()
    df_sorted['percentage_complete'] = (np.arange(1, len(df_sorted) + 1, dtype=np.float64) / len(df_sorted)) * 100
    return df_sorted

@st.cache_data(ttl=7200)
def process_sustainability_metrics(df):
    # Energy metrics
    total_energy = df['energy_kwh_saved'].sum()
    total_cooling = df['cooling_kwh_saved'].sum()
    total_carbon = df['carbon_savings_kg'].sum()
    
    # Monthly trends
    monthly_metrics = df.groupby('roi_month').agg({
        'energy_kwh_saved': 'sum',
        'cooling_kwh_saved': 'sum',
        'carbon_savings_kg': 'sum'
    }).reset_index()
    
    # Location-based metrics
    location_metrics = df.groupby('inferred_location').agg({
        'carbon_savings_kg': 'sum'
    }).reset_index()
    
    return (total_energy, total_cooling, total_carbon, 
            monthly_metrics, location_metrics)

@st.cache_data(ttl=7200)
def process_operational_metrics(df):
    # Risk distribution
    risk_dist = df['risk'].value_counts().reset_index()
    risk_dist.columns = ['risk', 'count']
    
    # Confidence score statistics
    confidence_mean = df['confidence_score'].mean()
    high_confidence = (df['confidence_score'] >= 0.8).mean() * 100
    
    # Monthly action counts
    monthly_actions = df.groupby('roi_month').agg({
        'risk': 'count',
        'confidence_score': 'mean'
    }).reset_index()
    monthly_actions.columns = ['month', 'actions', 'avg_confidence']
    
    return risk_dist, confidence_mean, high_confidence, monthly_actions

def process_monthly_data(df):
    """Helper function to create proper month-year grouping for trends."""
    df['month_year'] = pd.to_datetime(df['created_year'].astype(str) + '-' + 
                                    df['created_month'].astype(str).str.zfill(2) + '-01')
    return df

def render_storage_analytics(df, metrics):
    try:
        # Storage Overview - First Row
        st.markdown("### Storage Overview")
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
            dc_count = len(df[df['location_type'] == 'Data Center']['inferred_location'].unique())
            bd_count = len(df[df['location_type'] == 'Business Domain']['inferred_location'].unique())
            st.metric(
                "Locations Coverage",
                f"{dc_count} DCs, {bd_count} BDs",
                "Data Centers & Business Domains"
            )
        
        st.markdown("---")
        
        # Storage Distribution - Second Row
        st.markdown("### Storage Distribution")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            location_data = process_location_data(df)
            fig_treemap = px.treemap(
                location_data,
                path=['parent', 'id'],
                values='file_size_(gb)',
                title='Storage Distribution by Location Type',
                color='file_size_(gb)',
                color_continuous_scale='Viridis',
                hover_data=['label']
            )
            fig_treemap.update_traces(
                textinfo="label+value",
                hovertemplate="<br>".join([
                    "Location: %{customdata[0]}",
                    "Storage: %{value:.2f} GB"
                ])
            )
            fig_treemap.update_layout(height=400)
            st.plotly_chart(fig_treemap, use_container_width=True)

        with col2:
            # Separate pie charts for DCs and Business Domains
            fig_pie = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Data Centers', 'Business Domains'),
                specs=[[{"type": "pie"}, {"type": "pie"}]]
            )
            
            # Data Centers pie
            dc_data = df[df['location_type'] == 'Data Center'].groupby('location_label')['file_size_(gb)'].sum()
            fig_pie.add_trace(
                go.Pie(
                    values=dc_data.values,
                    labels=dc_data.index,
                    name="Data Centers"
                ),
                row=1, col=1
            )
            
            # Business Domains pie
            bd_data = df[df['location_type'] == 'Business Domain'].groupby('location_label')['file_size_(gb)'].sum()
            fig_pie.add_trace(
                go.Pie(
                    values=bd_data.values,
                    labels=bd_data.index,
                    name="Business Domains"
                ),
                row=1, col=2
            )
            
            fig_pie.update_layout(
                height=400,
                title='Storage Distribution by Location Type'
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        st.markdown("---")
        
        # Growth Trend - Third Row
        st.markdown("### Storage Growth Trend")
        
        # Add location type filter
        location_types = ['All'] + sorted(df['location_type'].unique().tolist())
        selected_type = st.selectbox('Filter by Location Type:', location_types)
        
        df_monthly = process_monthly_data(df)
        
        if selected_type == 'All':
            growth_data = df_monthly.groupby('month_year')['file_size_(gb)'].sum().reset_index()
        else:
            growth_data = df_monthly[df_monthly['location_type'] == selected_type].groupby('month_year')['file_size_(gb)'].sum().reset_index()
        
        growth_data = growth_data.sort_values('month_year')
        
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
            xaxis=dict(
                tickformat="%b %Y",
                tickmode='array',
                ticktext=growth_data['month_year'].dt.strftime('%b %Y'),
                tickvals=growth_data['month_year']
            )
        )
        st.plotly_chart(fig_growth, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error in storage analytics: {str(e)}")

def render_sustainability_metrics(df, metrics):
    try:
        # Environmental Impact Overview - First Row
        st.markdown("### Environmental Impact Overview")
        col1, col2, col3 = st.columns(3)
        
        total_energy = metrics['totals']['energy_savings_kwh'] + metrics['totals']['cooling_savings_kwh']
        
        with col1:
            st.metric(
                "Total Energy Saved",
                f"{total_energy:,.0f} kWh",
                "Direct + Cooling Energy",
                help="Total energy savings including both direct and cooling energy"
            )
        
        with col2:
            st.metric(
                "Carbon Reduction",
                f"{metrics['totals']['carbon_savings_kg']:,.0f} kg CO₂",
                "Carbon Footprint Reduction",
                help="Total reduction in carbon emissions"
            )
        
        with col3:
            trees_equivalent = metrics['totals']['carbon_savings_kg'] / 21
            st.metric(
                "Trees Equivalent",
                f"{trees_equivalent:,.0f} trees",
                "Annual CO₂ Absorption",
                help="Equivalent number of trees needed to absorb the same amount of CO₂ in one year"
            )
        
        st.markdown("---")
        
        # Energy Savings Analysis - Second Row
        st.markdown("### Energy Savings Analysis")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Energy Breakdown
            fig_energy = go.Figure()
            fig_energy.add_trace(go.Bar(
                name='Direct Energy',
                y=['Energy Savings'],
                x=[metrics['totals']['energy_savings_kwh']],
                orientation='h',
                marker_color='#2ecc71'
            ))
            fig_energy.add_trace(go.Bar(
                name='Cooling Energy',
                y=['Energy Savings'],
                x=[metrics['totals']['cooling_savings_kwh']],
                orientation='h',
                marker_color='#3498db'
            ))
            fig_energy.update_layout(
                title='Energy Savings Breakdown',
                barmode='stack',
                height=400,
                showlegend=True,
                xaxis_title='Energy (kWh)'
            )
            st.plotly_chart(fig_energy, use_container_width=True)
        
        with col2:
            # Carbon Savings by Location
            location_carbon = df.groupby(['location_type', 'location_label'])['carbon_savings'].sum().reset_index()
            fig_carbon = px.bar(
                location_carbon,
                x='location_label',
                y='carbon_savings',
                color='location_type',
                title='Carbon Reduction by Location',
                barmode='group',
                color_discrete_map={
                    'Data Center': '#2ecc71',
                    'Business Domain': '#3498db',
                    'Unknown': '#95a5a6'
                }
            )
            fig_carbon.update_layout(
                height=400,
                xaxis_title="Location",
                xaxis={'tickangle': -45},
                legend_title="Location Type"
            )
            st.plotly_chart(fig_carbon, use_container_width=True)
        
        st.markdown("---")
        
        # Monthly Trends - Third Row
        st.markdown("### Sustainability Trends")
        df_monthly = process_monthly_data(df)
        monthly_metrics = df_monthly.groupby('month_year').agg({
            'energy_savings': 'sum',
            'cooling_savings': 'sum',
            'carbon_savings': 'sum'
        }).reset_index()
        monthly_metrics = monthly_metrics.sort_values('month_year')
        
        fig_trends = go.Figure()
        
        # Add traces for energy and carbon
        fig_trends.add_trace(go.Scatter(
            x=monthly_metrics['month_year'],
            y=monthly_metrics['energy_savings'] + monthly_metrics['cooling_savings'],
            name='Total Energy Saved (kWh)',
            line=dict(color='#2ecc71', width=2)
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
            xaxis=dict(
                tickformat="%b %Y",
                tickmode='array',
                ticktext=monthly_metrics['month_year'].dt.strftime('%b %Y'),
                tickvals=monthly_metrics['month_year']
            )
        )
        st.plotly_chart(fig_trends, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error in sustainability metrics: {str(e)}")

def render_operational_analysis(df, metrics):
    try:
        # Operational Overview - First Row
        st.markdown("### Operations Overview")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Actions",
                f"{metrics['metrics']['total_actions']:,}",
                "Optimization Actions"
            )
        
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
        
        st.markdown("---")
        
        # Risk and Confidence Analysis - Second Row
        st.markdown("### Risk and Confidence Analysis")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Risk Distribution
            risk_dist = df['risk'].value_counts()
            fig_risk = px.pie(
                values=risk_dist.values,
                names=risk_dist.index,
                title='Action Distribution by Risk Level',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_risk.update_layout(height=400)
            st.plotly_chart(fig_risk, use_container_width=True)
        
        with col2:
            # Confidence Score Distribution
            fig_conf = px.histogram(
                df,
                x='confidence_score',
                nbins=20,
                title='Confidence Score Distribution'
            )
            fig_conf.add_vline(
                x=avg_confidence/100,
                line_dash="dash",
                line_color="red",
                annotation_text="Mean"
            )
            fig_conf.update_layout(height=400)
            st.plotly_chart(fig_conf, use_container_width=True)
        
        st.markdown("---")
        
        # Monthly Trends - Third Row
        st.markdown("### Operational Trends")
        df_monthly = process_monthly_data(df)
        monthly_actions = df_monthly.groupby('month_year').agg({
            'risk': 'count',
            'confidence_score': 'mean'
        }).reset_index()
        monthly_actions = monthly_actions.sort_values('month_year')
        
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
            xaxis=dict(
                tickformat="%b %Y",
                tickmode='array',
                ticktext=monthly_actions['month_year'].dt.strftime('%b %Y'),
                tickvals=monthly_actions['month_year']
            )
        )
        st.plotly_chart(fig_trends, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error in operational analysis: {str(e)}")

def render_financial_insights(df, metrics):
    try:
        # Financial Overview - First Row
        st.markdown("### Financial Overview")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Storage Savings",
                f"${metrics['totals']['storage_savings_usd']:,.0f}",
                "Direct Cost Reduction",
                help="Total storage cost savings based on reclaimed storage"
            )
        
        with col2:
            st.metric(
                "Net Labor Savings",
                f"${metrics['totals']['labor_savings_usd']:,.0f}",
                "Automation Benefits",
                help="Labor cost savings from automation minus automation costs"
            )
        
        with col3:
            st.metric(
                "Total Net Savings",
                f"${metrics['totals']['net_savings_usd']:,.0f}",
                "Combined Benefits",
                help="Total savings including storage, labor, and automation costs"
            )
        
        st.markdown("---")
        
        # Cost Distribution - Second Row
        st.markdown("### Cost Distribution")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Cost Components Breakdown
            fig_costs = go.Figure()
            
            # Add positive values (savings)
            fig_costs.add_trace(go.Bar(
                name='Storage Savings',
                x=['Cost Components'],
                y=[metrics['totals']['storage_savings_usd']],
                marker_color='#2ecc71'
            ))
            
            fig_costs.add_trace(go.Bar(
                name='Labor Savings',
                x=['Cost Components'],
                y=[metrics['totals']['labor_savings_usd']],
                marker_color='#3498db'
            ))
            
            # Add negative values (costs)
            fig_costs.add_trace(go.Bar(
                name='Automation Costs',
                x=['Cost Components'],
                y=[-metrics['totals']['automation_cost_usd']],
                marker_color='#e74c3c'
            ))
            
            fig_costs.update_layout(
                title='Cost Components Analysis',
                barmode='relative',
                height=400,
                showlegend=True,
                yaxis_title='Amount (USD)'
            )
            st.plotly_chart(fig_costs, use_container_width=True)
        
        with col2:
            # Location-based Savings
            location_savings = df.groupby(['location_type', 'location_label'])['net_savings_usd'].sum().reset_index()
            fig_location = px.bar(
                location_savings,
                x='location_label',
                y='net_savings_usd',
                color='location_type',
                title='Net Savings by Location',
                barmode='group',
                color_discrete_map={
                    'Data Center': '#2ecc71',
                    'Business Domain': '#3498db',
                    'Unknown': '#95a5a6'
                }
            )
            fig_location.update_layout(
                height=400,
                xaxis_title="Location",
                xaxis={'tickangle': -45},
                legend_title="Location Type"
            )
            st.plotly_chart(fig_location, use_container_width=True)
        
        st.markdown("---")
        
        # Monthly Trends - Third Row
        st.markdown("### Financial Trends")
        df_monthly = process_monthly_data(df)
        monthly_metrics = df_monthly.groupby('month_year').agg({
            'storage_cost_usd': 'sum',
            'labor_cost_usd': 'sum',
            'automation_cost_usd': 'sum',
            'net_savings_usd': 'sum'
        }).reset_index()
        monthly_metrics = monthly_metrics.sort_values('month_year')
        
        fig_trends = go.Figure()
        
        # Add traces for different financial metrics
        fig_trends.add_trace(go.Scatter(
            x=monthly_metrics['month_year'],
            y=monthly_metrics['storage_cost_usd'],
            name='Storage Savings',
            line=dict(color='#2ecc71', width=2)
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
            xaxis=dict(
                tickformat="%b %Y",
                tickmode='array',
                ticktext=monthly_metrics['month_year'].dt.strftime('%b %Y'),
                tickvals=monthly_metrics['month_year']
            )
        )
        st.plotly_chart(fig_trends, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error in financial insights: {str(e)}")

def render():
    st.title("Analytics Dashboard")
    
    # Initialize settings
    initialize_settings()
    
    # Load data
    if 'processed_df' not in st.session_state:
        st.warning("⚠️ Please upload and process data first")
        return
    
    # Calculate all metrics once
    metrics = calculate_financial_metrics(st.session_state['processed_df'], st.session_state.settings)
    if metrics is None:
        st.error("Error calculating metrics")
        return
    
    # Create tabs without emojis
    tab1, tab2, tab3, tab4 = st.tabs([
        "Storage Analytics",
        "Financial Insights",
        "Sustainability Metrics",
        "Operations Analysis"
    ])
    
    with tab1:
        render_storage_analytics(st.session_state['processed_df'], metrics)
    with tab2:
        render_financial_insights(st.session_state['processed_df'], metrics)
    with tab3:
        render_sustainability_metrics(st.session_state['processed_df'], metrics)
    with tab4:
        render_operational_analysis(st.session_state['processed_df'], metrics)
