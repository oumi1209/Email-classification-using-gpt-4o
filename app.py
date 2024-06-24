import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
from googleapiclient.discovery import build
import base64
from bs4 import BeautifulSoup
import openai
from openai import AzureOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from langchain_openai import AzureChatOpenAI

# Constants
CLIENT_SECRET_FILE = 'client_secret.json'
TOKEN_PICKLE = 'token.pickle'
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
os.environ["AZURE_OPENAI_API_KEY"] = "your_azure_openai_api_key"
os.environ["AZURE_OPENAI_ENDPOINT"] = "your_azure_openai_endpoint"
os.environ["AZURE_OPENAI_API_VERSION"] = "2024-02-01"
os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"] = "gpt-4o"

# Function to authenticate and get Gmail service
def authenticate_gmail():
    creds = None
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            flow.redirect_uri = 'http://localhost:8080/'
            creds = flow.run_local_server(port=8080, open_browser=True)
            with open(TOKEN_PICKLE, 'wb') as token:
                pickle.dump(creds, token)
    return creds

def get_email_content(message):
    if 'parts' in message['payload']:
        for part in message['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            elif part['mimeType'] == 'text/html':
                html_content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                return BeautifulSoup(html_content, 'html.parser').text
    else:
        return base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
    return ""

def get_unread_messages(service, max_results):
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread", maxResults=max_results).execute()
    messages = results.get('messages', [])
    unread_messages = []

    if not messages:
        return "No unread messages found."

    for msg in messages:
        msg = service.users().messages().get(userId='me', id=msg['id']).execute()
        snippet = msg['snippet']
        headers = msg['payload']['headers']
        subject = sender = date = None
        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
            elif header['name'] == 'From':
                sender = header['value']
            elif header['name'] == 'Date':
                date = header['value']
        
        content = get_email_content(msg)
        
        unread_messages.append({
            'id': msg['id'],
            'subject': subject,
            'sender': sender,
            'date': date,
            'snippet': snippet,
            'content': content
        })
    
    return unread_messages

def classify_email(content):
    prompt_template = PromptTemplate(
        input_variables=["email_content"],
        template="Classify the following email content into one of these categories: Work, Personal, Spam.\nEmail Content: {email_content}\nCategory:"
    )
    llm = AzureChatOpenAI(azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"], api_version=os.environ["AZURE_OPENAI_API_VERSION"], azure_deployment=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"], api_key=os.environ["AZURE_OPENAI_API_KEY"])
    result = llm.invoke(prompt_template.format(email_content=content))

    return result.content

def logout():
    if os.path.exists(TOKEN_PICKLE):
        os.remove(TOKEN_PICKLE)
    st.cache_data.clear()
    st.rerun()

st.title("Gmail Email Classifier")

if 'selected_email' not in st.session_state:
    st.session_state.selected_email = None
if 'category' not in st.session_state:
    st.session_state.category = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

col1, col2 = st.sidebar.columns(2)

# Add elements to the columns
with col1:
    st.write("Login to your Gmail account:")

with col2:
    st.image('images.png', width=35)  # Specify width to make the image small

max_results = st.slider("Number of emails to fetch:", min_value=1, max_value=100, value=10)

if st.sidebar.button("Login"):
    st.sidebar.write("Logging in...")
    
    creds = authenticate_gmail()
    if creds:
        service = build('gmail', 'v1', credentials=creds)
        messages = get_unread_messages(service, max_results)

        if isinstance(messages, str):
            st.write(messages)
        else:
            st.session_state.messages = messages
            st.sidebar.success("Logged in successfully!")

if st.session_state.messages:
    st.write("Latest Unread Emails:")
    email_options = {f"{msg['subject']} - {msg['sender']}": msg for msg in st.session_state.messages}
    selected_email_key = st.selectbox("Select an email to classify:", list(email_options.keys()))

    if selected_email_key:
        selected_email = email_options[selected_email_key]
        st.session_state.selected_email = selected_email
        st.session_state.selected_content = selected_email['content']
        st.session_state.category = classify_email(st.session_state.selected_content)

        st.write(f'Email: {st.session_state.selected_content}')
        st.write(f"Email Category: **{st.session_state.category}**")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    logout()
