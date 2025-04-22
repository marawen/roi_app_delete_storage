import streamlit as st
from views.helpers import load_processed_data
import pandas as pd

def render():
    st.title("📋 ROI Explorer")

    df = load_processed_data()
    if df is None:
        return

    # Create two columns for the main layout
    main_col1, main_col2 = st.columns([1, 3])

    with main_col1:
        st.markdown("### 🔍 Filters")
        
        # Location Type filter with custom styling
        st.markdown("#### Location Type")
        location_type_options = ['All'] + sorted(df['location_type'].unique().tolist())
        selected_type = st.selectbox(
            "Select location type",
            options=location_type_options,
            label_visibility="collapsed"
        )

        # Location filter with custom styling
        st.markdown("#### Location")
        location_options = df["inferred_location"].dropna().unique().tolist()
        selected_locations = st.multiselect(
            "Select locations",
            options=location_options,
            default=location_options,
            label_visibility="collapsed"
        )

        # Date Range filter
        if "created_date" in df.columns and not df["created_date"].isnull().all():
            st.markdown("#### Date Range")
            df["created_date"] = pd.to_datetime(df["created_date"], errors="coerce")
            min_date = df["created_date"].min()
            max_date = df["created_date"].max()
            date_range = st.date_input(
                "Select date range",
                [min_date, max_date],
                label_visibility="collapsed"
            )
            if len(date_range) == 2:
                start_date = pd.to_datetime(date_range[0])
                end_date = pd.to_datetime(date_range[1])
                df = df[(df["created_date"] >= start_date) & (df["created_date"] <= end_date)]

        # Sorting options
        st.markdown("#### Sort Options")
        sort_col = st.selectbox(
            "Sort by",
            options=[col for col in df.columns if col not in ['location_type', 'inferred_location']],
            label_visibility="collapsed"
        )
        sort_order = st.radio(
            "Sort order",
            options=["Descending", "Ascending"],
            horizontal=True,
            label_visibility="collapsed"
        )

    with main_col2:
        # Apply filters
        filtered_df = df.copy()
        if selected_type != 'All':
            filtered_df = filtered_df[filtered_df['location_type'] == selected_type]
        filtered_df = filtered_df[filtered_df["inferred_location"].isin(selected_locations)]

        # Sort the dataframe
        filtered_df = filtered_df.sort_values(by=sort_col, ascending=(sort_order == "Ascending"))

        # Optimize columns for display
        display_columns = [
            'name', 'inferred_location', 'location_type', 'file_size_(gb)',
            'storage_cost_usd', 'storage_cost_aed', 'carbon_savings',
            'confidence_score', 'created_date'
        ]
        display_columns = [col for col in display_columns if col in filtered_df.columns]
        
        # Prepare display DataFrame with formatted columns
        display_df = filtered_df[display_columns].copy()
        
        # Format numeric columns
        numeric_cols = display_df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_cols:
            if 'cost' in col.lower() or 'savings' in col.lower():
                display_df[col] = display_df[col].round(2).apply(lambda x: f"${x:,.2f}" if 'usd' in col.lower() else f"AED {x:,.2f}")
            elif 'gb' in col.lower():
                display_df[col] = display_df[col].round(2).apply(lambda x: f"{x:,.2f} GB")
            elif 'score' in col.lower():
                display_df[col] = display_df[col].apply(lambda x: f"{x*100:.1f}%")
            else:
                display_df[col] = display_df[col].round(2)

        # Format date columns
        if 'created_date' in display_df.columns:
            display_df['created_date'] = pd.to_datetime(display_df['created_date']).dt.strftime('%Y-%m-%d')

        # Rename columns for better display
        column_names = {
            'name': 'File Name',
            'inferred_location': 'Location',
            'location_type': 'Type',
            'file_size_(gb)': 'Size',
            'storage_cost_usd': 'Cost (USD)',
            'storage_cost_aed': 'Cost (AED)',
            'carbon_savings': 'Carbon Savings',
            'confidence_score': 'Confidence',
            'created_date': 'Created Date'
        }
        display_df.columns = [column_names.get(col, col) for col in display_df.columns]

        # Display summary metrics
        st.markdown("### 📊 Summary")
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric("Total Records", f"{len(filtered_df):,}")
        with metric_col2:
            st.metric("Total Size", f"{filtered_df['file_size_(gb)'].sum():,.2f} GB")
        with metric_col3:
            st.metric("Avg. Confidence", f"{(filtered_df['confidence_score'].mean() * 100):.1f}%")

        # Display the grid
        st.markdown("### 🧾 Filtered Recommendations")
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )

        # Export options
        st.markdown("### 📥 Export Options")
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            csv = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Raw Data (CSV)",
                data=csv,
                file_name="raw_recommendations.csv",
                mime="text/csv"
            )
            
        with export_col2:
            formatted_csv = display_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Formatted Data (CSV)",
                data=formatted_csv,
                file_name="formatted_recommendations.csv",
                mime="text/csv"
            )
