import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)
CORS(app)

# Build credentials dictionary from environment variables
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

creds = service_account.Credentials.from_service_account_info(credentials_dict)
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

SHEET_ID = os.getenv("SHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")

@app.route("/api/sales", methods=["GET"])
def get_sales_data():
    result = sheet.values().get(spreadsheetId=SHEET_ID, range=SHEET_NAME).execute()
    values = result.get('values', [])

    if not values:
        return jsonify({"error": "No data found"}), 404

    headers = values[0]
    data = [dict(zip(headers, row)) for row in values[1:]]

    return jsonify(data)


@app.route("/api/sales/search/name", methods=["GET"])
def search_sales_by_name():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Name parameter is required"}), 400

    result = sheet.values().get(spreadsheetId=SHEET_ID, range=SHEET_NAME).execute()
    values = result.get('values', [])

    if not values:
        return jsonify({"error": "No data found"}), 404

    headers = values[0]
    filtered_data = [dict(zip(headers, row)) for row in values[1:] if len(row) >= len(headers) and row[headers.index("NAMA")] == name]

    if not filtered_data:
        return jsonify({"message": f"No data found for name: {name}"}), 404

    return jsonify(filtered_data)


@app.route("/api/sales/search/full", methods=["GET"])
def search_sales_by_name_and_report():
    name = request.args.get('name')
    report_name = request.args.get('report_name')

    if not name or not report_name:
        return jsonify({"error": "Both 'name' and 'report_name' parameters are required"}), 400

    result = sheet.values().get(spreadsheetId=SHEET_ID, range=SHEET_NAME).execute()
    values = result.get('values', [])

    if not values:
        return jsonify({"error": "No data found"}), 404

    headers = values[0]
    filtered_data = [dict(zip(headers, row)) for row in values[1:] if row[headers.index("NAME")] == name and row[headers.index("REPORT_NAME")] == report_name]

    if not filtered_data:
        return jsonify({"message": f"No data found for name: {name} and report: {report_name}"}), 404

    return jsonify(filtered_data)


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Backend Running", "sheet": SHEET_NAME})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
