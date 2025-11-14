import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv("id.env")

app = Flask(__name__)
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

# Create credentials for Google Sheets API
creds = service_account.Credentials.from_service_account_info(credentials_dict)
service = build("sheets", "v4", credentials=creds)
sheet_api = service.spreadsheets()

# === CONFIG ===
SHEET_ID = os.getenv("SHEET_ID")  # Master sheet ID
MASTER_RANGE = "MASTER_DATA!A:P"  # Adjust if needed


# ---------------------------------------------
# UTIL: Fetch seluruh MASTER_DATA
# ---------------------------------------------
def fetch_master_data():
    result = (
        sheet_api.values()
        .get(spreadsheetId=SHEET_ID, range=MASTER_RANGE)
        .execute()
    )
    rows = result.get("values", [])

    if not rows or len(rows) < 2:
        return []

    header = rows[0]
    data = []

    for row in rows[1:]:
        row_dict = {}
        for i, key in enumerate(header):
            row_dict[key] = row[i] if i < len(row) else ""
        data.append(row_dict)

    return data


# ---------------------------------------------
# ROUTE: /api/sales  (ambil semua data)
# ---------------------------------------------
@app.route("/api/sales", methods=["GET"])
def get_sales_data():
    try:
        data = fetch_master_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------
# ROUTE: /api/sales/search  (filter by name)
# ---------------------------------------------
@app.route("/api/sales/search", methods=["GET"])
def search_sales_by_name():
    try:
        name = request.args.get("name", "").strip().upper()

        data = fetch_master_data()

        filtered = [
            row for row in data
            if row.get("NAMA", "").strip().upper() == name
        ]

        return jsonify(filtered)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------
# ROUTE: /api/leaderboard  (AMBIL OVERALL)
# ---------------------------------------------
@app.route("/api/leaderboard", methods=["GET"])
def leaderboard():
    try:
        data = fetch_master_data()

        lb = []

        for row in data:
            rep = row.get("REPORT_NAME", "")
            if "OVERALL" in rep.upper():
                nama = row.get("NAMA", "")
                percent_raw = row.get("SALES_PERCENTAGE", "0")

                # Convert "72,0%" → 72.0
                try:
                    percent_clean = float(
                        percent_raw.replace("%", "").replace(",", ".").strip()
                    )
                except:
                    percent_clean = 0

                lb.append({
                    "nama": nama,
                    "percentage": percent_clean
                })

        # sort descending
        lb_sorted = sorted(lb, key=lambda x: x["percentage"], reverse=True)

        return jsonify(lb_sorted)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------
# ROOT ROUTE
# ---------------------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "Backend Running",
        "sheet": "MASTER_DATA",
        "leaderboard": "/api/leaderboard",
        "sales": "/api/sales",
        "sales_search": "/api/sales/search"
    })


# ---------------------------------------------
# RUN LOCAL
# ---------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
