import re
import nltk
import pandas as pd
import logging
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download necessary NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except Exception as e:
    logger.warning(f"NLTK download error: {e}")

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

class WellnessChatbot:
    def __init__(self, employee_data=None):
        """
        Initialize chatbot with employee data
        
        Args:
            employee_data: DataFrame with employee health metrics
        """
        self.data = employee_data
        self.chat_history = []
    
    def update_data(self, employee_data):
        """Update the employee data used by the chatbot"""
        self.data = employee_data
    
    def preprocess_text(self, text):
        """
        Preprocess the input text - tokenize, remove stop words, lemmatize
        
        Args:
            text: Input text to preprocess
            
        Returns:
            Preprocessed tokens
        """
        # Convert to lowercase
        text = text.lower()
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and punctuation
        stop_words = set(stopwords.words('english'))
        tokens = [token for token in tokens if token.isalnum() and token not in stop_words]
        
        # Lemmatize
        tokens = [lemmatizer.lemmatize(token) for token in tokens]
        
        return tokens
    
    def extract_entities(self, text):
        """
        Extract department or employee names from the query
        
        Args:
            text: User query
            
        Returns:
            A dictionary with extracted entities
        """
        entities = {}
        entities['department'] = None
        entities['employee_id'] = None
        entities['employee_name'] = None
        entities['query_type'] = None
        entities['intent'] = 'general'  # Default intent
        
        # Check if we have data
        if self.data is None:
            return entities
        
        # Extract department names
        departments = self.data['department'].unique()
        for dept in departments:
            if dept.lower() in text.lower():
                entities['department'] = dept
                entities['query_type'] = 'department'
                break
        
        # Extract employee IDs (format: EMPxxx)
        emp_id_match = re.search(r'(emp\d{3})', text.lower())
        if emp_id_match:
            emp_id = emp_id_match.group(1).upper()
            if not self.data[self.data['employee_id'] == emp_id].empty:
                entities['employee_id'] = emp_id
                entities['query_type'] = 'employee'
        
        # Extract employee names (e.g., "Employee X")
        for _, row in self.data.iterrows():
            if row['name'].lower() in text.lower():
                entities['employee_name'] = row['name']
                entities['employee_id'] = row['employee_id']
                entities['query_type'] = 'employee'
                break
        
        # Identify query intent
        mood_keywords = ['mood', 'feeling', 'stress', 'stressed', 'emotion']
        health_keywords = ['health', 'heart rate', 'heartrate', 'spo2', 'oxygen']
        
        if any(keyword in text.lower() for keyword in mood_keywords):
            entities['intent'] = 'mood'
        elif any(keyword in text.lower() for keyword in health_keywords):
            entities['intent'] = 'health'
        
        return entities
    
    def get_department_info(self, department_name, intent='general'):
        """
        Get information about a department
        
        Args:
            department_name: Name of the department
            intent: The type of information to return
            
        Returns:
            Response message
        """
        if self.data is None:
            return "I don't have any employee data to provide information."
        
        # Filter data for the department
        dept_data = self.data[self.data['department'] == department_name]
        
        if dept_data.empty:
            return f"I couldn't find any information about the {department_name} department."
        
        # Calculate department stats
        avg_heart_rate = dept_data['heart_rate'].mean()
        avg_spo2 = dept_data['spo2'].mean()
        avg_stress = dept_data['stress_score'].mean()
        employee_count = len(dept_data)
        
        # Get mood distribution
        mood_counts = dept_data['mood'].value_counts()
        most_common_mood = mood_counts.index[0]
        
        if intent == 'mood':
            response = f"In the {department_name} department, the average stress level is {avg_stress:.1f} out of 100. "
            response += f"The most common mood is '{most_common_mood}'. "
            
            high_stress_count = len(dept_data[dept_data['stress_score'] > 70])
            if high_stress_count > 0:
                high_stress_percent = (high_stress_count / employee_count) * 100
                response += f"{high_stress_count} employees ({high_stress_percent:.1f}%) show high stress levels."
            else:
                response += "No employees are showing high stress levels at the moment."
        
        elif intent == 'health':
            response = f"The {department_name} department has an average heart rate of {avg_heart_rate:.1f} bpm "
            response += f"and average SpO2 of {avg_spo2:.1f}%. "
            
            if avg_heart_rate > 85:
                response += "The heart rate is slightly elevated. "
            else:
                response += "Heart rate levels are normal. "
                
            if avg_spo2 < 95:
                response += "SpO2 levels could be improved."
            else:
                response += "SpO2 levels are healthy."
        
        else:  # general
            response = f"The {department_name} department has {employee_count} employees. "
            response += f"Average heart rate: {avg_heart_rate:.1f} bpm, Average SpO2: {avg_spo2:.1f}%, "
            response += f"Average stress level: {avg_stress:.1f}/100. "
            response += f"The most common mood is '{most_common_mood}'."
        
        return response
    
    def get_employee_info(self, employee_id=None, employee_name=None, intent='general'):
        """
        Get information about an employee
        
        Args:
            employee_id: ID of the employee
            employee_name: Name of the employee
            intent: The type of information to return
            
        Returns:
            Response message
        """
        if self.data is None:
            return "I don't have any employee data to provide information."
        
        # Filter data for the employee
        if employee_id:
            employee_data = self.data[self.data['employee_id'] == employee_id]
        elif employee_name:
            employee_data = self.data[self.data['name'] == employee_name]
        else:
            return "I need an employee ID or name to provide information."
        
        if employee_data.empty:
            return "I couldn't find any information about this employee."
        
        # Get employee info
        employee = employee_data.iloc[0]
        name = employee['name']
        dept = employee['department']
        heart_rate = employee['heart_rate']
        spo2 = employee['spo2']
        stress = employee['stress_score']
        mood = employee['mood']
        
        if intent == 'mood':
            response = f"{name} is currently in a '{mood}' mood with a stress level of {stress:.1f}/100. "
            
            if stress > 70:
                response += "This is a high stress level. Consider checking in with them."
            elif stress > 50:
                response += "This is a moderate stress level."
            else:
                response += "This is a low stress level, which is good."
        
        elif intent == 'health':
            response = f"{name} has a heart rate of {heart_rate} bpm and SpO2 of {spo2}%. "
            
            if heart_rate > 100:
                response += "Their heart rate is above the normal range. "
            elif heart_rate < 60:
                response += "Their heart rate is below the normal range. "
            else:
                response += "Their heart rate is within the normal range. "
                
            if spo2 < 95:
                response += "Their SpO2 level is below the recommended level."
            else:
                response += "Their SpO2 level is good."
        
        else:  # general
            response = f"{name} (ID: {employee['employee_id']}) works in the {dept} department. "
            response += f"Heart rate: {heart_rate} bpm, SpO2: {spo2}%, Stress level: {stress:.1f}/100. "
            response += f"Current mood: {mood}."
        
        return response
    
    def get_department_summary(self):
        """Get a summary of all departments"""
        if self.data is None:
            return "I don't have any employee data to provide information."
        
        dept_stats = self.data.groupby('department').agg({
            'employee_id': 'count',
            'stress_score': 'mean'
        }).reset_index()
        
        dept_stats.columns = ['Department', 'Employee Count', 'Avg Stress']
        dept_stats = dept_stats.sort_values('Avg Stress', ascending=True)
        
        response = "Here's a summary of all departments, ordered by stress level (lowest first):\n"
        
        for _, row in dept_stats.iterrows():
            response += f"- {row['Department']}: {row['Employee Count']} employees, "
            response += f"Avg stress: {row['Avg Stress']:.1f}/100\n"
        
        highest_stress = dept_stats.iloc[-1]
        lowest_stress = dept_stats.iloc[0]
        
        response += f"\n{highest_stress['Department']} shows the highest stress levels, "
        response += f"while {lowest_stress['Department']} shows the lowest."
        
        return response
    
    def respond(self, query):
        """
        Generate a response to a user query
        
        Args:
            query: User's question
            
        Returns:
            Chatbot response
        """
        # Store in chat history
        self.chat_history.append({"user": query})
        
        # Check for empty query
        if not query or query.strip() == "":
            response = "Please ask me a question about employee wellness or department statistics."
            self.chat_history.append({"bot": response})
            return response
        
        # Check for basic greetings
        greetings = ['hi', 'hello', 'hey', 'greetings', 'howdy']
        if query.lower() in greetings or query.lower().startswith('hi ') or query.lower().startswith('hello '):
            response = "Hello! I'm the HR Wellness Assistant. How can I help you today?"
            self.chat_history.append({"bot": response})
            return response
        
        # Extract entities from the query
        entities = self.extract_entities(query)
        
        # Default intent if not identified
        intent = entities.get('intent', 'general')
        
        # Generate response based on query type
        if "department list" in query.lower() or "all departments" in query.lower():
            response = self.get_department_summary()
        
        elif entities['query_type'] == 'department' and entities['department'] is not None:
            response = self.get_department_info(entities['department'], intent)
        
        elif entities['query_type'] == 'employee':
            # Convert None values to empty strings to avoid type errors
            emp_id = entities['employee_id'] if entities['employee_id'] is not None else ""
            emp_name = entities['employee_name'] if entities['employee_name'] is not None else ""
            response = self.get_employee_info(emp_id, emp_name, intent)
        
        # Handle general questions
        elif any(keyword in query.lower() for keyword in ['highest stress', 'most stressed']):
            if self.data is None:
                response = "I don't have any employee data to provide information."
            else:
                dept_stats = self.data.groupby('department')['stress_score'].mean().sort_values(ascending=False)
                highest_dept = dept_stats.index[0]
                highest_value = dept_stats.iloc[0]
                response = f"The department with the highest stress level is {highest_dept} with an average stress score of {highest_value:.1f}/100."
        
        elif any(keyword in query.lower() for keyword in ['lowest stress', 'least stressed']):
            if self.data is None:
                response = "I don't have any employee data to provide information."
            else:
                dept_stats = self.data.groupby('department')['stress_score'].mean().sort_values(ascending=True)
                lowest_dept = dept_stats.index[0]
                lowest_value = dept_stats.iloc[0]
                response = f"The department with the lowest stress level is {lowest_dept} with an average stress score of {lowest_value:.1f}/100."
        
        else:
            # Default response for unrecognized queries
            response = "I'm not sure I understand your question. You can ask me about:"
            response += "\n- A specific department (e.g., 'How is the Engineering department doing?')"
            response += "\n- A specific employee (e.g., 'What's the mood of Employee 5?')"
            response += "\n- Department stress levels (e.g., 'Which department has the highest stress?')"
            response += "\n- All departments (e.g., 'Show me all departments')"
        
        # Store in chat history
        self.chat_history.append({"bot": response})
        return response