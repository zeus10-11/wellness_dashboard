import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Constants for health metrics
MIN_HEART_RATE = 60
MAX_HEART_RATE = 100
MIN_SPO2 = 92
MAX_SPO2 = 100

def generate_demo_data(n_employees=50):
    """
    Generate demo data for HR wellness dashboard
    
    Args:
        n_employees: Number of employees to generate data for
    
    Returns:
        DataFrame with employee health metrics
    """
    np.random.seed(42)  # For reproducible results
    
    departments = ['Engineering', 'Marketing', 'Finance', 'HR', 'Operations', 'Sales']
    
    # Generate random data
    data = {
        'employee_id': [f'EMP{i:03d}' for i in range(1, n_employees+1)],
        'name': [f'Employee {i}' for i in range(1, n_employees+1)],
        'department': np.random.choice(departments, size=n_employees),
        'age': np.random.randint(22, 60, size=n_employees),
        'gender': np.random.choice(['Male', 'Female'], size=n_employees),
        'heart_rate': np.random.randint(MIN_HEART_RATE, MAX_HEART_RATE, size=n_employees),
        'spo2': np.random.randint(MIN_SPO2, MAX_SPO2, size=n_employees),
    }
    
    df = pd.DataFrame(data)
    
    # Calculate stress level based on heart rate and SpO2
    # High heart rate and low SpO2 correlate with higher stress
    df['stress_score'] = calculate_stress_score(df['heart_rate'], df['spo2'])
    
    # Determine mood based on stress levels
    df['mood'] = df['stress_score'].apply(determine_mood)
    
    # Add timestamp for when data was last updated
    current_time = datetime.now()
    time_range = [current_time - timedelta(minutes=np.random.randint(5, 60)) for _ in range(n_employees)]
    df['last_updated'] = time_range
    
    return df

def calculate_stress_score(heart_rate, spo2):
    """
    Calculate stress score based on heart rate and SpO2
    
    Args:
        heart_rate: Heart rate values
        spo2: SpO2 values
    
    Returns:
        Stress score (0-100)
    """
    # Normalize heart rate (higher heart rate = higher stress)
    hr_normalized = (heart_rate - MIN_HEART_RATE) / (MAX_HEART_RATE - MIN_HEART_RATE)
    
    # Normalize SpO2 (lower SpO2 = higher stress)
    spo2_normalized = 1 - ((spo2 - MIN_SPO2) / (MAX_SPO2 - MIN_SPO2))
    
    # Combine factors with weights (heart rate has more impact on stress)
    stress_score = (hr_normalized * 0.7 + spo2_normalized * 0.3) * 100
    
    return stress_score.round(1)

def determine_mood(stress_score):
    """
    Determine mood based on stress score
    
    Args:
        stress_score: Stress score (0-100)
    
    Returns:
        Mood category
    """
    if stress_score < 30:
        return 'Calm'
    elif stress_score < 50:
        return 'Relaxed'
    elif stress_score < 70:
        return 'Moderate'
    elif stress_score < 85:
        return 'Tense'
    else:
        return 'Stressed'

def get_mood_emoji(mood):
    """
    Get emoji representation for mood
    
    Args:
        mood: Mood category
    
    Returns:
        Emoji representing mood
    """
    mood_map = {
        'Calm': '😌',
        'Relaxed': '🙂',
        'Moderate': '😐',
        'Tense': '😟',
        'Stressed': '😫'
    }
    return mood_map.get(mood, '❓')

def plot_department_stress(df):
    """
    Create a bar chart of average stress levels by department
    
    Args:
        df: DataFrame with employee data
    
    Returns:
        Plotly figure
    """
    dept_stress = df.groupby('department')['stress_score'].mean().reset_index()
    dept_stress = dept_stress.sort_values('stress_score', ascending=False)
    
    fig = px.bar(
        dept_stress, 
        x='department', 
        y='stress_score',
        title='Average Stress Levels by Department',
        labels={'stress_score': 'Stress Score', 'department': 'Department'},
        color='stress_score',
        color_continuous_scale='Bluered',
        template='plotly_dark'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(l=20, r=20, t=40, b=20),
        coloraxis_colorbar=dict(title="Stress Level")
    )
    
    return fig

def plot_heart_rate_distribution(df, department=None):
    """
    Create a histogram of heart rate distribution
    
    Args:
        df: DataFrame with employee data
        department: Optional filter by department
    
    Returns:
        Plotly figure
    """
    if department and department != 'All Departments':
        filtered_df = df[df['department'] == department]
        title = f'Heart Rate Distribution - {department}'
    else:
        filtered_df = df
        title = 'Heart Rate Distribution - All Departments'
    
    fig = px.histogram(
        filtered_df,
        x='heart_rate',
        nbins=20,
        color_discrete_sequence=['#4a56e2'],
        title=title,
        labels={'heart_rate': 'Heart Rate (bpm)'},
        template='plotly_dark'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(l=20, r=20, t=40, b=20),
        bargap=0.1
    )
    
    # Add reference lines for normal range
    fig.add_shape(
        type="line",
        x0=60, y0=0, x1=60, y1=1,
        yref="paper",
        line=dict(color="green", width=2, dash="dash")
    )
    fig.add_shape(
        type="line",
        x0=100, y0=0, x1=100, y1=1,
        yref="paper",
        line=dict(color="green", width=2, dash="dash")
    )
    
    fig.add_annotation(
        x=80, y=0.95,
        yref="paper",
        text="Normal Range (60-100 bpm)",
        showarrow=False,
        font=dict(size=12, color="green")
    )
    
    return fig

def plot_spo2_distribution(df, department=None):
    """
    Create a histogram of SpO2 distribution
    
    Args:
        df: DataFrame with employee data
        department: Optional filter by department
    
    Returns:
        Plotly figure
    """
    if department and department != 'All Departments':
        filtered_df = df[df['department'] == department]
        title = f'SpO2 Distribution - {department}'
    else:
        filtered_df = df
        title = 'SpO2 Distribution - All Departments'
    
    fig = px.histogram(
        filtered_df,
        x='spo2',
        nbins=10,
        color_discrete_sequence=['#00c3ff'],
        title=title,
        labels={'spo2': 'SpO2 (%)'},
        template='plotly_dark'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(l=20, r=20, t=40, b=20),
        bargap=0.1
    )
    
    # Add reference line for healthy threshold
    fig.add_shape(
        type="line",
        x0=95, y0=0, x1=95, y1=1,
        yref="paper",
        line=dict(color="green", width=2, dash="dash")
    )
    
    fig.add_annotation(
        x=97, y=0.95,
        yref="paper",
        text="Healthy (≥95%)",
        showarrow=False,
        font=dict(size=12, color="green")
    )
    
    return fig

def plot_mood_distribution(df, department=None):
    """
    Create a pie chart of mood distribution
    
    Args:
        df: DataFrame with employee data
        department: Optional filter by department
    
    Returns:
        Plotly figure
    """
    if department and department != 'All Departments':
        filtered_df = df[df['department'] == department]
        title = f'Mood Distribution - {department}'
    else:
        filtered_df = df
        title = 'Mood Distribution - All Departments'
    
    mood_counts = filtered_df['mood'].value_counts().reset_index()
    mood_counts.columns = ['mood', 'count']
    
    # Custom color mapping for moods
    colors = {
        'Calm': '#32CD32',      # Light Green
        'Relaxed': '#90EE90',   # Green
        'Moderate': '#FFD700',  # Gold
        'Tense': '#FFA500',     # Orange
        'Stressed': '#FF4500'   # Red-Orange
    }
    
    fig = px.pie(
        mood_counts,
        values='count',
        names='mood',
        title=title,
        color='mood',
        color_discrete_map=colors,
        template='plotly_dark'
    )
    
    fig.update_traces(
        textinfo='percent+label',
        pull=[0.05 if m == 'Stressed' else 0 for m in mood_counts['mood']]
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    
    return fig

def create_gauge_chart(value, title, min_val, max_val, good_range, warning_range, danger_range):
    """
    Create a gauge chart for displaying metrics
    
    Args:
        value: Current value
        title: Chart title
        min_val: Minimum value on gauge
        max_val: Maximum value on gauge
        good_range: (min, max) for good range
        warning_range: (min, max) for warning range
        danger_range: (min, max) for danger range
    
    Returns:
        Plotly figure
    """
    # Create steps for gauge colors
    steps = []
    
    if good_range:
        steps.append({
            'range': good_range,
            'color': '#32CD32'  # Green
        })
    
    if warning_range:
        steps.append({
            'range': warning_range,
            'color': '#FFD700'  # Yellow
        })
    
    if danger_range:
        steps.append({
            'range': danger_range, 
            'color': '#FF4500'  # Red
        })
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 24}},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickwidth': 1},
            'bar': {'color': '#4a56e2'},
            'steps': steps,
            'threshold': {
                'line': {'color': 'white', 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=200,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return fig

def create_department_comparison_chart(df):
    """
    Create a radar chart comparing departments across various metrics
    
    Args:
        df: DataFrame with employee data
    
    Returns:
        Plotly figure
    """
    # Calculate averages by department
    dept_metrics = df.groupby('department').agg({
        'heart_rate': 'mean',
        'spo2': 'mean',
        'stress_score': 'mean'
    }).reset_index()
    
    # Normalize values for radar chart
    dept_metrics['heart_rate_norm'] = (dept_metrics['heart_rate'] - MIN_HEART_RATE) / (MAX_HEART_RATE - MIN_HEART_RATE)
    dept_metrics['spo2_norm'] = (dept_metrics['spo2'] - MIN_SPO2) / (MAX_SPO2 - MIN_SPO2)
    dept_metrics['stress_norm'] = dept_metrics['stress_score'] / 100
    
    # For SpO2, higher is better, so invert the normalization for visualization
    dept_metrics['spo2_viz'] = 1 - dept_metrics['spo2_norm']
    
    fig = go.Figure()
    
    # Categories for radar chart
    categories = ['Heart Rate', 'SpO2', 'Stress']
    
    # Add traces for each department
    for i, dept in enumerate(dept_metrics['department']):
        fig.add_trace(go.Scatterpolar(
            r=[
                dept_metrics.loc[i, 'heart_rate_norm'],
                dept_metrics.loc[i, 'spo2_viz'],
                dept_metrics.loc[i, 'stress_norm']
            ],
            theta=categories,
            fill='toself',
            name=dept
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        title='Department Health Metrics Comparison',
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig
