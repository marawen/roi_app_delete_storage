import pandas as pd
import os
import streamlit as st
import numpy as np
from datetime import datetime
import json

@st.cache_data(ttl=7200)
def load_processed_data():
    """Load and process the data from the processed CSV file."""
    try:
        if not os.path.exists('outputs/processed_data.csv'):
            return None
        
        df = pd.read_csv('outputs/processed_data.csv')
        
        # Ensure location type information is present
        if 'location_type' not in df.columns:
            data_centers = {'AUH', 'DXB', 'AJM'}
            df['location_type'] = df['inferred_location'].apply(
                lambda x: 'Data Center' if x in data_centers else 'Business Domain' if pd.notna(x) else 'Unknown'
            )
        
        return df
    except Exception as e:
        st.error(f"Error loading processed data: {str(e)}")
        return None

@st.cache_data(ttl=7200)
def calculate_financial_metrics(df, settings):
    """Centralized function for all financial calculations with caching."""
    try:
        # Base metrics using vectorized operations
        metrics = {
            'total_storage_gb': df['file_size_(gb)'].sum(),
            'avg_storage_gb': df['file_size_(gb)'].mean(),
            'total_actions': len(df)
        }
        
        # Storage costs (vectorized)
        df['storage_cost_usd'] = df['file_size_(gb)'] * settings['cost_per_gb'] * settings['retention']
        df['storage_cost_aed'] = df['storage_cost_usd'] * settings['conversion_rate']
        
        # Energy and sustainability (vectorized)
        total_energy_factor = settings['energy_kwh'] * (1 + settings['cooling'])
        df['energy_savings'] = df['file_size_(gb)'] * settings['energy_kwh'] * settings['retention']
        df['cooling_savings'] = df['file_size_(gb)'] * settings['energy_kwh'] * settings['cooling'] * settings['retention']
        df['carbon_savings'] = df['file_size_(gb)'] * total_energy_factor * settings['co2_rate'] * settings['retention']
        
        # Labor and automation (vectorized)
        labor_hours_min = settings['min_minutes'] / 60
        labor_hours_max = settings['max_minutes'] / 60
        df['labor_hours'] = labor_hours_min
        df['labor_cost_usd'] = (labor_hours_min * settings['min_rate_aed']) / settings['conversion_rate']
        
        # Automation costs (vectorized)
        turbo_cost = settings['turbo_unit_cost_usd'] * (settings['turbo_pct'] / 100)
        aap_cost = settings['aap_unit_cost_usd'] * ((100 - settings['turbo_pct']) / 100)
        df['automation_cost_usd'] = turbo_cost + aap_cost
        
        # Net savings (vectorized)
        df['net_savings_usd'] = df['storage_cost_usd'] + df['labor_cost_usd'] - df['automation_cost_usd']
        
        # Monthly aggregation (single groupby operation)
        monthly_metrics = df.groupby('roi_month').agg({
            'storage_cost_usd': 'sum',
            'storage_cost_aed': 'sum',
            'energy_savings': 'sum',
            'cooling_savings': 'sum',
            'carbon_savings': 'sum',
            'labor_cost_usd': 'sum',
            'automation_cost_usd': 'sum',
            'net_savings_usd': 'sum',
            'file_size_(gb)': 'sum'
        }).reset_index()
        
        # Calculate totals
        totals = {
            'storage_savings_usd': df['storage_cost_usd'].sum(),
            'storage_savings_aed': df['storage_cost_aed'].sum(),
            'energy_savings_kwh': df['energy_savings'].sum(),
            'cooling_savings_kwh': df['cooling_savings'].sum(),
            'carbon_savings_kg': df['carbon_savings'].sum(),
            'labor_savings_usd': df['labor_cost_usd'].sum(),
            'automation_cost_usd': df['automation_cost_usd'].sum(),
            'net_savings_usd': df['net_savings_usd'].sum()
        }
        
        return {
            'metrics': metrics,
            'monthly_metrics': monthly_metrics,
            'totals': totals,
            'processed_df': df
        }
        
    except Exception as e:
        st.error(f"Error in financial calculations: {str(e)}")
        return None

def initialize_settings():
    """Initialize settings from config file."""
    if 'settings' not in st.session_state:
        try:
            with open("config/config.json", "r") as f:
                config = json.load(f)
                
            st.session_state.settings = {
                'cost_per_gb': config['cost_per_gb_per_month_usd'],
                'retention': config['retention_months'],
                'conversion_rate': config['currency_conversion_rate'],
                'energy_kwh': config['energy_per_gb_kwh'],
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
        except Exception as e:
            st.error(f"Error loading settings: {str(e)}")
            st.session_state.settings = {}
