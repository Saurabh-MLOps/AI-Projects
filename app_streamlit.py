import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Saurabh's Wisdom Garden",
    page_icon="🌿",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .user-message {
        background-color: #6c5ce7;
        color: white;
    }
    .bot-message {
        background-color: #f0f0f0;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Gemini
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    st.error("❌ Gemini API key not found! Please make sure you have created a .env file with your API key.")
    st.stop()

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    st.success("✅ Gemini API configured successfully!")
except Exception as e:
    st.error(f"❌ Error configuring Gemini API: {str(e)}")
    st.stop()

# Title and description
st.title("🌿 Saurabh's Wisdom Garden")
st.markdown("### Your Personal Excel Data Assistant")

# Load Excel data
@st.cache_data
def load_excel_data():
    try:
        df = pd.read_excel('POC KPI v1.xlsb', engine='pyxlsb')
        st.success("✅ Excel file loaded successfully!")
        return df
    except Exception as e:
        st.error(f"❌ Error loading Excel file: {e}")
        return None

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

# Load the data
df = load_excel_data()

if df is not None:
    # Create tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["Chat Analysis", "Data Overview", "Visualizations"])
    
    with tab1:
        # Chat interface
        st.markdown("### Chat with your Excel Data")
        
        # Initialize chat history in session state if it doesn't exist
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">🧑‍💼 You: {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message bot-message">🤖 Assistant: {message["content"]}</div>', unsafe_allow_html=True)
        
        # Chat input
        user_question = st.text_input("Ask a question about your Excel data:", key="user_input")
        
        if user_question:
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            
            # Show user message
            st.markdown(f'<div class="chat-message user-message">🧑‍💼 You: {user_question}</div>', unsafe_allow_html=True)
            
            with st.spinner("🤔 Analyzing your question..."):
                try:
                    # Get context and generate response
                    excel_context = get_excel_context(df)
                    prompt = f"""You are an AI assistant helping analyze an Excel file. Here is the context about the data:

{excel_context}

User question: {user_question}

Please provide a detailed and helpful answer based on the Excel data. If the question requires specific calculations or analysis, explain your reasoning and show the relevant data points."""
                    
                    response = model.generate_content(prompt)
                    
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                    
                    # Show assistant message
                    st.markdown(f'<div class="chat-message bot-message">🤖 Assistant: {response.text}</div>', unsafe_allow_html=True)
                except Exception as e:
                    error_message = f"Error generating response: {str(e)}"
                    st.error(error_message)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_message})
    
    with tab2:
        st.markdown("### Data Overview")
        # Show basic information about the dataset
        st.write("#### Dataset Information")
        st.write(f"- Number of rows: {len(df)}")
        st.write(f"- Number of columns: {len(df.columns)}")
        
        # Show sample data
        st.write("#### Sample Data")
        st.dataframe(df.head(), use_container_width=True)
        
        # Show column information
        st.write("#### Column Information")
        col_info = pd.DataFrame({
            'Data Type': df.dtypes,
            'Non-Null Count': df.count(),
            'Null Count': df.isnull().sum()
        })
        st.dataframe(col_info, use_container_width=True)
    
    with tab3:
        st.markdown("### Data Visualizations")
        
        # Get numeric columns for visualization
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        
        if len(numeric_cols) > 0:
            # Column selection for visualization
            selected_col = st.selectbox("Select a column to visualize:", numeric_cols)
            
            # Create visualization
            fig = px.histogram(df, x=selected_col, title=f"Distribution of {selected_col}")
            st.plotly_chart(fig, use_container_width=True)
            
            # Show basic statistics
            st.write("#### Basic Statistics")
            st.dataframe(df[selected_col].describe(), use_container_width=True)
        else:
            st.info("No numeric columns available for visualization.")

else:
    st.error("Failed to load the Excel file. Please check if the file exists and is accessible.")