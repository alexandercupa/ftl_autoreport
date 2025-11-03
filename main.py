import os
import json
from flask import Flask, jsonify
from flask_cors import CORS
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv("id.env")

app = Flask(_name_)
CORS(app)

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

from flask import Flask, request, jsonify

@app.route("/api/sales", methods=["GET"])
def get_sales_data():
    # Mendapatkan data dari Google Sheets
    result = sheet.values().get(spreadsheetId=SHEET_ID, range=SHEET_NAME).execute()
    values = result.get('values', [])

    if not values:
        return jsonify({"error": "No data found"}), 404

    # Ambil baris pertama sebagai header (keys)
    headers = values[0]

    # Buat list of dictionaries, dimana key adalah header dan value adalah baris-baris berikutnya
    data = []
    for row in values[1:]:
        row_data = {headers[i]: row[i] if i < len(row) else None for i in range(len(headers))}
        data.append(row_data)

    # Kembalikan data dalam format JSON
    return jsonify(data)


@app.route("/api/sales/search", methods=["GET"])
def search_sales_by_name():
    # Ambil parameter 'name' dari query string
    name = request.args.get('name')
    
    if not name:
        return jsonify({"error": "Name parameter is required"}), 400

    # Mendapatkan data dari Google Sheets
    result = sheet.values().get(spreadsheetId=SHEET_ID, range=SHEET_NAME).execute()
    values = result.get('values', [])

    if not values:
        return jsonify({"error": "No data found"}), 404

    # Ambil baris pertama sebagai header (keys)
    headers = values[0]

    # Filter data berdasarkan 'name' yang diberikan
    filtered_data = []
    for row in values[1:]:
        row_data = {headers[i]: row[i] if i < len(row) else None for i in range(len(headers))}
        if row_data.get("NAMA") == name:
            filtered_data.append(row_data)

    # Jika tidak ada data yang cocok
    if not filtered_data:
        return jsonify({"message": f"No data found for name: {name}"}), 404

    # Kembalikan data dalam format JSON
    return jsonify(filtered_data)

@app.route("/api/sales/search", methods=["GET"])
def search_sales_by_name_and_report():
    # Ambil parameter 'name' dan 'report_name' dari query string
    name = request.args.get('name')
    report_name = request.args.get('report_name')

    if not name or not report_name:
        return jsonify({"error": "Both 'name' and 'report_name' parameters are required"}), 400

    # Mendapatkan data dari Google Sheets
    result = sheet.values().get(spreadsheetId=SHEET_ID, range=SHEET_NAME).execute()
    values = result.get('values', [])

    if not values:
        return jsonify({"error": "No data found"}), 404

    # Ambil baris pertama sebagai header (keys)
    headers = values[0]

    # Filter data berdasarkan 'name' dan 'report_name' yang diberikan
    filtered_data = []
    for row in values[1:]:
        row_data = {headers[i]: row[i] if i < len(row) else None for i in range(len(headers))}
        if row_data.get("NAME") == name and row_data.get("REPORT_NAME") == report_name:
            filtered_data.append(row_data)

    # Jika tidak ada data yang cocok
    if not filtered_data:
        return jsonify({"message": f"No data found for name: {name} and report: {report_name}"}), 404

    # Kembalikan data dalam format JSON
    return jsonify(filtered_data)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Backend Running", "sheet": SHEET_NAME})

if _name_ == "_main_":
    app.run(host="0.0.0.0", port=5000)
