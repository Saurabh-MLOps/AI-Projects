import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import os

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
        background-color: #1a1a2e;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .user-message {
        background-color: #16213e;
        color: white;
    }
    .bot-message {
        background-color: #0f3460;
        color: white;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #e94560 !important;
    }
    .stMarkdown {
        color: white;
    }
    .stTextInput > div > div > input {
        background-color: #16213e;
        color: white;
        border: 1px solid #e94560;
    }
    .stTextInput > div > div > input:focus {
        border-color: #e94560;
        box-shadow: 0 0 0 1px #e94560;
    }
    .stButton > button {
        background-color: #e94560;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
    }
    .stButton > button:hover {
        background-color: #c1121f;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Gemini with direct API key
GOOGLE_API_KEY = "AIzaSyAAckLry3BDN0JWzL1JtyOSEImRtyupGeo"
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # List available models and their capabilities
    available_models = []
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            available_models.append(model.name)
    
    if not available_models:
        st.error("❌ No models available with generateContent capability")
        st.stop()
    
    # Add model selection dropdown
    st.sidebar.title("Model Settings")
    selected_model = st.sidebar.selectbox(
        "Select Gemini Model",
        available_models,
        index=0
    )
    
    # Initialize the selected model
    model = genai.GenerativeModel(selected_model)
    st.sidebar.success(f"✅ Using model: {selected_model}")
except Exception as e:
    st.error(f"❌ Error configuring Gemini API: {str(e)}")
    st.stop()

# Title and description
st.title("🌿 AI Chatbot")
st.markdown("### Your Personal Assistant")

# Load Excel data
@st.cache_data
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
        
        st.success("✅ Excel file loaded successfully!")
        return excel_data, sheet_names
    except Exception as e:
        st.error(f"❌ Error loading Excel file: {e}")
        return None, None

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

# Load the data
excel_data, sheet_names = load_excel_data()

if excel_data is not None:
    # Create tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["Chat Analysis", "Data Overview", "Visualizations"])
    
    with tab1:
        # Chat interface
        st.markdown("### Chat with your Excel Data")
        
        # Sheet selector
        selected_sheet = st.selectbox("Select a sheet to analyze:", sheet_names)
        
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
                    excel_context = get_excel_context(excel_data, sheet_names, selected_sheet)
                    
                    # Generate visualizations
                    visualizations = generate_visualizations(excel_data[selected_sheet], selected_sheet)
                    
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
                    
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                    
                    # Show assistant message
                    st.markdown(f'<div class="chat-message bot-message">🤖 Assistant: {response.text}</div>', unsafe_allow_html=True)
                    
                    # Display relevant visualizations
                    if visualizations:
                        st.markdown("### Relevant Visualizations")
                        for fig in visualizations:
                            st.plotly_chart(fig, use_container_width=True)
                
                except Exception as e:
                    error_message = f"Error generating response: {str(e)}"
                    st.error(error_message)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_message})
    
    with tab2:
        st.markdown("### Data Overview")
        # Sheet selector for overview
        overview_sheet = st.selectbox("Select a sheet:", sheet_names, key="overview_sheet")
        df = excel_data[overview_sheet]
        
        # Show basic information about the dataset
        st.write("#### Dataset Information")
        st.write(f"- Sheet name: {overview_sheet}")
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
        
        # Sheet selector for visualizations
        viz_sheet = st.selectbox("Select a sheet:", sheet_names, key="viz_sheet")
        df = excel_data[viz_sheet]
        
        # Get numeric columns for visualization
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        
        if len(numeric_cols) > 0:
            # Column selection for visualization
            selected_col = st.selectbox("Select a column to visualize:", numeric_cols)
            
            # Create visualization
            fig = px.histogram(df, x=selected_col, title=f"Distribution of {selected_col} in {viz_sheet}")
            st.plotly_chart(fig, use_container_width=True)
            
            # Show basic statistics
            st.write("#### Basic Statistics")
            st.dataframe(df[selected_col].describe(), use_container_width=True)
        else:
            st.info("No numeric columns available for visualization in this sheet.")

else:
    st.error("Failed to load the Excel file. Please check if the file exists and is accessible.") 