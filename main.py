import os
import json
from functools import wraps
from flask import Flask, jsonify, request
from flask_cors import CORS
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv("id.env")

app = Flask(__name__)
CORS(app)

# --- SECURITY CONFIG ---
API_KEY = os.getenv("API_KEY", "JAKFQ25!!")     # Default fallback (optional)
REPORT_PASSWORD = os.getenv("REPORT_PASSWORD", "")

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("x-api-key")
        if not key or key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


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
SHEET_ID = os.getenv("SHEET_ID")
MASTER_RANGE = "MASTER_DATA!A:P"


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
@require_api_key
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
@require_api_key
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
@require_api_key
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
        "protected_routes": [
            "/api/leaderboard",
            "/api/sales",
            "/api/sales/search"
        ],
        "note": "All API routes require API_KEY"
    })


# ---------------------------------------------
# AUTH ROUTE (PUBLIC)
# ---------------------------------------------
@app.route("/api/auth", methods=["POST"])
def check_auth():
    data = request.get_json(silent=True) or {}
    pw = data.get("password", "").strip()

    if not pw:
        return jsonify({"ok": False, "msg": "Password kosong"}), 400

    if pw == REPORT_PASSWORD:
        return jsonify({"ok": True}), 200

    return jsonify({"ok": False, "msg": "Password salah"}), 401


# ---------------------------------------------
# RUN LOCAL (ignored on Vercel)
# ---------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
