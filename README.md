# Gmail Email Classifier

This project uses the Gmail API to fetch the latest emails from a user's Gmail account and classifies them into three categories: Work, Personal, and Spam using the Azure OpenAI GPT-4 model. The application is built using Streamlit for the frontend.

## Features
- **Login to Gmail**: Authenticate and connect to a Gmail account.
- **Fetch Emails**: Retrieve a specified number of unread emails.
- **Classify Emails**: Classify the content of each email into Work, Personal, or Spam.
- **Logout**: Safely logout and clear session data.

## Requirements
- Python 3.7+
- Streamlit
- Google API Client
- BeautifulSoup
- OpenAI API Key (Azure)
- LangChain

## Installation

1. **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/gmail-email-classifier.git
    cd gmail-email-classifier
    ```

2. **Set up a virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Add your credentials**
    - Place the `client_secret.json` file in the root directory. (tutorial: https://www.youtube.com/watch?v=brCkpzAD0gc)
    - Set environment variables for Azure OpenAI:
      ```bash
      export AZURE_OPENAI_API_KEY="your azure openai_api_key"
      export AZURE_OPENAI_ENDPOINT="your azure openai_endpoint"
      export AZURE_OPENAI_API_VERSION=""
      export AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=""
      ```

## Running the Application
```bash
streamlit run app.py
