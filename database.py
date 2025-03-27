import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database connection string from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL', '')

# Create SQLAlchemy engine and session
try:
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    Base = declarative_base()
    logger.info("Database connection established successfully")
except Exception as e:
    logger.error(f"Error connecting to database: {e}")
    raise

# Define database models
class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    department = Column(String(50), nullable=False)
    age = Column(Integer)
    gender = Column(String(10))
    
    def __repr__(self):
        return f"<Employee(id={self.id}, employee_id='{self.employee_id}', name='{self.name}')>"

class HealthMetric(Base):
    __tablename__ = 'health_metrics'
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(String(10), nullable=False)
    heart_rate = Column(Float)
    spo2 = Column(Float)
    stress_score = Column(Float)
    mood = Column(String(20))
    timestamp = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<HealthMetric(id={self.id}, employee_id='{self.employee_id}', timestamp='{self.timestamp}')>"

def initialize_database():
    """Create all database tables if they don't exist"""
    try:
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        return False

def insert_demo_data(df):
    """
    Insert demo data into the database
    
    Args:
        df: DataFrame with employee data
    
    Returns:
        True if successful, False otherwise
    """
    session = Session()
    try:
        # Extract unique employees
        employees_df = df[['employee_id', 'name', 'department', 'age', 'gender']].drop_duplicates()
        
        # Add employees
        for _, row in employees_df.iterrows():
            # Check if employee already exists
            existing_employee = session.query(Employee).filter_by(employee_id=row['employee_id']).first()
            if not existing_employee:
                employee = Employee(
                    employee_id=row['employee_id'],
                    name=row['name'],
                    department=row['department'],
                    age=row['age'],
                    gender=row['gender']
                )
                session.add(employee)
        
        # Add health metrics
        for _, row in df.iterrows():
            health_metric = HealthMetric(
                employee_id=row['employee_id'],
                heart_rate=row['heart_rate'],
                spo2=row['spo2'],
                stress_score=row['stress_score'],
                mood=row['mood'],
                timestamp=row['last_updated']
            )
            session.add(health_metric)
        
        session.commit()
        logger.info(f"Inserted {len(employees_df)} employees and {len(df)} health metrics")
        return True
    
    except Exception as e:
        if session:
            session.rollback()
        logger.error(f"Error inserting demo data: {e}")
        return False
    
    finally:
        if session:
            session.close()

def load_data_from_db():
    """
    Load employee health metrics from the database
    
    Returns:
        DataFrame with employee health metrics, or None if error
    """
    try:
        # Query to join employees and their latest health metrics
        query = """
        WITH latest_metrics AS (
            SELECT 
                employee_id,
                MAX(timestamp) as max_timestamp
            FROM 
                health_metrics
            GROUP BY 
                employee_id
        )
        SELECT 
            e.employee_id,
            e.name,
            e.department,
            e.age,
            e.gender,
            hm.heart_rate,
            hm.spo2,
            hm.stress_score,
            hm.mood,
            hm.timestamp as last_updated
        FROM 
            employees e
        JOIN 
            latest_metrics lm ON e.employee_id = lm.employee_id
        JOIN 
            health_metrics hm ON e.employee_id = hm.employee_id AND lm.max_timestamp = hm.timestamp
        ORDER BY 
            e.department, e.name
        """
        
        df = pd.read_sql(query, engine)
        logger.info(f"Loaded {len(df)} employee records from database")
        return df
    
    except Exception as e:
        logger.error(f"Error loading data from database: {e}")
        return None

def has_data():
    """Check if the database has any data"""
    session = Session()
    try:
        employee_count = session.query(Employee).count()
        metrics_count = session.query(HealthMetric).count()
        return employee_count > 0 and metrics_count > 0
    except Exception as e:
        logger.error(f"Error checking database data: {e}")
        return False
    finally:
        if session:
            session.close()