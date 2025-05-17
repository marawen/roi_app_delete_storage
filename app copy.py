import streamlit as st
from streamlit_option_menu import option_menu
from views import upload_process, roi_summary, visualizations, roi_explorer, business_roi, forecast

st.set_page_config(
    page_title="Delete Storage ROI App",
    page_icon="💾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Updated CSS for the entire page
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #f6f8fc 0%, #e9f1f9 100%);
    }
    
    /* Main Layout */
    .split-layout {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 4rem;
        padding: 2rem 4rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .left-content {
        flex: 1;
        max-width: 600px;
    }
    
    .right-content {
        flex: 1;
        max-width: 400px;
    }
    
    /* Typography */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(45deg, #1E88E5, #1565C0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        line-height: 1.2;
    }
    
    .sub-header {
        font-size: 1.25rem;
        color: #546E7A;
        margin-bottom: 2.5rem;
        font-weight: 400;
        line-height: 1.6;
        opacity: 0.9;
    }
    
    /* Login Form */
    .login-section {
        padding: 0;
        max-width: 400px;
        margin: 0;
    }
    
    .login-header {
        color: #1E88E5;
        margin-bottom: 2rem;
        font-size: 2rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.5);
        border: 2px solid rgba(30, 136, 229, 0.1);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        font-size: 1rem;
        margin-bottom: 1.2rem;
        transition: all 0.3s ease;
        width: 100%;
        box-sizing: border-box;
        backdrop-filter: blur(8px);
    }
    
    .stTextInput > div > div > input:focus {
        background: rgba(255, 255, 255, 0.8);
        border-color: #1E88E5;
        box-shadow: 0 0 0 4px rgba(30, 136, 229, 0.1);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #90a4ae;
    }
    
    .stTextInput > label {
        color: #37474F;
        font-size: 0.95rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    /* Button */
    .stButton > button {
        background: linear-gradient(45deg, #1E88E5, #1565C0);
        color: white;
        border: none;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1rem;
        width: 100%;
        transition: all 0.3s ease;
        margin-top: 1.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(30, 136, 229, 0.2);
        background: linear-gradient(45deg, #1976D2, #1565C0);
    }
    
    /* Benefits Section */
    .benefits-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
        margin-top: 3rem;
    }
    
    .benefit-card {
        background: rgba(255, 255, 255, 0.5);
        padding: 1.8rem;
        border-radius: 16px;
        border: 1px solid rgba(30, 136, 229, 0.1);
        transition: transform 0.2s ease;
        backdrop-filter: blur(8px);
    }
    
    .benefit-card:hover {
        transform: translateY(-5px);
    }
    
    .benefit-card h3 {
        color: #1E88E5;
        font-size: 1.4rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .benefit-card p {
        color: #546E7A;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* Error Message */
    .stAlert {
        background: rgba(255, 235, 238, 0.8);
        color: #d32f2f;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(211, 47, 47, 0.2);
        margin-top: 1rem;
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        backdrop-filter: blur(8px);
    }
    
    /* Remove default Streamlit styles */
    div[data-testid="stForm"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    
    div[data-testid="stVerticalBlock"] > div:has(div.stTextInput) {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    
    /* Dashboard Styles */
    .metric-card {
        background: rgba(255, 255, 255, 0.5);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(30, 136, 229, 0.1);
        transition: transform 0.2s ease;
        backdrop-filter: blur(8px);
        text-align: center;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-value {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        background: linear-gradient(45deg, #1E88E5, #1565C0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        color: #546E7A;
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    .feature-section {
        background: rgba(255, 255, 255, 0.5);
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid rgba(30, 136, 229, 0.1);
        backdrop-filter: blur(8px);
        margin: 1.5rem 0;
    }
    
    .feature-header {
        color: #1E88E5;
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .feature-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .feature-list li {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.8rem 0;
        border-bottom: 1px solid rgba(30, 136, 229, 0.1);
        color: #546E7A;
    }
    
    .feature-list li:last-child {
        border-bottom: none;
    }
    
    .info-box {
        background: rgba(255, 255, 255, 0.5);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(30, 136, 229, 0.1);
        backdrop-filter: blur(8px);
        margin: 1.5rem 0;
    }
    
    .info-box b {
        color: #1E88E5;
    }
    
    .help-card {
        background: rgba(255, 255, 255, 0.5);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(30, 136, 229, 0.1);
        backdrop-filter: blur(8px);
        height: 100%;
    }
    
    .help-card h4 {
        color: #1E88E5;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for navigation and login
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = None
if 'is_logged_in' not in st.session_state:
    st.session_state['is_logged_in'] = False

# Login function
def check_login(username, password):
    return username == "admin" and password == "ibm123456"

# Logout function
def logout():
    st.session_state['is_logged_in'] = False
    st.rerun()

# Sidebar navigation using option_menu
with st.sidebar:
    if st.session_state['is_logged_in']:
        selected = option_menu(
            menu_title="Navigation",
            options=["Home", "Upload & Process", "ROI Summary", "Visualizations", "ROI Explorer", "Business ROI", "Forecast", "Logout"],
            icons=["house", "cloud-upload", "bar-chart-line", "pie-chart", "table", "briefcase", "graph-up", "box-arrow-right"],
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#f8f9fa"},
                "icon": {"color": "#1E88E5", "font-size": "18px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#e3f2fd",
                    "padding": "12px 20px",
                },
                "nav-link-selected": {"background-color": "#1E88E5", "color": "white", "font-weight": "500"}
            }
        )
        if selected == "Logout":
            logout()
    else:
        selected = option_menu(
            menu_title="Navigation",
            options=["Home"],
            icons=["house"],
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#f8f9fa"},
                "icon": {"color": "#1E88E5", "font-size": "18px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#e3f2fd",
                    "padding": "12px 20px",
                },
                "nav-link-selected": {"background-color": "#1E88E5", "color": "white", "font-weight": "500"}
            }
        )

# Handle session state navigation
if st.session_state['current_view'] == 'forecast':
    selected = "Forecast"
    st.session_state['current_view'] = None

# Render selected section
if selected == "Home":
    if not st.session_state['is_logged_in']:
        st.markdown('<div class="split-layout">', unsafe_allow_html=True)
        
        # Left content (Main content)
        st.markdown('<div class="left-content">', unsafe_allow_html=True)
        st.markdown('<h1 class="main-header">Welcome to Turbonomic ROI Assistant</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Transform your storage infrastructure with intelligent analytics and maximize your ROI through data-driven insights.</p>', unsafe_allow_html=True)
        
        # Benefits Grid
        st.markdown("""
        <div class="benefits-grid">
            <div class="benefit-card">
                <h3>📈 Analytics</h3>
                <p>Advanced storage analytics and visualization tools for deep insights.</p>
            </div>
            <div class="benefit-card">
                <h3>💰 ROI</h3>
                <p>Maximize returns through intelligent storage optimization.</p>
            </div>
            <div class="benefit-card">
                <h3>🌱 Efficiency</h3>
                <p>Improve operational efficiency while reducing costs.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Right content (Login form)
        st.markdown('<div class="right-content">', unsafe_allow_html=True)
        st.markdown('<div class="login-section">', unsafe_allow_html=True)
        st.markdown('<h2 class="login-header">🔐 Sign In</h2>', unsafe_allow_html=True)
        
        username = st.text_input("Username", 
                               key="username",
                               placeholder="Enter your username",
                               help="Your admin username")
        
        password = st.text_input("Password", 
                               type="password",
                               key="password",
                               placeholder="Enter your password",
                               help="Your admin password")
        
        if st.button("Sign In", use_container_width=True):
            if check_login(username, password):
                st.session_state['is_logged_in'] = True
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # Header Section
        st.markdown('<h1 class="main-header">🚀 Turbonomic ROI Assistant</h1>', unsafe_allow_html=True)
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
            st.markdown("""
            <div class="feature-section">
                <p class="feature-header">📈 Analytics & Insights</p>
                <ul class="feature-list">
                    <li>📊 Storage Analytics: Detailed storage usage patterns</li>
                    <li>💰 Cost Analysis: Comprehensive cost savings calculations</li>
                    <li>🌱 Sustainability Metrics: Environmental impact assessment</li>
                    <li>📈 Performance Tracking: Monitor optimization progress</li>
                </ul>
            </div>
            
            <div class="feature-section">
                <p class="feature-header">🔍 Detailed Exploration</p>
                <ul class="feature-list">
                    <li>🎯 ROI Explorer: Deep dive into recommendations</li>
                    <li>💼 Business ROI: Financial impact analysis</li>
                    <li>🔍 Custom Filters: Tailored data views</li>
                    <li>📤 Export Options: Multiple format support</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with feature_col2:
            st.markdown("""
            <div class="feature-section">
                <p class="feature-header">📊 Reporting & Forecasting</p>
                <ul class="feature-list">
                    <li>📑 Business Reports: Professional PDF reports</li>
                    <li>📈 Growth Forecasting: 12-month projections</li>
                    <li>📊 Trend Analysis: Historical data patterns</li>
                    <li>📉 Custom Visualizations: Interactive charts</li>
                </ul>
            </div>
            
            <div class="feature-section">
                <p class="feature-header">⚙️ Process Management</p>
                <ul class="feature-list">
                    <li>🔄 Data Processing: Automated file handling</li>
                    <li>📦 Batch Operations: Bulk recommendation processing</li>
                    <li>🔄 Version Control: Track changes over time</li>
                    <li>⚙️ Configuration Options: Customizable settings</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        # Getting Started Section
        st.markdown("### 🚀 Getting Started")
        st.markdown("""
        <div class="info-box">
            <b>Quick Start Guide:</b>
            <ul class="feature-list">
                <li>1️⃣ Navigate to <b>Upload & Process</b> to import your Turbonomic data</li>
                <li>2️⃣ Configure your ROI parameters in the settings</li>
                <li>3️⃣ Explore insights in <b>ROI Summary</b> and <b>Visualizations</b></li>
                <li>4️⃣ Generate reports in <b>Business ROI</b></li>
                <li>5️⃣ View future projections in <b>Forecast</b></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # Help & Support Section
        st.markdown("### ℹ️ Help & Resources")
        help_col1, help_col2 = st.columns(2)
        
        with help_col1:
            st.markdown("""
            <div class="help-card">
                <h4>📚 Need Help?</h4>
                <p>Check out our comprehensive documentation or reach out to our support team for assistance with any questions.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with help_col2:
            st.markdown("""
            <div class="help-card">
                <h4>💡 Pro Tip</h4>
                <p>Use the sidebar navigation to quickly access different sections of the application and streamline your workflow.</p>
            </div>
            """, unsafe_allow_html=True)

elif selected == "Upload & Process":
    if st.session_state['is_logged_in']:
        upload_process.render()
    else:
        st.warning("Please login to access this section.")

elif selected == "ROI Summary":
    if st.session_state['is_logged_in']:
        roi_summary.render()
    else:
        st.warning("Please login to access this section.")

elif selected == "Visualizations":
    if st.session_state['is_logged_in']:
        visualizations.render()
    else:
        st.warning("Please login to access this section.")

elif selected == "ROI Explorer":
    if st.session_state['is_logged_in']:
        roi_explorer.render()
    else:
        st.warning("Please login to access this section.")

elif selected == "Business ROI":
    if st.session_state['is_logged_in']:
        business_roi.render()
    else:
        st.warning("Please login to access this section.")

elif selected == "Forecast":
    if st.session_state['is_logged_in']:
        forecast.render()
    else:
        st.warning("Please login to access this section.")
