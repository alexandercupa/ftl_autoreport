import os
import json
from flask import Flask, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv("id.env")

app = Flask(__name__)

# Build credentials dictionary from .env
credentials_dict = {
    "type": os.getenv("GOOGLE_TYPE"),
    "project_id": os.getenv("GOOGLE_PROJECT_ID"),
    "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
    "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
    "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("GOOGLE_UNIVERSE_DOMAIN"),
}

# Create credentials object from JSON
creds = service_account.Credentials.from_service_account_info(credentials_dict)

# Connect to Google Sheets
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

SHEET_ID = os.getenv("SHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")

@app.route("/api/sales", methods=["GET"])
def get_sales_data():
    result = sheet.values().get(spreadsheetId=SHEET_ID, range=SHEET_NAME).execute()
    values = result.get('values', [])
    return jsonify(values)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Backend Running", "sheet": SHEET_NAME})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
