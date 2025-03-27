import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
import time

from utils import (
    plot_department_stress, plot_heart_rate_distribution,
    plot_spo2_distribution, plot_mood_distribution,
    create_gauge_chart, create_department_comparison_chart,
    get_mood_emoji
)
from data_processor import (
    load_data, get_departments, filter_data,
    get_summary_metrics, get_department_rankings
)
from chatbot import WellnessChatbot

# Page configuration
st.set_page_config(
    page_title="HR Wellness Dashboard",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced futuristic look
st.markdown("""
<style>
    /* Base theme */
    .main {
        background-color: #0e1117;
    }
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #1a1f36 100%);
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0e1117;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: #4a56e2;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #5a66f2;
    }
    
    /* Cards and containers */
    .data-card {
        border-radius: 10px;
        padding: 20px;
        background-color: rgba(26, 31, 54, 0.8);
        margin-bottom: 20px;
        border: 1px solid #2b325b;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .data-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(74, 86, 226, 0.3);
        border: 1px solid #4a56e2;
    }
    
    /* Metrics styling */
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #4a56e2;
        text-shadow: 0 0 15px rgba(74, 86, 226, 0.5);
        transition: all 0.3s ease;
    }
    .data-card:hover .metric-value {
        color: #5a66f2;
        transform: scale(1.05);
    }
    .metric-label {
        font-size: 14px;
        color: #c0c0c0;
        font-weight: 300;
    }
    
    /* Employee cards */
    .employee-card {
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
        background-color: rgba(26, 31, 54, 0.7);
        border: 1px solid #2b325b;
        transition: all 0.2s ease;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }
    .employee-card:hover {
        background-color: rgba(43, 50, 91, 0.8);
        border-left: 3px solid #4a56e2;
    }
    
    /* DataFrame styling */
    .stDataFrame {
        border-radius: 10px !important;
        background-color: rgba(26, 31, 54, 0.7) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Text elements */
    h1, h2, h3 {
        color: #ffffff;
        text-shadow: 0 0 10px rgba(74, 86, 226, 0.3);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(14, 17, 23, 0.3);
        padding: 5px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(26, 31, 54, 0.7);
        border-radius: 8px;
        padding: 10px 20px;
        color: white;
        transition: all 0.2s ease;
        border: 1px solid rgba(43, 50, 91, 0.5);
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(43, 50, 91, 0.9);
        border-color: #4a56e2;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4a56e2 !important;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(74, 86, 226, 0.4);
    }
    
    /* Sidebar styling */
    .css-1aumxhk, [data-testid="stSidebar"] {
        background-color: rgba(26, 31, 54, 0.85);
        border-right: 1px solid #2b325b;
        backdrop-filter: blur(10px);
    }
    [data-testid="stSidebarContent"] {
        background: linear-gradient(180deg, rgba(26, 31, 54, 0.9) 0%, rgba(14, 17, 23, 0.9) 100%);
    }
    
    /* Inputs and controls */
    .stSlider [data-baseweb="slider"] {
        height: 5px;
        background-color: rgba(43, 50, 91, 0.6) !important;
    }
    .stSlider [data-baseweb="slider"] [data-baseweb="thumb"] {
        height: 15px;
        width: 15px;
        background-color: #4a56e2;
        box-shadow: 0 0 10px rgba(74, 86, 226, 0.6);
    }
    .stCheckbox [data-testid="stCheckbox"] {
        color: #4a56e2 !important;
    }
    .stCheckbox [data-testid="stCheckbox"]:hover {
        color: #5a66f2 !important;
    }
    .stSelectbox [data-baseweb="select"] {
        background-color: rgba(26, 31, 54, 0.7);
        border: 1px solid #2b325b;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    .stSelectbox [data-baseweb="select"]:hover, .stSelectbox [data-baseweb="select"]:focus {
        border-color: #4a56e2;
        box-shadow: 0 0 0 1px #4a56e2;
    }
    
    /* Button styling */
    button[kind="primary"] {
        background-color: #4a56e2;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    button[kind="primary"]:hover {
        background-color: #5a66f2;
        box-shadow: 0 0 15px rgba(74, 86, 226, 0.5);
        transform: translateY(-2px);
    }
    
    /* Custom elements */
    .glow-text {
        color: #4a56e2;
        text-shadow: 0 0 10px rgba(74, 86, 226, 0.8);
        font-weight: bold;
    }
    .hover-zoom {
        transition: transform 0.3s ease;
    }
    .hover-zoom:hover {
        transform: scale(1.05);
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 6px;
    }
    .status-good {
        background-color: #4CAF50;
        box-shadow: 0 0 8px #4CAF50;
    }
    .status-warning {
        background-color: #FFC107;
        box-shadow: 0 0 8px #FFC107;
    }
    .status-critical {
        background-color: #F44336;
        box-shadow: 0 0 8px #F44336;
    }
    
    /* Animations */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    .pulse-animation {
        animation: pulse 2s infinite ease-in-out;
    }
    
    /* Neon borders */
    .neon-border {
        border: 1px solid #4a56e2;
        box-shadow: 0 0 10px rgba(74, 86, 226, 0.8), inset 0 0 10px rgba(74, 86, 226, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Load SVG logo
with open('assets/logo.svg', 'r') as f:
    svg_logo = f.read()

# Header
col1, col2 = st.columns([1, 5])
with col1:
    st.markdown(f'{svg_logo}', unsafe_allow_html=True)
with col2:
    st.title("Employee Wellness Dashboard")
    st.markdown("Monitor employee health metrics and analyze stress levels in real-time")

# Load data
with st.spinner("Loading wellness data..."):
    df = load_data()

# Sidebar for filters
st.sidebar.markdown("## Dashboard Controls")

# Add logo to sidebar
st.sidebar.markdown(f'{svg_logo}', unsafe_allow_html=True)
st.sidebar.markdown("---")

# Department filter
departments = get_departments(df)
selected_department = st.sidebar.selectbox("Select Department", departments)

# View mode
view_mode = st.sidebar.radio(
    "Dashboard View Mode",
    ["Standard", "Compact", "Detailed"],
    index=0
)

# Alert threshold customization
st.sidebar.markdown("## Alert Thresholds")
with st.sidebar.expander("Customize Thresholds"):
    hr_threshold = st.slider(
        "Heart Rate Alert (bpm)",
        min_value=80,
        max_value=120,
        value=100,
        step=5,
        help="Employees with heart rate above this value will be flagged"
    )
    
    stress_threshold = st.slider(
        "Stress Level Alert",
        min_value=50,
        max_value=90,
        value=70,
        step=5,
        help="Employees with stress level above this value will be flagged"
    )
    
    spo2_threshold = st.slider(
        "SpO2 Alert (%)",
        min_value=90,
        max_value=95,
        value=92,
        step=1,
        help="Employees with SpO2 below this value will be flagged"
    )

# Time range filter (for future implementation with time series data)
st.sidebar.markdown("## Time Range")
time_range = st.sidebar.radio(
    "Select Time Period",
    ["Today", "This Week", "This Month", "Quarter"],
    index=0
)

# Data visualization options
st.sidebar.markdown("## Visualization Options")
chart_type = st.sidebar.selectbox(
    "Chart Style",
    ["Standard", "Minimal", "Dark", "Futuristic"],
    index=3
)

include_annotations = st.sidebar.checkbox("Include Chart Annotations", value=True)
show_trend_lines = st.sidebar.checkbox("Show Trend Lines", value=True)

# Export options
st.sidebar.markdown("## Export & Share")
with st.sidebar.expander("Export Options"):
    export_format = st.radio(
        "Export Format",
        ["CSV", "Excel", "PDF", "JSON"],
        index=0
    )
    
    if st.button("Export Data"):
        st.info(f"In a production environment, this would export the data as {export_format}.")
    
    report_type = st.selectbox(
        "Schedule Reports",
        ["Daily Summary", "Weekly Analytics", "Monthly Overview", "Custom"],
        index=1
    )
    
    if st.button("Schedule"):
        st.success(f"Report scheduled: {report_type}")

# Apply filters
filtered_df = filter_data(df, selected_department)

# Calculate summary metrics
metrics = get_summary_metrics(filtered_df)

# Database information
st.sidebar.markdown("## Database")
st.sidebar.info("PostgreSQL database is connected and storing employee wellness data.")

# Last updated timestamp
current_time = datetime.now().strftime("%d %b %Y, %H:%M:%S")
st.sidebar.markdown(f"**Last Updated:** {current_time}")

# Admin section (collapsible)
with st.sidebar.expander("Admin Controls"):
    st.markdown("#### Database Management")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Reset Demo Data"):
            # This will clear the cache and reload the data
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        if st.button("Archive Data"):
            st.info("This would archive old data to storage.")
    
    st.markdown("#### User Management")
    user_role = st.selectbox(
        "Current User Role",
        ["HR Manager", "Department Head", "Executive", "Admin"],
        index=0
    )
    
    st.markdown("#### Data Refresh")
    refresh_rate = st.select_slider(
        "Auto Refresh Rate",
        options=["Off", "1 min", "5 min", "15 min", "30 min"],
        value="Off"
    )
    st.caption("In a production environment, this would automatically refresh data from sensors.")
    
    advanced_settings = st.checkbox("Show Advanced Settings", value=False)
    if advanced_settings:
        st.markdown("#### System Settings")
        cache_time = st.number_input("Cache Time (minutes)", min_value=1, max_value=60, value=5)
        max_records = st.number_input("Max Records to Display", min_value=10, max_value=500, value=100)
        st.caption("These settings would affect system performance.")

# Refresh button
if st.sidebar.button("Refresh Dashboard"):
    st.rerun()

# Help section
with st.sidebar.expander("Help & Resources"):
    st.markdown("""
    - **Documentation**: View dashboard documentation
    - **Support**: Contact system administrator
    - **Training**: Schedule HR wellness training
    - **FAQ**: Frequently asked questions
    """)
    
    if st.button("Contact Support"):
        st.info("In a production environment, this would open a support ticket system.")

# Main dashboard
# Top metrics row with animation and interactive elements
st.markdown("## Health Metrics Overview")

# Add a header with animated effect
st.markdown("""
<div style="padding: 10px; margin-bottom: 20px; border-radius: 10px; background-color: rgba(26, 31, 54, 0.7); text-align: center;">
    <h2 class="glow-text pulse-animation" style="margin: 0; font-size: 1.8rem;">Real-Time Wellness Metrics</h2>
    <p style="color: #c0c0c0; margin-top: 5px;">Interactive dashboard with live metrics and alerts</p>
</div>
""", unsafe_allow_html=True)

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

# Determine status classes based on thresholds
hr_status = "status-good" if metrics['avg_heart_rate'] < hr_threshold else "status-critical" 
spo2_status = "status-critical" if metrics['avg_spo2'] < spo2_threshold else "status-good"
stress_status = "status-good" if stress_threshold > 70 else "status-warning" if stress_threshold > 50 else "status-critical"

with metric_col1:
    st.markdown(f"""
    <div class="data-card hover-zoom neon-border">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h4 style="margin: 0;">Total Employees</h4>
            <div class="status-indicator status-good"></div>
        </div>
        <div class="metric-value pulse-animation">{metrics['total_employees']}</div>
        <div class="metric-label">
            {f"In {selected_department}" if selected_department != 'All Departments' else "Across all departments"}
        </div>
        <div style="margin-top: 10px; font-size: 12px; color: #c0c0c0;">
            <span style="display: inline-block; width: 8px; height: 8px; background-color: #4a56e2; margin-right: 5px; border-radius: 50%;"></span> Updated {current_time.split(',')[1].strip()}
        </div>
    </div>
    """, unsafe_allow_html=True)

with metric_col2:
    # Add animation if heart rate is outside normal range
    animation_class = "pulse-animation" if metrics['avg_heart_rate'] > 100 or metrics['avg_heart_rate'] < 60 else ""
    
    st.markdown(f"""
    <div class="data-card hover-zoom">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h4 style="margin: 0;">Average Heart Rate</h4>
            <div class="status-indicator {hr_status}"></div>
        </div>
        <div class="metric-value {animation_class}">{metrics['avg_heart_rate']:.1f} <span style="font-size: 16px;">bpm</span></div>
        <div class="metric-label">Normal range: 60-100 bpm</div>
        <div style="height: 5px; width: 100%; background-color: rgba(74, 86, 226, 0.2); border-radius: 3px; margin-top: 10px;">
            <div style="height: 100%; width: {min(100, metrics['avg_heart_rate']/1.2)}%; background-color: #4a56e2; border-radius: 3px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with metric_col3:
    # Add animation if SpO2 is below healthy range
    animation_class = "pulse-animation" if metrics['avg_spo2'] < 95 else ""
    
    st.markdown(f"""
    <div class="data-card hover-zoom">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h4 style="margin: 0;">Average SpO2</h4>
            <div class="status-indicator {spo2_status}"></div>
        </div>
        <div class="metric-value {animation_class}">{metrics['avg_spo2']:.1f}<span style="font-size: 16px;">%</span></div>
        <div class="metric-label">Healthy: ≥95%</div>
        <div style="height: 5px; width: 100%; background-color: rgba(74, 86, 226, 0.2); border-radius: 3px; margin-top: 10px;">
            <div style="height: 100%; width: {metrics['avg_spo2']}%; background-color: {'#4CAF50' if metrics['avg_spo2'] >= 95 else '#FFC107' if metrics['avg_spo2'] >= 92 else '#F44336'}; border-radius: 3px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with metric_col4:
    # Always pulse animation for high stress
    animation_class = "pulse-animation" if metrics['high_stress_count'] > 0 else ""
    
    st.markdown(f"""
    <div class="data-card hover-zoom">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h4 style="margin: 0;">High Stress Employees</h4>
            <div class="status-indicator {stress_status}"></div>
        </div>
        <div class="metric-value {animation_class}">{metrics['high_stress_count']}</div>
        <div class="metric-label" style="color: {'#F44336' if metrics['high_stress_percent'] > 20 else '#FFC107' if metrics['high_stress_percent'] > 10 else '#c0c0c0'};">
            {metrics['high_stress_percent']:.1f}% of total
        </div>
        <div style="height: 5px; width: 100%; background-color: rgba(74, 86, 226, 0.2); border-radius: 3px; margin-top: 10px;">
            <div style="height: 100%; width: {metrics['high_stress_percent']}%; background-color: {'#F44336' if metrics['high_stress_percent'] > 20 else '#FFC107' if metrics['high_stress_percent'] > 10 else '#4CAF50'}; border-radius: 3px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Create tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["Department Analysis", "Employee Details", "Comparative Insights", "Wellness Assistant"])

with tab1:
    # Department stress overview
    st.markdown("### Department Stress Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(plot_department_stress(df), use_container_width=True)
    
    with col2:
        st.plotly_chart(plot_mood_distribution(filtered_df, selected_department), use_container_width=True)
    
    # HR and SpO2 distributions
    st.markdown("### Health Metrics Distribution")
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(plot_heart_rate_distribution(filtered_df, selected_department), use_container_width=True)
    
    with col2:
        st.plotly_chart(plot_spo2_distribution(filtered_df, selected_department), use_container_width=True)
    
    # Department ranking table
    st.markdown("### Department Wellness Rankings")
    dept_rankings = get_department_rankings(df)
    st.dataframe(
        dept_rankings,
        use_container_width=True,
        hide_index=False,
        column_config={
            "Department": st.column_config.TextColumn("Department"),
            "Avg Stress": st.column_config.NumberColumn("Avg Stress", format="%.1f"),
            "Avg HR": st.column_config.NumberColumn("Avg HR", format="%.1f bpm"),
            "Avg SpO2": st.column_config.NumberColumn("Avg SpO2", format="%.1f%%"),
            "Count": st.column_config.NumberColumn("Employee Count")
        }
    )

with tab2:
    # Individual employee metrics
    st.markdown("### Employee Health Status")
    
    # Quick stats with gauge charts
    if selected_department != 'All Departments':
        st.markdown(f"#### Key Metrics for {selected_department}")
    else:
        st.markdown("#### Overall Key Metrics")
    
    gauge_col1, gauge_col2, gauge_col3 = st.columns(3)
    
    with gauge_col1:
        avg_hr = filtered_df['heart_rate'].mean()
        st.plotly_chart(
            create_gauge_chart(
                avg_hr, "Avg Heart Rate (bpm)", 
                40, 120, 
                (60, 100), (40, 60), (100, 120)
            ),
            use_container_width=True
        )
    
    with gauge_col2:
        avg_spo2 = filtered_df['spo2'].mean()
        st.plotly_chart(
            create_gauge_chart(
                avg_spo2, "Avg SpO2 (%)", 
                90, 100, 
                (95, 100), (92, 95), (90, 92)
            ),
            use_container_width=True
        )
    
    with gauge_col3:
        avg_stress = filtered_df['stress_score'].mean()
        st.plotly_chart(
            create_gauge_chart(
                avg_stress, "Avg Stress Score", 
                0, 100, 
                (0, 50), (50, 75), (75, 100)
            ),
            use_container_width=True
        )
    
    # Employee list with search
    st.markdown("### Employee List")
    search_term = st.text_input("Search by Employee ID or Name", "")
    
    if search_term:
        search_results = filtered_df[
            filtered_df['employee_id'].str.contains(search_term, case=False) | 
            filtered_df['name'].str.contains(search_term, case=False)
        ]
    else:
        search_results = filtered_df
    
    # Display employees with pagination
    employees_per_page = 10
    total_pages = (len(search_results) + employees_per_page - 1) // employees_per_page
    
    if len(search_results) > 0:
        # Only show slider if there's more than one page
        if total_pages > 1:
            page = st.slider("Page", 1, total_pages, 1)
        else:
            page = 1
            
        start_idx = (page - 1) * employees_per_page
        end_idx = min(start_idx + employees_per_page, len(search_results))
        
        displayed_employees = search_results.iloc[start_idx:end_idx]
        
        for _, employee in displayed_employees.iterrows():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                # Determine status indicators based on thresholds
                hr_status = "status-good" if employee['heart_rate'] < hr_threshold else "status-critical"
                spo2_status = "status-critical" if employee['spo2'] < spo2_threshold else "status-good"
                stress_status = "status-good" if employee['stress_score'] < stress_threshold else "status-critical"
                
                # Add pulse animation to elements that exceed thresholds
                hr_class = "pulse-animation" if employee['heart_rate'] >= hr_threshold else ""
                spo2_class = "pulse-animation" if employee['spo2'] < spo2_threshold else ""
                stress_class = "pulse-animation" if employee['stress_score'] >= stress_threshold else ""
                
                st.markdown(f"""
                <div class='employee-card neon-border'>
                    <strong class="glow-text">{employee['name']}</strong> ({employee['employee_id']})<br>
                    <small>{employee['department']} | Age: {employee['age']} | {employee['gender']}</small>
                    <div style="position: absolute; top: 10px; right: 10px;">
                        <span class="status-indicator {hr_status if employee['heart_rate'] > 100 else spo2_status if employee['spo2'] < 95 else stress_status if employee['stress_score'] > 70 else 'status-good'}"></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class='employee-card hover-zoom'>
                    <div class='metric-label'>Heart Rate</div>
                    <div class='metric-value {hr_class}'>{employee['heart_rate']} bpm</div>
                    <div class="status-indicator {hr_status}" style="display: inline-block;"></div>
                    <small>{" " * 5}Normal range: 60-100 bpm</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class='employee-card hover-zoom'>
                    <div class='metric-label'>SpO2</div>
                    <div class='metric-value {spo2_class}'>{employee['spo2']}%</div>
                    <div class="status-indicator {spo2_status}" style="display: inline-block;"></div>
                    <small>{" " * 5}Healthy: ≥95%</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class='employee-card hover-zoom'>
                    <div class='metric-label'>Mood</div>
                    <div class='metric-value'>{employee['mood']} {get_mood_emoji(employee['mood'])}</div>
                    <div class='metric-label {stress_class}'>Stress: <span class="glow-text">{employee['stress_score']}</span></div>
                    <div class="status-indicator {stress_status}" style="display: inline-block;"></div>
                </div>
                """, unsafe_allow_html=True)
        
        st.caption(f"Showing {start_idx+1}-{end_idx} of {len(search_results)} employees")
    else:
        st.info("No employees found matching your search criteria.")

with tab3:
    # Comparative insights
    st.markdown("### Department Health Comparison")
    st.plotly_chart(create_department_comparison_chart(df), use_container_width=True)
    
    # Custom analysis explanation
    st.markdown("### Stress Analysis Insights")
    
    # Calculate high-stress departments
    high_stress_depts = df.groupby('department')['stress_score'].mean().sort_values(ascending=False)
    highest_stress_dept = high_stress_depts.index[0]
    highest_stress_value = high_stress_depts.iloc[0]
    
    lowest_stress_dept = high_stress_depts.index[-1]
    lowest_stress_value = high_stress_depts.iloc[-1]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class='data-card'>
            <h4>🔍 Highest Stress Department</h4>
            <div class='metric-value'>{highest_stress_dept}</div>
            <div class='metric-label'>Average Stress Score: {highest_stress_value:.1f}</div>
            <br>
            <p>This department shows the highest average stress levels and might need immediate wellness interventions.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='data-card'>
            <h4>✅ Lowest Stress Department</h4>
            <div class='metric-value'>{lowest_stress_dept}</div>
            <div class='metric-label'>Average Stress Score: {lowest_stress_value:.1f}</div>
            <br>
            <p>This department shows the lowest average stress levels, potentially with good wellness practices that could be shared.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Correlation analysis
    stress_hr_corr = np.corrcoef(df['heart_rate'], df['stress_score'])[0, 1]
    stress_spo2_corr = np.corrcoef(df['spo2'], df['stress_score'])[0, 1]
    
    st.markdown("### Correlation Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class='data-card'>
            <h4>Heart Rate & Stress</h4>
            <div class='metric-value'>{stress_hr_corr:.2f}</div>
            <div class='metric-label'>Correlation Coefficient</div>
            <br>
            <p>A positive correlation indicates that higher heart rates are associated with higher stress levels.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='data-card'>
            <h4>SpO2 & Stress</h4>
            <div class='metric-value'>{stress_spo2_corr:.2f}</div>
            <div class='metric-label'>Correlation Coefficient</div>
            <br>
            <p>A negative correlation indicates that lower SpO2 levels are associated with higher stress levels.</p>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    # Initialize chatbot
    st.markdown("### Wellness Assistant")
    
    # Add custom CSS for enhanced chat interface
    st.markdown("""
    <style>
    .chat-container {
        border-radius: 12px;
        background-color: rgba(26, 31, 54, 0.8);
        padding: 20px;
        margin-bottom: 20px;
        height: 450px;
        overflow-y: auto;
        border: 1px solid #4a56e2;
        box-shadow: 0 0 15px rgba(74, 86, 226, 0.5), inset 0 0 10px rgba(74, 86, 226, 0.2);
        backdrop-filter: blur(10px);
        position: relative;
    }
    
    .chat-container::before {
        content: "";
        position: absolute;
        top: -5px;
        left: -5px;
        right: -5px;
        bottom: -5px;
        border-radius: 15px;
        background: linear-gradient(45deg, #4a56e2, transparent, #4a56e2, transparent);
        background-size: 400% 400%;
        opacity: 0.3;
        z-index: -1;
        animation: gradient-animation 15s ease infinite;
    }
    
    @keyframes gradient-animation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .user-message {
        background: linear-gradient(135deg, #4a56e2 0%, #3a46d2 100%);
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 3px 18px;
        margin: 8px 0;
        max-width: 70%;
        align-self: flex-end;
        margin-left: auto;
        margin-right: 10px;
        box-shadow: 0 2px 8px rgba(74, 86, 226, 0.4);
        position: relative;
        transition: all 0.3s ease;
        transform-origin: bottom right;
        animation: message-appear 0.3s ease-out forwards;
    }
    
    .user-message:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(74, 86, 226, 0.6);
    }
    
    .bot-message {
        background: linear-gradient(135deg, #2b325b 0%, #1a1f36 100%);
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 3px;
        margin: 8px 0;
        max-width: 70%;
        align-self: flex-start;
        margin-right: auto;
        margin-left: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        position: relative;
        transition: all 0.3s ease;
        transform-origin: bottom left;
        animation: message-appear 0.3s ease-out forwards;
        border-left: 2px solid #4a56e2;
    }
    
    .bot-message:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    @keyframes message-appear {
        0% { opacity: 0; transform: translateY(10px) scale(0.95); }
        100% { opacity: 1; transform: translateY(0) scale(1); }
    }
    
    .message-container {
        display: flex;
        flex-direction: column;
        margin-bottom: 12px;
        position: relative;
    }
    
    .timestamp {
        font-size: 10px;
        color: rgba(255, 255, 255, 0.5);
        margin-top: 4px;
        align-self: flex-end;
    }
    
    .typing-indicator {
        display: inline-block;
        padding: 8px 12px;
        background-color: rgba(43, 50, 91, 0.7);
        border-radius: 12px;
        margin-left: 10px;
    }
    
    .typing-indicator span {
        height: 8px;
        width: 8px;
        float: left;
        margin: 0 1px;
        background-color: #4a56e2;
        display: block;
        border-radius: 50%;
        opacity: 0.4;
    }
    
    .typing-indicator span:nth-of-type(1) {
        animation: typing 1s infinite 0.1s;
    }
    
    .typing-indicator span:nth-of-type(2) {
        animation: typing 1s infinite 0.3s;
    }
    
    .typing-indicator span:nth-of-type(3) {
        animation: typing 1s infinite 0.5s;
    }
    
    @keyframes typing {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-5px); }
        100% { transform: translateY(0px); }
    }
    
    /* Chat input styling */
    [data-testid="stForm"] {
        background-color: rgba(26, 31, 54, 0.7);
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        border: 1px solid #2b325b;
        transition: all 0.3s ease;
    }
    
    [data-testid="stForm"]:hover {
        border-color: #4a56e2;
    }
    
    /* Chat header */
    .chat-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(74, 86, 226, 0.3);
    }
    
    .chat-status {
        display: inline-block;
        width: 12px;
        height: 12px;
        background-color: #4CAF50;
        border-radius: 50%;
        margin-right: 10px;
        box-shadow: 0 0 8px #4CAF50;
        animation: blink 2s infinite;
    }
    
    @keyframes blink {
        0% { opacity: 0.4; }
        50% { opacity: 1; }
        100% { opacity: 0.4; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create a session state for chat history if it doesn't exist
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = WellnessChatbot(df)
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Update chatbot with latest data
    st.session_state.chatbot.update_data(df)
    
    # Display a futuristic chat header
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 15px; background: linear-gradient(90deg, rgba(26, 31, 54, 0.8) 0%, rgba(74, 86, 226, 0.4) 100%); padding: 10px 20px; border-radius: 10px; border-left: 3px solid #4a56e2;">
        <div class="chat-status"></div>
        <div>
            <div style="font-weight: bold; font-size: 16px;">Wellness AI Assistant</div>
            <div style="font-size: 12px; color: #c0c0c0;">Active | Connected to Employee Database</div>
        </div>
        <div style="margin-left: auto; display: flex; gap: 10px;">
            <div class="status-indicator status-good" title="System Status: Normal"></div>
            <div class="status-indicator status-good" title="Database Connected"></div>
            <div class="status-indicator status-good" title="AI Model Loaded"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Display chat messages with improved UI
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container" id="chat-container">', unsafe_allow_html=True)
        
        # Current timestamp for messages
        current_time = datetime.now().strftime("%H:%M")
        
        # If there's no history, show a welcome message
        if not st.session_state.chat_history:
            st.markdown(f"""
            <div class="message-container">
                <div class="bot-message">
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <div style="width: 24px; height: 24px; border-radius: 50%; background-color: #4a56e2; display: flex; justify-content: center; align-items: center; margin-right: 8px;">
                            <span style="color: white; font-weight: bold; font-size: 10px;">AI</span>
                        </div>
                        <div style="font-weight: bold; font-size: 14px;">Wellness Assistant</div>
                    </div>
                    Hello! I'm your Wellness Assistant. Ask me about departments, employees, or stress levels!
                    <div class="timestamp">{current_time}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display all messages in the chat history with enhanced UI
            for message in st.session_state.chat_history:
                if 'user' in message:
                    st.markdown(f"""
                    <div class="message-container">
                        <div class="user-message">
                            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                                <div style="font-weight: bold; font-size: 14px;">You</div>
                            </div>
                            {message["user"]}
                            <div class="timestamp">{current_time}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                if 'bot' in message:
                    st.markdown(f"""
                    <div class="message-container">
                        <div class="bot-message">
                            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                                <div style="width: 24px; height: 24px; border-radius: 50%; background-color: #4a56e2; display: flex; justify-content: center; align-items: center; margin-right: 8px;">
                                    <span style="color: white; font-weight: bold; font-size: 10px;">AI</span>
                                </div>
                                <div style="font-weight: bold; font-size: 14px;">Wellness Assistant</div>
                            </div>
                            {message["bot"]}
                            <div class="timestamp">{current_time}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Create input form
    with st.form(key='chat_form', clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input("Ask about employee wellness:", placeholder="Example: How is the Engineering department doing?", label_visibility="collapsed")
        with col2:
            submit_button = st.form_submit_button("Send")
    
    # Process form submission
    if submit_button and user_input:
        # Store user message
        st.session_state.chat_history.append({"user": user_input})
        
        # Get chatbot response
        response = st.session_state.chatbot.respond(user_input)
        
        # Store bot response
        st.session_state.chat_history.append({"bot": response})
        
        # Rerun to update the interface
        st.rerun()
    
    # Add interactive example queries section with futuristic design
    st.markdown("""
    <div style="margin-top: 25px; padding: 15px; background: linear-gradient(90deg, rgba(26, 31, 54, 0.7) 0%, rgba(43, 50, 91, 0.7) 100%); border-radius: 10px; border: 1px solid #2b325b; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);">
        <h3 style="margin-top: 0; margin-bottom: 15px; color: white; font-size: 18px; display: flex; align-items: center;">
            <span style="display: inline-block; width: 24px; height: 24px; background-color: #4a56e2; border-radius: 50%; margin-right: 10px; text-align: center; line-height: 24px; font-size: 14px;">💡</span>
            Suggested Queries
        </h3>
        <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 10px;">
            <div style="background: linear-gradient(135deg, rgba(74, 86, 226, 0.3) 0%, rgba(43, 50, 91, 0.3) 100%); padding: 8px 15px; border-radius: 20px; cursor: pointer; transition: all 0.2s ease; border: 1px solid rgba(74, 86, 226, 0.5); display: inline-block; margin: 5px 0;">Which department has the highest stress?</div>
            <div style="background: linear-gradient(135deg, rgba(74, 86, 226, 0.3) 0%, rgba(43, 50, 91, 0.3) 100%); padding: 8px 15px; border-radius: 20px; cursor: pointer; transition: all 0.2s ease; border: 1px solid rgba(74, 86, 226, 0.5); display: inline-block; margin: 5px 0;">How is the Engineering department?</div>
            <div style="background: linear-gradient(135deg, rgba(74, 86, 226, 0.3) 0%, rgba(43, 50, 91, 0.3) 100%); padding: 8px 15px; border-radius: 20px; cursor: pointer; transition: all 0.2s ease; border: 1px solid rgba(74, 86, 226, 0.5); display: inline-block; margin: 5px 0;">Show me all departments</div>
            <div style="background: linear-gradient(135deg, rgba(74, 86, 226, 0.3) 0%, rgba(43, 50, 91, 0.3) 100%); padding: 8px 15px; border-radius: 20px; cursor: pointer; transition: all 0.2s ease; border: 1px solid rgba(74, 86, 226, 0.5); display: inline-block; margin: 5px 0;">Tell me about employee EMP001</div>
        </div>
        
        <div style="display: flex; flex-wrap: wrap; gap: 10px;">
            <div class="query-category" style="flex: 1;">
                <div style="font-weight: bold; font-size: 14px; color: #4a56e2; margin-bottom: 8px; border-bottom: 1px solid rgba(74, 86, 226, 0.3); padding-bottom: 5px;">
                    <span style="display: inline-block; width: 18px; height: 18px; background-color: rgba(74, 86, 226, 0.3); border-radius: 50%; margin-right: 5px; text-align: center; line-height: 18px; font-size: 10px;">🔍</span>
                    Department Queries
                </div>
                <ul style="list-style-type: none; padding-left: 10px; margin: 0;">
                    <li style="margin-bottom: 8px; display: flex; align-items: center;">
                        <span style="color: #4a56e2; margin-right: 8px;">→</span>
                        <span>Show me the mood in Marketing</span>
                    </li>
                    <li style="margin-bottom: 8px; display: flex; align-items: center;">
                        <span style="color: #4a56e2; margin-right: 8px;">→</span>
                        <span>What's the health status of Sales?</span>
                    </li>
                    <li style="margin-bottom: 8px; display: flex; align-items: center;">
                        <span style="color: #4a56e2; margin-right: 8px;">→</span>
                        <span>Which team has the lowest SpO2?</span>
                    </li>
                </ul>
            </div>
            
            <div class="query-category" style="flex: 1;">
                <div style="font-weight: bold; font-size: 14px; color: #4a56e2; margin-bottom: 8px; border-bottom: 1px solid rgba(74, 86, 226, 0.3); padding-bottom: 5px;">
                    <span style="display: inline-block; width: 18px; height: 18px; background-color: rgba(74, 86, 226, 0.3); border-radius: 50%; margin-right: 5px; text-align: center; line-height: 18px; font-size: 10px;">👤</span>
                    Employee Queries
                </div>
                <ul style="list-style-type: none; padding-left: 10px; margin: 0;">
                    <li style="margin-bottom: 8px; display: flex; align-items: center;">
                        <span style="color: #4a56e2; margin-right: 8px;">→</span>
                        <span>What is John's stress level?</span>
                    </li>
                    <li style="margin-bottom: 8px; display: flex; align-items: center;">
                        <span style="color: #4a56e2; margin-right: 8px;">→</span>
                        <span>Who has the highest heart rate?</span>
                    </li>
                    <li style="margin-bottom: 8px; display: flex; align-items: center;">
                        <span style="color: #4a56e2; margin-right: 8px;">→</span>
                        <span>Compare EMP002 and EMP003</span>
                    </li>
                </ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("*This dashboard uses simulated data for demonstration purposes. In a production environment, it would connect to real-time health monitoring systems.*")

# Add a note about data refresh
st.markdown(f"Dashboard last refreshed at {current_time}")

if __name__ == "__main__":
    # This will be executed when the script runs directly
    pass
