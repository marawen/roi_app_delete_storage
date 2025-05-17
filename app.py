import streamlit as st
from streamlit_option_menu import option_menu
from views import upload_process, roi_summary, visualizations, roi_explorer, business_roi, forecast, home, settings
import base64

# First, check if session_state exists before trying to access it
if 'is_logged_in' not in st.session_state:
    st.session_state["is_logged_in"] = False

# Initialize current view in session state if not exists
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'home'

# Set page config
st.set_page_config(
    page_title="Turbo ROI Assistant",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"  # Always expanded
)

# ✅ Define the SVG logo
def get_svg_base64():
    svg_code = '''<svg viewBox="0 0 120 80" xmlns="http://www.w3.org/2000/svg">
  <!-- Background (transparent) -->
  <rect x="0" y="0" width="120" height="80" fill="white" opacity="0" />
  
  <!-- Logo Group -->
  <g transform="translate(10, 10)">
    <!-- Graphs with gradient fills -->
    <defs>
      <linearGradient id="greenGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#4CAF50" />
        <stop offset="100%" stop-color="#2E7D32" />
      </linearGradient>
      <linearGradient id="blueGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#1976D2" />
        <stop offset="100%" stop-color="#0D47A1" />
      </linearGradient>
      <linearGradient id="redGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#E91E63" />
        <stop offset="100%" stop-color="#AD1457" />
      </linearGradient>
    </defs>
    
    <!-- Bar Chart -->
    <g>
      <!-- Bar 1 (Green) -->
      <rect x="0" y="25" width="14" height="35" rx="2" ry="2" fill="url(#greenGrad)" />
      
      <!-- Bar 2 (Red/Pink) -->
      <rect x="20" y="40" width="14" height="20" rx="2" ry="2" fill="url(#redGrad)" />
      
      <!-- Bar 3 (Blue) -->
      <rect x="40" y="15" width="14" height="45" rx="2" ry="2" fill="url(#blueGrad)" />
      
      <!-- Baseline -->
      <line x1="0" y1="60" x2="54" y2="60" stroke="#444" stroke-width="2" />
    </g>
    
    <!-- Turbo Effect (Speed Lines) -->
    <g opacity="0.85">
      <path d="M65,22 C72,22 72,15 79,15" stroke="#1976D2" stroke-width="2.5" stroke-linecap="round" fill="none" />
      <path d="M65,32 C72,32 72,25 79,25" stroke="#1976D2" stroke-width="2.5" stroke-linecap="round" fill="none" />
      <path d="M65,42 C72,42 72,35 79,35" stroke="#1976D2" stroke-width="2.5" stroke-linecap="round" fill="none" />
    </g>
    
    <!-- Upward trending arrow -->
    <g transform="translate(75, 30)">
      <circle cx="0" cy="0" r="15" fill="#FFFFFF" opacity="0.5" />
      <path d="M-8,8 L0,-8 L8,8 M0,-8 L0,15" stroke="#1976D2" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none" />
    </g>
    
    <!-- ROI text embedded in the design -->
    <g transform="translate(85, 55)">
      <rect x="-15" y="-12" width="30" height="24" rx="4" ry="4" fill="#1976D2" opacity="0.9" />
      <text x="0" y="5" font-family="Arial, sans-serif" font-weight="bold" font-size="14" text-anchor="middle" fill="white">ROI</text>
    </g>
  </g>
</svg>'''
    
    # Convert to base64
    b64 = base64.b64encode(svg_code.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"

# Get the base64 encoded SVG
logo_b64 = get_svg_base64()

# ✅ Load styles - Add custom CSS directly
st.markdown("""
<style>
/* Hide Streamlit defaults */
header {visibility: hidden;}
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}

/* Remove extra whitespace */
.block-container {
    padding-top: 1rem !important;
    max-width: 1200px !important;
}

/* Remove extra padding in Streamlit elements */
.stHorizontalBlock {
    padding-top: 0 !important;
    gap: 1.5rem !important;
}

/* Fix title duplication */
h1:first-of-type {
    visibility: hidden;
    height: 0;
    margin: 0;
    padding: 0;
}

/* Custom page title */
.page-title {
    font-size: 2rem;
    font-weight: 600;
    color: #333;
    margin-bottom: 1.5rem;
    padding-top: 1rem;
}

/* Main headers */
.main-header {
    color: #333;
    font-size: 2.2rem;
    font-weight: 600;
    margin-bottom: 0.2rem;
    margin-top: 0.5rem;
    display: inline-block;
    vertical-align: middle;
}

.sub-header {
    color: #546E7A;
    font-size: 1rem;
    margin-bottom: 2.5rem;
}

/* Benefits Cards */
.benefits-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 1rem;
    margin-top: 1.5rem;
}

.benefit-card {
    background: white;
    padding: 1.2rem;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    height: 100%;
}

.benefit-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.benefit-card h3 {
    font-size: 1.1rem;
    margin-bottom: 0.7rem;
    color: #333;
    font-weight: 500;
}

.benefit-card p {
    font-size: 0.9rem;
    color: #546E7A;
    line-height: 1.4;
}

/* Card styling */
.intro-card, .step-card, .insight-card {
    background: white;
    padding: 1.2rem;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    margin-bottom: 1rem;
}

.section-header {
    font-size: 1.3rem;
    font-weight: 600;
    color: #1976D2;
    margin: 1.5rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e0e0e0;
}

/* Step cards for homepage */
.step-card {
    height: 100%;
    position: relative;
    padding-bottom: 4rem;
}

.step-number {
    display: inline-block;
    width: 30px;
    height: 30px;
    background-color: #1976D2;
    color: white;
    border-radius: 50%;
    text-align: center;
    line-height: 30px;
    font-weight: bold;
    margin-bottom: 0.5rem;
}

.card-button {
    position: absolute;
    bottom: 1.2rem;
    left: 1.2rem;
    right: 1.2rem;
    background-color: #E3F2FD;
    color: #1976D2;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    text-align: center;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
}

.card-button:hover {
    background-color: #1976D2;
    color: white;
}

.card-link {
    text-decoration: none;
}

/* Settings summary */
.settings-summary {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.summary-item {
    display: flex;
    justify-content: space-between;
    padding: 0.3rem 0;
    border-bottom: 1px solid #e0e0e0;
}

.summary-item:last-child {
    border-bottom: none;
}

/* Action buttons */
.action-button {
    background-color: #1976D2;
    color: white;
    padding: 0.8rem 1.2rem;
    border-radius: 6px;
    text-align: center;
    font-weight: 500;
    margin-bottom: 1rem;
    cursor: pointer;
    transition: all 0.2s;
}

.action-button:hover {
    background-color: #1565C0;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.action-button.secondary {
    background-color: #E3F2FD;
    color: #1976D2;
}

.action-button.secondary:hover {
    background-color: #BBDEFB;
}

.button-link {
    text-decoration: none;
    display: block;
}

/* Navigation button */
.navigate-button {
    display: inline-block;
    background-color: #1976D2;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-weight: 500;
    cursor: pointer;
}

/* Welcome banner */
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

/* Upload instruction */
.upload-instruction {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
}

/* Sign in section */
.sign-in-header {
    font-size: 1.3rem;
    font-weight: 500;
    margin-bottom: 1.5rem;
    color: #1976D2;
}

/* Blue separator */
.blue-separator {
    background-color: #1976D2;
    width: 4px;
    border-radius: 2px;
    margin: 0 auto;
}

/* Footer */
.custom-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    text-align: center;
    font-size: 0.85rem;
    color: #90a4ae;
    padding: 1rem 0;
    background-color: white;
    border-top: 1px solid #f0f0f0;
}

/* Main content area needs padding to avoid footer overlap */
.main-content-area {
    padding-bottom: 60px;
}

/* Logo styling */
.logo-container {
    display: flex;
    align-items: center;
    margin-bottom: 0.5rem;
}

.logo-img {
    width: 75px;
    height: 50px;
    margin-right: 15px;
}

/* Sidebar logo styling */
.sidebar-logo {
    width: 70px;
    margin: 1rem auto 1.5rem;
    display: block;
}

/* Metrics styling */
[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: #1976D2 !important;
}

[data-testid="stMetricLabel"] {
    font-size: 0.9rem !important;
    font-weight: 500 !important;
}

/* Logout button styling */
.logout-container {
    padding: 1rem;
    margin-top: 2rem;
    border-top: 1px solid #e0e0e0;
}

.user-info {
    font-size: 0.9rem;
    color: #546E7A;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
}

.user-avatar {
    display: inline-flex;
    width: 28px;
    height: 28px;
    background-color: #1976D2;
    color: white;
    border-radius: 50%;
    align-items: center;
    justify-content: center;
    font-weight: 500;
    margin-right: 0.7rem;
}
</style>
""", unsafe_allow_html=True)

# ✅ Basic login check
def check_login(username, password):
    return username == "admin" and password == "ibm123456"

# ✅ Simple login form
def render_login():
    # Logo and title - using the SVG as base64-encoded image
    st.markdown(f"""
    <div class="logo-container">
        <img src="{logo_b64}" alt="Turbo ROI Logo" class="logo-img">
        <h1 class="main-header">Turbo ROI Assistant</h1>
    </div>
    <p class="sub-header">Optimize storage. Visualize value. Drive ROI with confidence.</p>
    """, unsafe_allow_html=True)
    
    # Main content area with padding for footer
    st.markdown("<div class='main-content-area'>", unsafe_allow_html=True)
    
    # Layout with columns - better sizing for proper spacing
    col1, col_sep, col2 = st.columns([5, 0.2, 3.5])

    with col1:
        # Cards section - spacing control
        st.markdown("""
        <div class="benefits-grid">
            <div class="benefit-card">
                <h3>📈 Analytics</h3>
                <p>Actionable insights from your storage recommendations.</p>
            </div>
            <div class="benefit-card">
                <h3>💰 ROI</h3>
                <p>Real-time savings projections and cost avoidance metrics.</p>
            </div>
            <div class="benefit-card">
                <h3>🌿 Efficiency</h3>
                <p>Drive sustainability and reduce waste intelligently.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_sep:
        # Blue separator with full height
        st.markdown(
            """
            <div class="blue-separator" style="height: 330px;"></div>
            """, 
            unsafe_allow_html=True
        )

    with col2:
        # Sign In section - no extra container, just direct elements
        st.markdown('<div class="sign-in-header">🔐 Sign In</div>', unsafe_allow_html=True)
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        # Make the button match the screenshot
        sign_in_button = st.button("Sign In")
        if sign_in_button:
            if check_login(username, password):
                st.session_state["is_logged_in"] = True
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown(
        """
        <div class='custom-footer'>
            © 2025 Turbo ROI Assistant – All rights reserved.
        </div>
        """, 
        unsafe_allow_html=True
    )

# ✅ App view after login with sidebar menu
def render_logged_in_app():
    # Map view names to their display names for the sidebar
    view_display_names = {
        "home": "Home",
        "settings": "Settings",
        "upload_process": "Upload & Process",
        "roi_summary": "ROI Summary",
        "visualizations": "Visualizations",
        "roi_explorer": "ROI Explorer",
        "business_roi": "Business ROI",
        "forecast": "Forecast",
    }
    
    # Map view names to their icons
    view_icons = {
        "home": "house",
        "settings": "gear",
        "upload_process": "cloud-upload",
        "roi_summary": "bar-chart-line",
        "visualizations": "pie-chart",
        "roi_explorer": "table",
        "business_roi": "briefcase",
        "forecast": "graph-up",
    }
    
    with st.sidebar:
        # Add logo to sidebar
        st.markdown(f'<img src="{logo_b64}" alt="Turbo ROI Logo" class="sidebar-logo">', unsafe_allow_html=True)
        
        # Get all view names and their display names
        view_names = list(view_display_names.keys())
        display_names = [view_display_names[view] for view in view_names]
        icons = [view_icons[view] for view in view_names]
        
        # Find index of current view
        try:
            default_index = view_names.index(st.session_state['current_view'])
        except ValueError:
            default_index = 0  # Default to Home if view not found
        
        # Using option_menu for navigation
        selected_display = option_menu(
            menu_title="Turbo ROI",
            options=display_names,
            icons=icons,
            default_index=default_index,
            styles={
                "container": {"padding": "0!important", "background-color": "#f8f9fa"},
                "icon": {"color": "#1976D2", "font-size": "16px"},
                "nav-link": {
                    "font-size": "15px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#e3f2fd",
                    "padding": "10px 15px",
                },
                "nav-link-selected": {
                    "background-color": "#1976D2",
                    "color": "white",
                    "font-weight": "500"
                },
                "menu-title": {
                    "margin": "10px 0",
                    "color": "#424242",
                    "font-size": "18px"
                }
            }
        )
        
        # Convert selected display name back to view name
        selected_view = view_names[display_names.index(selected_display)]
        
        # Update current view if changed
        if selected_view != st.session_state['current_view']:
            st.session_state['current_view'] = selected_view
            st.rerun()
        
        # Add logout section to the bottom of the sidebar
        st.markdown("""
        <div class="logout-container">
            <div class="user-info">
                <div class="user-avatar">A</div>
                <span>admin@company.com</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Logout button
        if st.button("🔒 Logout", use_container_width=True):
            st.session_state["is_logged_in"] = False
            st.rerun()
    
    # Main content area
    st.markdown("<div class='main-content-area'>", unsafe_allow_html=True)
    
    # Route to the appropriate view
    current_view = st.session_state['current_view']
    if current_view == "home":
        home.render()
    elif current_view == "settings":
        settings.render()
    elif current_view == "upload_process":
        upload_process.render()
    elif current_view == "roi_summary":
        roi_summary.render()
    elif current_view == "visualizations":
        visualizations.render()
    elif current_view == "roi_explorer":
        roi_explorer.render()
    elif current_view == "business_roi":
        business_roi.render()
    elif current_view == "forecast":
        forecast.render()
    else:
        # Default to home if view not recognized
        home.render()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown(
        """
        <div class='custom-footer'>
            © 2025 Turbo ROI Assistant – All rights reserved.
        </div>
        """, 
        unsafe_allow_html=True
    )

# ✅ App entry
if st.session_state["is_logged_in"]:
    render_logged_in_app()
else:
    render_login()