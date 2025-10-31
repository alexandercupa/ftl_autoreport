from flask import Flask, jsonify, request
import os
import pandas as pd
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- STEP 1: Setup Flask ---
app = Flask(__name__)

# --- STEP 2: Load environment variables ---
load_dotenv("id.env")

SHEET_ID = os.getenv("SHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")

SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

# --- STEP 3: Function to load sheet ---
def load_sheet():
    result = sheet.values().get(
        spreadsheetId=SHEET_ID,
        range=f"{SHEET_NAME}!A1:Z100"
    ).execute()
    values = result.get('values', [])
    if not values:
        return None
    headers = values[0]
    data = values[1:]
    df = pd.DataFrame(data, columns=headers)
    return df

# --- STEP 4: Routes ---
@app.route("/")
def home():
    return jsonify({"status": "ok", "message": "FTL Dashboard API is running."})

@app.route("/sales", methods=["GET"])
def get_all_sales():
    df = load_sheet()
    if df is None:
        return jsonify({"error": "No data found"}), 404
    return jsonify(df.to_dict(orient="records"))

@app.route("/sales/<string:name>", methods=["GET"])
def get_sales_by_name(name):
    df = load_sheet()
    if df is None:
        return jsonify({"error": "No data found"}), 404
    row = df[df["NAMA"].str.lower() == name.lower()]
    if row.empty:
        return jsonify({"error": "Sales associate not found"}), 404
    return jsonify(row.to_dict(orient="records")[0])

# --- STEP 5: Run app ---
if __name__ == "__main__":
    app.run(debug=True)
