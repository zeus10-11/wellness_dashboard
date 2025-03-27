import pandas as pd
import streamlit as st
from utils import generate_demo_data

def load_data():
    """
    Load and process the HR wellness data
    
    Returns:
        Processed DataFrame with employee health metrics
    """
    # In a real application, we would load data from a database or API
    # For this demo, we'll generate synthetic data
    df = generate_demo_data(n_employees=50)
    
    # Cache the data to improve performance
    return df

def get_departments(df):
    """
    Get list of unique departments
    
    Args:
        df: DataFrame with employee data
    
    Returns:
        List of department names
    """
    departments = df['department'].unique().tolist()
    departments.sort()
    return ['All Departments'] + departments

def filter_data(df, department=None):
    """
    Filter data based on selected department
    
    Args:
        df: DataFrame with employee data
        department: Department to filter by
    
    Returns:
        Filtered DataFrame
    """
    if department and department != 'All Departments':
        return df[df['department'] == department]
    return df

def get_summary_metrics(df):
    """
    Calculate summary metrics from the data
    
    Args:
        df: DataFrame with employee data
    
    Returns:
        Dictionary of summary metrics
    """
    metrics = {
        'total_employees': len(df),
        'avg_heart_rate': df['heart_rate'].mean(),
        'avg_spo2': df['spo2'].mean(),
        'avg_stress': df['stress_score'].mean(),
        'high_stress_count': len(df[df['stress_score'] > 70]),
        'high_stress_percent': len(df[df['stress_score'] > 70]) / len(df) * 100,
        'department_count': df['department'].nunique()
    }
    
    return metrics

def get_department_rankings(df):
    """
    Rank departments by average stress level
    
    Args:
        df: DataFrame with employee data
    
    Returns:
        DataFrame with department rankings
    """
    dept_ranks = df.groupby('department').agg({
        'stress_score': 'mean',
        'heart_rate': 'mean',
        'spo2': 'mean',
        'employee_id': 'count'
    }).reset_index()
    
    dept_ranks.columns = ['Department', 'Avg Stress', 'Avg HR', 'Avg SpO2', 'Count']
    dept_ranks = dept_ranks.sort_values('Avg Stress', ascending=True)
    dept_ranks = dept_ranks.reset_index(drop=True)
    dept_ranks.index = dept_ranks.index + 1  # Start indexing at 1
    
    return dept_ranks
