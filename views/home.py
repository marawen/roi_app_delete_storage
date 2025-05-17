import streamlit as st
import pandas as pd
import os

def render():
    # Custom title with improved wording
    st.markdown('<div class="page-title">🏠 Command Center</div>', unsafe_allow_html=True)
    
    # Welcome message
    st.markdown("""
    <div class="welcome-banner">
        <h2>Welcome to Turbo ROI Assistant</h2>
        <p>Optimize storage, visualize value, and drive ROI with confidence.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Process explanation with smaller heading
    st.markdown("""
    <div class="process-explanation">
        <h3 style="font-size: 1.2rem; margin-bottom: 0.7rem;">Streamlined ROI Workflow</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create CSS for horizontal workflow cards
    st.markdown("""
    <style>
    .workflow-container {
        display: flex;
        flex-direction: row;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .workflow-step {
        flex: 1;
        background: white;
        padding: 1.2rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        position: relative;
        min-height: 200px;
        display: flex;
        flex-direction: column;
    }
    
    .step-number {
        display: inline-block;
        width: 26px;
        height: 26px;
        background-color: #1976D2;
        color: white;
        border-radius: 50%;
        text-align: center;
        line-height: 26px;
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 0.5rem;
    }
    
    .workflow-step h4 {
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #333;
    }
    
    .step-description {
        font-size: 0.85rem;
        color: #546E7A;
        line-height: 1.3;
        margin-bottom: 1rem;
    }
    
    .section-subheader {
        font-size: 1.2rem;
        font-weight: 600;
        color: #333;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create three columns for the workflow cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="workflow-step">
            <div class="step-number">1</div>
            <h4>Configure Settings</h4>
            <p class="step-description">Set up storage costs, energy metrics, and labor costs parameters.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Settings", key="go_to_settings"):
            st.session_state['current_view'] = 'settings'
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="workflow-step">
            <div class="step-number">2</div>
            <h4>Upload & Process</h4>
            <p class="step-description">Upload Turbonomic Delete Storage recommendation Excel files.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Upload Files", key="go_to_upload"):
            st.session_state['current_view'] = 'upload_process'
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="workflow-step">
            <div class="step-number">3</div>
            <h4>Analyze Results</h4>
            <p class="step-description">Review ROI summaries, visualizations, and actionable insights.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Results", key="go_to_results"):
            st.session_state['current_view'] = 'roi_summary'
            st.rerun()
    
    # Recent activity section - if there's processed data
    if os.path.exists('outputs/processed_data.csv') and 'processed_df' in st.session_state:
        st.markdown("---")
        st.markdown('<div class="section-subheader">📊 Recent Analysis Results</div>', unsafe_allow_html=True)
        
        # Try to read the most recent processing results
        try:
            df = st.session_state.get('processed_df', pd.read_csv('outputs/processed_data.csv'))
            
            # Display summary metrics
            if 'file_size_(gb)' in df.columns:
                total_size = df['file_size_(gb)'].sum()
                total_actions = len(df)
                
                # Metrics in 4 columns for better spacing
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Storage Actions", f"{total_actions:,}")
                col2.metric("Total Size", f"{total_size:.2f} GB")
                
                # If we have ROI data stored in session, display it
                if 'last_processed_results' in st.session_state:
                    results = st.session_state['last_processed_results']
                    if 'totals' in results:
                        col3.metric("Cost Savings", f"${results['totals']['net_savings_usd']:,.2f}")
                        col4.metric("CO₂ Reduction", f"{results['totals']['carbon_savings']:,.1f} kg")
                
                # Quick action buttons in a more compact layout
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    if st.button("📊 View ROI Summary", key="continue_to_summary"):
                        st.session_state['current_view'] = 'roi_summary'
                        st.rerun()
                
                with col2:
                    if st.button("📈 Explore Visualizations", key="continue_to_viz"):
                        st.session_state['current_view'] = 'visualizations'
                        st.rerun()
        except Exception as e:
            st.warning(f"Could not load recent activity. You may need to upload and process new data.")
    
    # Tips section with a better title
    st.markdown("---")
    st.markdown('<div class="section-subheader">💡 Quick Tips & Resources</div>', unsafe_allow_html=True)
    
    # Two-column layout for tips
    tips_col1, tips_col2 = st.columns(2)
    
    with tips_col1:
        with st.expander("📘 Getting Started", expanded=False):
            st.markdown("""
            - **Step 1**: Configure your ROI parameters in Settings
            - **Step 2**: Upload your Turbonomic Excel files
            - **Step 3**: Analyze the results in ROI Summary and Visualizations
            - **Pro Tip**: You can adjust settings at any time to compare different scenarios
            """)
            
        with st.expander("🔍 Understanding Your Data", expanded=False):
            st.markdown("""
            - Check the 'ROI Score' column to identify high-value actions
            - Look at 'Location Label' to see where storage is being used
            - The 'Age Days' metric shows how long files have been inactive
            - Higher 'Confidence Score' means more reliable recommendations
            """)
    
    with tips_col2:
        with st.expander("⚡ Performance Tips", expanded=False):
            st.markdown("""
            - Focus first on recommendations with both high ROI and high confidence
            - Consider location when prioritizing cleanup actions
            - Group actions by platform type for more efficient implementation
            - Set realistic implementation timelines in your settings
            """)
            
        with st.expander("📊 Interpreting Results", expanded=False):
            st.markdown("""
            - Storage savings represent direct cost reduction potential
            - Energy savings contribute to sustainability goals
            - Labor vs. automation costs help optimize your implementation approach
            - The forecast shows the impact of continued optimization
            """)