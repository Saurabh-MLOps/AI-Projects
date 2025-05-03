# AI Chatbot - Using Gemini Models

This project implements an intelligent chatbot that can analyze Excel data using Google's Gemini model. The chatbot can understand natural language questions about your Excel data and provide detailed insights, visualizations, and analysis.

## 🌟 Features

- **Excel Data Analysis**: Analyze data from Excel files with natural language queries
- **Interactive Visualizations**: Automatic generation of relevant charts and graphs
- **Multiple Sheet Support**: Work with multiple sheets in your Excel file
- **Smart Context Understanding**: The bot understands the structure and content of your data
- **Detailed Statistics**: Get comprehensive statistical analysis of your data
- **Natural Language Interface**: Ask questions in plain English about your data

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Google Cloud account with Gemini API access
- Excel file to analyze

### Installation

1. Clone this repository:
```bash
git clone <your-repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up your Google API key:
   - Get your API key from Google Cloud Console
   - Replace the API key in the code or set it as an environment variable

### Running the Application

1. Place your Excel file in the project directory
2. Run the Streamlit app:
```bash
streamlit run app_streamlit.py
```

## 💡 Example Usage

Here are some example questions you can ask the chatbot:

- "What are the key trends in the data?"
- "Show me the distribution of [column name]"
- "What is the correlation between [column1] and [column2]?"
- "What are the top 5 values in [column name]?"
- "Generate a summary of the data"

## 📊 Features in Detail

### Data Analysis
- Automatic detection of data types
- Statistical analysis of numeric columns
- Correlation analysis between variables
- Distribution analysis

### Visualizations
- Histograms for numeric columns
- Correlation heatmaps
- Interactive plots using Plotly
- Custom visualizations based on user queries

### Smart Features
- Context-aware responses
- Multi-sheet analysis
- Natural language understanding
- Detailed data summaries

## 🔧 Technical Details

The project uses:
- Google's Gemini AI model for natural language processing
- Pandas for data manipulation
- Plotly for interactive visualizations
- Streamlit for the web interface

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini team for the AI model
- Streamlit team for the web framework
- Pandas and Plotly communities for the data analysis tools

## 📞 Support

If you encounter any issues or have questions, please:
1. Check the existing issues
2. Create a new issue with a detailed description
3. Include any relevant error messages and steps to reproduce

---

Made with ❤️ by [Me](https://linktr.ee/saurabh_mlops)
