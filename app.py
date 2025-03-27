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

# Page configuration
st.set_page_config(
    page_title="HR Wellness Dashboard",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for futuristic look
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #1a1f36 100%);
    }
    .css-1aumxhk {
        background-color: #1a1f36;
    }
    .data-card {
        border-radius: 10px;
        padding: 20px;
        background-color: #1a1f36;
        margin-bottom: 20px;
        border: 1px solid #2b325b;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #4a56e2;
    }
    .metric-label {
        font-size: 14px;
        color: #c0c0c0;
    }
    .employee-card {
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
        background-color: #1a1f36;
        border: 1px solid #2b325b;
    }
    .stDataFrame {
        border-radius: 10px !important;
        background-color: #1a1f36 !important;
    }
    h1, h2, h3 {
        color: #ffffff;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1f36;
        border-radius: 6px 6px 0px 0px;
        padding: 10px 20px;
        color: white;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4a56e2 !important;
        color: white !important;
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

# Department filter
departments = get_departments(df)
selected_department = st.sidebar.selectbox("Select Department", departments)

# Time range filter (for future implementation with time series data)
st.sidebar.markdown("## Time Range")
time_range = st.sidebar.radio(
    "Select Time Period",
    ["Today", "This Week", "This Month", "Quarter"],
    index=0
)

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
    if st.button("Reset Demo Data"):
        # This will clear the cache and reload the data
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("#### Data Refresh")
    refresh_rate = st.select_slider(
        "Auto Refresh Rate",
        options=["Off", "1 min", "5 min", "15 min", "30 min"],
        value="Off"
    )
    st.caption("In a production environment, this would automatically refresh data from sensors.")

# Refresh button
if st.sidebar.button("Refresh Data"):
    st.rerun()

# Main dashboard
# Top metrics row
st.markdown("## Health Metrics Overview")
metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

with metric_col1:
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.metric(
        label="Total Employees",
        value=metrics['total_employees'],
        delta=None
    )
    if selected_department != 'All Departments':
        st.caption(f"In {selected_department}")
    else:
        st.caption("Across all departments")
    st.markdown('</div>', unsafe_allow_html=True)

with metric_col2:
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.metric(
        label="Average Heart Rate",
        value=f"{metrics['avg_heart_rate']:.1f} bpm",
        delta=None
    )
    st.caption("Normal range: 60-100 bpm")
    st.markdown('</div>', unsafe_allow_html=True)

with metric_col3:
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.metric(
        label="Average SpO2",
        value=f"{metrics['avg_spo2']:.1f}%",
        delta=None
    )
    st.caption("Healthy: ≥95%")
    st.markdown('</div>', unsafe_allow_html=True)

with metric_col4:
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.metric(
        label="High Stress Employees",
        value=f"{metrics['high_stress_count']}",
        delta=f"{metrics['high_stress_percent']:.1f}% of total",
        delta_color="inverse"
    )
    st.caption("Stress score > 70")
    st.markdown('</div>', unsafe_allow_html=True)

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["Department Analysis", "Employee Details", "Comparative Insights"])

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
                st.markdown(f"""
                <div class='employee-card'>
                    <strong>{employee['name']}</strong> ({employee['employee_id']})<br>
                    <small>{employee['department']} | Age: {employee['age']} | {employee['gender']}</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class='employee-card'>
                    <div class='metric-label'>Heart Rate</div>
                    <div class='metric-value'>{employee['heart_rate']} bpm</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class='employee-card'>
                    <div class='metric-label'>SpO2</div>
                    <div class='metric-value'>{employee['spo2']}%</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class='employee-card'>
                    <div class='metric-label'>Mood</div>
                    <div class='metric-value'>{employee['mood']} {get_mood_emoji(employee['mood'])}</div>
                    <small>Stress: {employee['stress_score']}</small>
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

# Footer
st.markdown("---")
st.markdown("*This dashboard uses simulated data for demonstration purposes. In a production environment, it would connect to real-time health monitoring systems.*")

# Add a note about data refresh
st.markdown(f"Dashboard last refreshed at {current_time}")

if __name__ == "__main__":
    # This will be executed when the script runs directly
    pass
