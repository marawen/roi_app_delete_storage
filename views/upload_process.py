import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os
from views.helpers import calculate_financial_metrics

def render():
    # Custom title with consistent styling
    st.markdown('<div class="page-title">📤 Upload & Process</div>', unsafe_allow_html=True)
    
    # Introduction
    st.markdown("""
    <div class="welcome-banner">
        <h2>File Upload & Processing</h2>
        <p>Upload your Turbonomic Delete Storage recommendation Excel files to process them using your configured settings.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if settings are configured
    if 'settings' not in st.session_state:
        st.warning("⚠️ ROI parameters are not configured. Please set up your parameters in Settings first.")
        st.button("Go to Settings", key="go_to_settings", on_click=navigate_to, args=('settings',))
        return
    
    # Add CSS for styling
    st.markdown("""
    <style>
    .upload-instruction {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
    }
    
    .settings-summary {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
    }

    .settings-summary .summary-item {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid #e0e0e0;
    }

    .settings-summary .summary-item:last-child {
        border-bottom: none;
    }
    
    .file-info-box {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
    }
    
    .process-button {
        margin-top: 1rem;
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
    </style>
    """, unsafe_allow_html=True)
    
    # Upload instruction box
    st.markdown("""
    <div class="upload-instruction">
        <p><strong>Upload your Turbonomic Excel file</strong> with delete storage recommendations.</p>
        <p>Supported format: Turbonomic Delete Storage recommendation Excel export (.xlsx)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Settings summary
    settings = st.session_state.settings
    st.markdown('<div class="section-subheader">⚙️ Current Settings</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="settings-summary">
        <div class="summary-item"><span>Storage Cost:</span> <strong>${settings['cost_per_gb']:.3f}/GB/month</strong></div>
        <div class="summary-item"><span>Implementation:</span> <strong>{settings['implementation_months']} months</strong></div>
        <div class="summary-item"><span>Automation:</span> <strong>{settings['turbo_pct']}% / {100-settings['turbo_pct']}%</strong></div>
        <div class="summary-item"><span>Growth Rate:</span> <strong>{settings['forecast_growth_rate']*100:.1f}%</strong></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Adjust settings button (with callback function)
    st.button("Adjust Settings", key="adjust_settings", on_click=navigate_to, args=('settings',))
        
    # File uploader
    uploaded_file = st.file_uploader(
        "Drag and drop your file here",
        type=["xlsx"],
        key="recommendation_file"
    )
    
    # Show "please upload" message if no file
    if not uploaded_file:
        st.info("Please upload a file to continue.")
    else:
        # Display file information using native Streamlit components
        st.write("**Selected File:**", uploaded_file.name)
        st.write("**Size:**", f"{uploaded_file.size / 1024:.1f} KB")
        
        # Process File button
        process_clicked = st.button("▶️ Process File", 
                           type="primary", 
                           key="process_file_btn", 
                           use_container_width=True)
        
        # Process file when button is clicked
        if process_clicked:
            # Clear any previous results
            if 'processed_df' in st.session_state:
                del st.session_state['processed_df']
            if 'last_processed_results' in st.session_state:
                del st.session_state['last_processed_results']
            
            # Process the file
            process_file(uploaded_file)

# Callback function for navigation
def navigate_to(page):
    st.session_state['current_view'] = page

def process_file(uploaded_file):
    """Process the uploaded file and display results"""
    with st.spinner("Processing your data..."):
        try:
            # Read the Excel file
            df = pd.read_excel(uploaded_file)
            
            # Basic cleaning
            df = df.replace(r'^\s*$', pd.NA, regex=True)
            
            # Transform column names to lowercase with underscores
            df.columns = (
                df.columns.str.strip()
                         .str.lower()
                         .str.replace(' ', '_')
                         .str.replace('-', '_')
                         .str.replace('(', '_')
                         .str.replace(')', '_')
            )
            
            # Drop empty columns
            df = df.dropna(axis=1, how='all')
            
            # Ensure key columns exist or create mappings
            # Handle the file size column
            if 'file_size_gb_' in df.columns:
                df['file_size_(gb)'] = df['file_size_gb_']
            elif 'file_size__gb_' in df.columns:
                df['file_size_(gb)'] = df['file_size__gb_']
            
            # Find file size column
            file_size_col = [col for col in df.columns if 'size' in col and 'gb' in col]
            if file_size_col:
                df['file_size_(gb)'] = df[file_size_col[0]]
            
            # Clean last_modified_on column
            if 'last_modified_on' in df.columns:
                df['last_modified_on'] = df['last_modified_on'].astype(str).str.strip().str.replace('"', '', regex=False)

            # 📅 Enhanced Date Feature Engineering
            today = pd.Timestamp(datetime.today().date())

            # Date Created
            date_created_col = [col for col in df.columns if 'date' in col and 'created' in col]
            if date_created_col:
                df['date_created'] = df[date_created_col[0]]
            
            df['date_created_parsed'] = pd.to_datetime(df['date_created'], errors='coerce')
            df['age_days'] = (today - df['date_created_parsed']).dt.days
            df['created_year'] = df['date_created_parsed'].dt.year
            df['created_month'] = df['date_created_parsed'].dt.month
            df['created_day'] = df['date_created_parsed'].dt.day

            # Last Modified
            last_mod_col = [col for col in df.columns if 'last' in col and 'modified' in col]
            if last_mod_col:
                df['last_modified_on'] = df[last_mod_col[0]]
            
            try:
                df['last_modified_parsed'] = pd.to_datetime(df['last_modified_on'], errors='coerce')
            except:
                # Try different formats if the default doesn't work
                formats_to_try = ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y']
                for fmt in formats_to_try:
                    try:
                        df['last_modified_parsed'] = pd.to_datetime(df['last_modified_on'], format=fmt, errors='coerce')
                        if not df['last_modified_parsed'].isna().all():
                            break
                    except:
                        continue
            
            df['last_access_age_days'] = (today - df['last_modified_parsed']).dt.days
            df['last_modified_year'] = df['last_modified_parsed'].dt.year
            df['last_modified_month'] = df['last_modified_parsed'].dt.month
            df['last_modified_day'] = df['last_modified_parsed'].dt.day
            
            # Container cluster
            container_col = [col for col in df.columns if 'container' in col and 'cluster' in col]
            if container_col:
                df['container_cluster'] = df[container_col[0]]
                df['detach_days'] = df['container_cluster'].str.extract(r'(\d+)').astype(float)
            else:
                df['detach_days'] = 0
            
            # Name column
            name_col = [col for col in df.columns if col == 'name']
            if name_col:
                pass  # We already have a 'name' column
            elif 'file_name' in df.columns:
                df['name'] = df['file_name']
            else:
                # Use another column as name
                text_cols = df.select_dtypes(include=['object']).columns
                if len(text_cols) > 0:
                    df['name'] = df[text_cols[0]]

            # LOCATION EXTRACTION - IMPROVED APPROACH
            # 1. First, check if we already have the dedicated location columns from the CSV
            if 'inferred_location' in df.columns and not df['inferred_location'].isna().all():
                st.info("Using existing location information from the file.")
                # Already have inferred_location column
                if 'inferred_type' in df.columns:
                    # Rename to match our expected column name
                    df['location_type'] = df['inferred_type']
                elif 'location_type' not in df.columns:
                    # Create location_type from location confidence if available
                    if 'confidence_location' in df.columns:
                        # Higher confidence tends to be data centers
                        df['location_type'] = df['confidence_location'].apply(
                            lambda x: 'Data Center' if pd.notna(x) and float(x) > 7 else 'Business Domain'
                        )
                    else:
                        # Default to 'Unknown' if we can't determine
                        df['location_type'] = 'Unknown'
            
            # 2. If not present, try to infer from known location patterns
            elif any(col for col in df.columns if 'location' in col.lower()):
                # Look for any columns with 'location' in the name
                location_cols = [col for col in df.columns if 'location' in col.lower()]
                if location_cols:
                    st.info(f"Extracting location from column: {location_cols[0]}")
                    df['inferred_location'] = df[location_cols[0]]
                    
                    # Try to determine type from common patterns
                    # Data centers usually have 3-letter codes
                    data_centers = {'AUH', 'DXB', 'AJM'}
                    df['location_type'] = df['inferred_location'].apply(
                        lambda x: 'Data Center' if str(x).upper() in data_centers else 'Business Domain'
                    )
            
            # 3. Last resort - extract from filename or file path
            else:
                st.info("Extracting location information from filenames")
                df['location_info'] = df['name'].apply(extract_location_code)
                df['inferred_location'] = df['location_info'].apply(lambda x: x[0])
                df['location_type'] = df['location_info'].apply(lambda x: x[1])
                if 'location_info' in df.columns:
                    df = df.drop('location_info', axis=1)
                
                # If still no valid locations, try path extraction
                if df['inferred_location'].isna().all() or df['inferred_location'].eq('None').all():
                    file_path_col = next((col for col in df.columns if 'path' in col.lower()), None)
                    if file_path_col:
                        st.info(f"Extracting location from file paths in column: {file_path_col}")
                        # Extract locations from paths
                        df['location_info'] = df[file_path_col].apply(extract_location_from_path)
                        df['inferred_location'] = df['location_info'].apply(lambda x: x[0])
                        df['location_type'] = df['location_info'].apply(lambda x: x[1])
                        if 'location_info' in df.columns:
                            df = df.drop('location_info', axis=1)

            # Create a more descriptive location label
            df['location_label'] = df.apply(
                lambda row: f"{row['inferred_location']} ({row['location_type']})" 
                if 'location_type' in df.columns and pd.notna(row['inferred_location']) and row['inferred_location'] is not None
                else 'Unknown Location', 
                axis=1
            )

            # If we still don't have valid locations, create artificial ones for visualization
            if ('inferred_location' not in df.columns or 
                df['inferred_location'].isna().all() or 
                df['inferred_location'].eq('None').all()):
                
                st.warning("Could not detect location information. Creating artificial locations for visualization.")
                # Create artificial locations (50% Data Centers, 50% Business Domains)
                import numpy as np
                
                # Generate random locations
                locations = []
                for i in range(len(df)):
                    if i % 2 == 0:  # Even rows
                        loc_type = 'Data Center'
                        loc_code = f"DC{(i % 3) + 1}"
                    else:  # Odd rows
                        loc_type = 'Business Domain'
                        loc_code = f"BD{(i % 3) + 1}"
                    locations.append((loc_code, loc_type))
                
                df['inferred_location'] = [loc[0] for loc in locations]
                df['location_type'] = [loc[1] for loc in locations]
                df['location_label'] = df.apply(
                    lambda row: f"{row['inferred_location']} ({row['location_type']})", axis=1
                )

            # Confidence & ROI score
            risk_col = [col for col in df.columns if col == 'risk']
            if risk_col:
                df['confidence_score'] = df['risk'].apply(
                    lambda x: 1.0 if isinstance(x, str) and 'accepted and executed immediately' in x.lower() else 0.5
                )
            elif 'confidence_type' in df.columns:
                # Use existing confidence if available
                df['confidence_score'] = df['confidence_type'] / 10  # Normalize if it's on a different scale
            else:
                df['confidence_score'] = 0.5  # Default value
            
            # Calculate ROI score
            df['roi_score'] = (
                (df['file_size_(gb)'] * 2) +
                (df['age_days'].fillna(0) / 365) +
                (df['detach_days'].fillna(0) / 365) +
                (df['confidence_score'] * 5)
            )

            # 📊 Monthly Aggregation Summary
            df['roi_month'] = df['created_year'].astype(str) + '-' + df['created_month'].astype(str).str.zfill(2)

            # Add information about extraction method
            location_sources = []
            if 'inferred_location' in df.columns and not df['inferred_location'].isna().all():
                location_sources.append("columns")
            if 'location_info' in df.columns:
                location_sources.append("filename patterns")
            if not location_sources:
                location_sources.append("artificial generation")
                
            st.success(f"✅ Location information extracted from: {', '.join(location_sources)}")
            
            # Calculate all financial metrics using our centralized function
            try:
                results = calculate_financial_metrics(df, st.session_state.settings)
                
                if results is not None:
                    # Store processed data
                    processed_df = results['processed_df']
                    monthly_metrics = results['monthly_metrics']
                    totals = results['totals']
                    
                    # Save processed data to CSV and session state
                    os.makedirs('outputs', exist_ok=True)
                    processed_df.to_csv('outputs/processed_data.csv', index=False)
                    st.session_state['processed_df'] = processed_df
                    st.session_state['last_processed_results'] = results
                    
                    # Display success message with processed results
                    st.success("✅ Data processed successfully!")
                    
                    # Display results section
                    display_processing_results(processed_df, monthly_metrics, totals)
                else:
                    st.error("Error processing financial metrics. Please check your file format and try again.")
            except Exception as e:
                st.error(f"Error calculating financial metrics: {str(e)}")
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.markdown("Please ensure your file is in the correct Turbonomic recommendation export format.")

def display_processing_results(processed_df, monthly_metrics, totals):
    """Display the processing results in an organized, visually appealing way"""
    
    st.markdown("---")
    st.markdown('<div class="section-subheader">📊 Processing Results</div>', unsafe_allow_html=True)
    
    # Determine which keys to use for metrics
    storage_key = next((k for k in totals.keys() if 'storage_savings_gb' in k or 'storage_gb' in k), None)
    if not storage_key:
        # Fallback: use a key that might contain storage size
        storage_key = next((k for k in totals.keys() if 'storage' in k and not 'usd' in k.lower()), 'storage_amount')
    
    cost_key = next((k for k in totals.keys() if 'net_savings_usd' in k or 'net_savings' in k), None)
    if not cost_key:
        # Fallback: use a key that might contain cost
        cost_key = next((k for k in totals.keys() if 'savings' in k and 'usd' in k.lower()), 'net_savings')
    
    carbon_key = next((k for k in totals.keys() if 'carbon' in k), None)
    if not carbon_key:
        # Fallback 
        carbon_key = next((k for k in totals.keys() if 'co2' in k), 'carbon_savings')
    
    # Summary metrics with more consistent styling
    st.markdown(f"""
    <div class="metrics-row">
        <div class="metric-item">
            <div class="metric-label">Total Actions</div>
            <div class="metric-value">{len(processed_df):,}</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">Total Storage</div>
            <div class="metric-value">{totals.get(storage_key, 0):,.2f} GB</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">Cost Savings</div>
            <div class="metric-value">${totals.get(cost_key, 0):,.2f}</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">CO₂ Reduction</div>
            <div class="metric-value">{totals.get(carbon_key, 0):,.2f} kg</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Monthly breakdown in an expandable section
    with st.expander("📅 Monthly Breakdown", expanded=True):
        styled_monthly = style_monthly_summary(monthly_metrics)
        st.dataframe(styled_monthly, use_container_width=True, hide_index=True)
    
    # Enhanced Summary & Next Steps Section
    st.markdown("""
    <div class="summary-container">
        <div class="summary-header">
            <div class="summary-icon">🚀</div>
            <div class="summary-title">Next Steps</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Add buttons using Streamlit's native buttons in consistent layout with callbacks
    col1, col2 = st.columns(2)
    with col1:
        st.button("📊 View ROI Summary", 
                 type="primary", 
                 key="view_roi_summary", 
                 on_click=navigate_to, 
                 args=('roi_summary',),
                 use_container_width=True)
    with col2:
        st.button("📈 Explore Visualizations", 
                 key="explore_visualizations", 
                 on_click=navigate_to, 
                 args=('visualizations',),
                 use_container_width=True)
    
    # Generate the CSV data for download
    @st.cache_data
    def get_csv_data(df):
        return df.to_csv(index=False)
    
    csv_data = get_csv_data(processed_df)
    
    # Download option with no callback
    st.markdown("<div style='margin-top: 1rem;'>", unsafe_allow_html=True)
    st.download_button(
        "📥 Download Processed Data",
        data=csv_data,
        file_name=f"processed_recommendations_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        key="download_results",
        use_container_width=True
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Close the summary container
    st.markdown("</div>", unsafe_allow_html=True)

def extract_location_code(filename):
    """
    Extract location code from filename using specific patterns.
    Returns tuple of (location_code, location_type)
    """
    # Common location patterns
    data_centers = {'AUH', 'DXB', 'AJM'}
    
    if not filename or pd.isna(filename):
        return None, 'Unknown'
    
    filename = str(filename).upper()
    
    # Try to find location code in the filename
    # Pattern 1: Look for 3-letter codes that match our data centers
    for dc in data_centers:
        if dc in filename:
            return dc, 'Data Center'
    
    # Pattern 2: Look for other business domain codes (3-4 uppercase letters)
    import re
    match = re.search(r'[/_\\-]([A-Z]{3,4})[/_\\-]', f"_{filename}_")
    if match:
        code = match.group(1)
        if code in data_centers:
            return code, 'Data Center'
        return code, 'Business Domain'
    
    # Pattern 3: Look for DC or BD followed by numbers
    match = re.search(r'(DC|BD)[_\-]?(\d+)', filename)
    if match:
        prefix = match.group(1)
        number = match.group(2)
        if prefix == 'DC':
            return f"DC{number}", 'Data Center'
        return f"BD{number}", 'Business Domain'
    
    return None, 'Unknown'

def extract_location_from_path(path):
    """
    Extract location information from file paths.
    Returns tuple of (location_code, location_type)
    """
    if not path or pd.isna(path):
        return None, 'Unknown'
    
    path = str(path).upper()
    
    # Common patterns in paths
    # Pattern 1: /DCs/DC01/... or similar
    import re
    
    # Look for data center folder patterns
    dc_match = re.search(r'[/\\](DC\d+|DATA\s*CENTER\s*\d+)[/\\]', path)
    if dc_match:
        return dc_match.group(1).replace(' ', ''), 'Data Center'
    
    # Look for business domain folder patterns
    bd_match = re.search(r'[/\\](BD\d+|BUSINESS\s*DOMAIN\s*\d+|DEPT\s*\d+)[/\\]', path)
    if bd_match:
        return bd_match.group(1).replace(' ', ''), 'Business Domain'
    
    # Additional pattern: look for folder that might indicate location
    loc_match = re.search(r'[/\\](AUH|DXB|AJM)[/\\]', path)
    if loc_match:
        return loc_match.group(1), 'Data Center'
    
    return None, 'Unknown'

def infer_platform(x):
    if 'win' in x:
        return 'Windows'
    elif '.vmx' in x or '.vmdk' in x:
        return 'Linux'
    elif 'veeam' in x:
        return 'Veeam'
    return 'Unknown'

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