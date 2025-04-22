import streamlit as st
from streamlit_option_menu import option_menu
from views import upload_process, roi_summary, visualizations, roi_explorer, business_roi, forecast

st.set_page_config(
    page_title="Delete Storage ROI App",
    page_icon="💾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 2rem;
    }
    .feature-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #2E7D32;
        margin-top: 1rem;
    }
    .feature-text {
        font-size: 1rem;
        color: #616161;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1E88E5;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #616161;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1E88E5;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for navigation if not exists
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = None

# Sidebar navigation using option_menu
with st.sidebar:
    selected = option_menu(
        menu_title="Navigation",
        options=["Home", "Upload & Process", "ROI Summary", "Visualizations", "ROI Explorer", "Business ROI", "Forecast"],
        icons=["house", "cloud-upload", "bar-chart-line", "pie-chart", "table", "briefcase", "graph-up"],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#f0f2f6"},
            "icon": {"color": "#1E88E5", "font-size": "18px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#e3f2fd"
            },
            "nav-link-selected": {"background-color": "#1E88E5", "color": "white", "font-weight": "normal"}
        }
    )

# Handle session state navigation
if st.session_state['current_view'] == 'forecast':
    selected = "Forecast"
    st.session_state['current_view'] = None

# Render selected section
if selected == "Home":
    # Header Section
    st.markdown('<p class="main-header">🚀 Turbonomic ROI Assistant</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Optimize Your Storage Infrastructure with Intelligent Analytics</p>', unsafe_allow_html=True)

    # Quick Stats Section
    st.markdown("### 📊 Quick Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">💾</div>
            <div class="metric-label">Storage Optimization</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">💰</div>
            <div class="metric-label">Cost Analysis</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">🌱</div>
            <div class="metric-label">Sustainability Metrics</div>
        </div>
        """, unsafe_allow_html=True)

    # Main Features Section
    st.markdown("### 🎯 Key Features")
    
    feature_col1, feature_col2 = st.columns(2)
    
    with feature_col1:
        st.markdown('<p class="feature-header">📈 Analytics & Insights</p>', unsafe_allow_html=True)
        st.markdown("""
        - **Storage Analytics**: Detailed storage usage patterns
        - **Cost Analysis**: Comprehensive cost savings calculations
        - **Sustainability Metrics**: Environmental impact assessment
        - **Performance Tracking**: Monitor optimization progress
        """)
        
        st.markdown('<p class="feature-header">🔍 Detailed Exploration</p>', unsafe_allow_html=True)
        st.markdown("""
        - **ROI Explorer**: Deep dive into recommendations
        - **Business ROI**: Financial impact analysis
        - **Custom Filters**: Tailored data views
        - **Export Options**: Multiple format support
        """)

    with feature_col2:
        st.markdown('<p class="feature-header">📊 Reporting & Forecasting</p>', unsafe_allow_html=True)
        st.markdown("""
        - **Business Reports**: Professional PDF reports
        - **Growth Forecasting**: 12-month projections
        - **Trend Analysis**: Historical data patterns
        - **Custom Visualizations**: Interactive charts
        """)
        
        st.markdown('<p class="feature-header">⚙️ Process Management</p>', unsafe_allow_html=True)
        st.markdown("""
        - **Data Processing**: Automated file handling
        - **Batch Operations**: Bulk recommendation processing
        - **Version Control**: Track changes over time
        - **Configuration Options**: Customizable settings
        """)

    # Getting Started Section
    st.markdown("### 🚀 Getting Started")
    st.markdown("""
    <div class="info-box">
    <b>Quick Start Guide:</b><br>
    1. Navigate to <b>Upload & Process</b> to import your Turbonomic data<br>
    2. Configure your ROI parameters in the settings<br>
    3. Explore insights in <b>ROI Summary</b> and <b>Visualizations</b><br>
    4. Generate reports in <b>Business ROI</b><br>
    5. View future projections in <b>Forecast</b>
    </div>
    """, unsafe_allow_html=True)

    # Help & Support Section
    st.markdown("### ℹ️ Help & Resources")
    help_col1, help_col2 = st.columns(2)
    
    with help_col1:
        st.info("**Need Help?**\nCheck out our documentation or contact support for assistance.")
    
    with help_col2:
        st.warning("**Pro Tip:**\nUse the sidebar navigation to quickly access different sections of the application.")

elif selected == "Upload & Process":
    upload_process.render()

elif selected == "ROI Summary":
    roi_summary.render()

elif selected == "Visualizations":
    visualizations.render()

elif selected == "ROI Explorer":
    roi_explorer.render()

elif selected == "Business ROI":
    business_roi.render()

elif selected == "Forecast":
    forecast.render()
