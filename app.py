import os
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Load and process Excel file
def load_excel_data():
    try:
        df = pd.read_excel('POC KPI v1.xlsb', engine='pyxlsb')
        return df
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return None

# Initialize Gemini model
model = genai.GenerativeModel('gemini-pro')

def get_excel_context(df):
    """Generate a comprehensive context from the Excel data"""
    context = []
    
    # Add basic information
    context.append(f"The Excel file contains {len(df)} rows and {len(df.columns)} columns.")
    context.append(f"Column names: {', '.join(df.columns)}")
    
    # Add data types
    context.append("\nData types:")
    for col in df.columns:
        context.append(f"- {col}: {df[col].dtype}")
    
    # Add sample data
    context.append("\nSample data (first 5 rows):")
    context.append(df.head().to_string())
    
    # Add basic statistics for numeric columns
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    if len(numeric_cols) > 0:
        context.append("\nBasic statistics for numeric columns:")
        context.append(df[numeric_cols].describe().to_string())
    
    return "\n".join(context)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def process_query():
    try:
        data = request.json
        user_query = data.get('query', '')
        
        # Load Excel data
        df = load_excel_data()
        if df is None:
            return jsonify({'error': 'Failed to load Excel file'}), 500
        
        # Get comprehensive context
        excel_context = get_excel_context(df)
        
        # Prepare the prompt
        prompt = f"""You are an AI assistant helping analyze an Excel file. Here is the context about the data:

{excel_context}

User question: {user_query}

Please provide a detailed and helpful answer based on the Excel data. If the question requires specific calculations or analysis, explain your reasoning and show the relevant data points."""

        # Generate response using Gemini
        response = model.generate_content(prompt)
        
        return jsonify({'response': response.text})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)