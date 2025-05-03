# %% [markdown]
# # AI Chatbot with Gemini and Excel Analysis
# 
# This notebook implements a chatbot that can analyze Excel data using Google's Gemini model.

# %%
# Install required packages
# !pip install pandas plotly google-generativeai pyxlsb

# %%
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import os
from IPython.display import display, HTML

# %%
# Initialize Gemini with API key
GOOGLE_API_KEY = "AIzaSyAAckLry3BDN0JWzL1JtyOSEImRtyupGeo"
genai.configure(api_key=GOOGLE_API_KEY)

# List available models
available_models = []
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        available_models.append(model.name)

print("Available models:")
for model in available_models:
    print(f"- {model}")

# Initialize the model (using the first available model)
model = genai.GenerativeModel(available_models[0])

# %%
def load_excel_data():
    try:
        # Create a dictionary to store all sheets
        excel_data = {}
        # Use ExcelFile to get sheet names
        excel = pd.ExcelFile('POC KPI v1.xlsb', engine='pyxlsb')
        sheet_names = excel.sheet_names
        
        # Load each sheet into the dictionary
        for sheet in sheet_names:
            excel_data[sheet] = pd.read_excel('POC KPI v1.xlsb', engine='pyxlsb', sheet_name=sheet)
        
        print("✅ Excel file loaded successfully!")
        return excel_data, sheet_names
    except Exception as e:
        print(f"❌ Error loading Excel file: {e}")
        return None, None

# %%
def get_excel_context(dfs, sheet_names, selected_sheet=None):
    """Generate a comprehensive context from the Excel data"""
    context = []
    
    if selected_sheet:
        # Generate context for specific sheet
        df = dfs[selected_sheet]
        context.append(f"\nAnalyzing sheet: {selected_sheet}")
        context.append(f"This sheet contains {len(df)} rows and {len(df.columns)} columns.")
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
    else:
        # Generate overview of all sheets
        context.append(f"The Excel file contains {len(sheet_names)} sheets:")
        for sheet in sheet_names:
            df = dfs[sheet]
            context.append(f"\nSheet: {sheet}")
            context.append(f"- Rows: {len(df)}")
            context.append(f"- Columns: {len(df.columns)}")
            context.append(f"- Column names: {', '.join(df.columns)}")
    
    return "\n".join(context)

# %%
def generate_visualizations(df, selected_sheet):
    """Generate relevant visualizations based on the data"""
    visualizations = []
    
    # Get numeric columns
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    
    if len(numeric_cols) > 0:
        # Create distribution plots for numeric columns
        for col in numeric_cols:
            fig = px.histogram(df, x=col, title=f"Distribution of {col} in {selected_sheet}")
            visualizations.append(fig)
        
        # Create correlation heatmap if there are multiple numeric columns
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            fig = px.imshow(corr_matrix, 
                          title=f"Correlation Heatmap for {selected_sheet}",
                          labels=dict(color="Correlation"))
            visualizations.append(fig)
    
    return visualizations

# %%
# Load the data
excel_data, sheet_names = load_excel_data()

if excel_data is not None:
    # Display available sheets
    print("Available sheets:")
    for sheet in sheet_names:
        print(f"- {sheet}")
    
    # Select a sheet to analyze
    selected_sheet = input("Enter the sheet name to analyze: ")
    
    if selected_sheet in sheet_names:
        # Get context and generate response
        excel_context = get_excel_context(excel_data, sheet_names, selected_sheet)
        
        # Generate visualizations
        visualizations = generate_visualizations(excel_data[selected_sheet], selected_sheet)
        
        # Display visualizations
        for fig in visualizations:
            fig.show()
        
        # Chat interface
        while True:
            user_question = input("\nAsk a question about your Excel data (or 'quit' to exit): ")
            
            if user_question.lower() == 'quit':
                break
            
            prompt = f"""You are an AI assistant helping analyze an Excel file. Here is the context about the data:

{excel_context}

User question: {user_question}

Please provide a detailed and helpful answer based on the Excel data. Follow these guidelines:
1. Provide direct analysis and insights without showing any code
2. Include relevant statistics and trends from the data
3. Explain your reasoning and assumptions clearly
4. If the question requires calculations, show the results directly
5. Reference specific data points when making conclusions
6. If trends or patterns are found, describe them in detail

You are currently analyzing the sheet named '{selected_sheet}'."""
            
            response = model.generate_content(prompt)
            print(f"\nAssistant: {response.text}")
    else:
        print(f"Sheet '{selected_sheet}' not found in the Excel file.")
else:
    print("Failed to load the Excel file. Please check if the file exists and is accessible.") 