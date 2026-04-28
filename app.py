"""
app.py — Flask backend for VoteWise.

All routes for the VoteWise Election Education Assistant application.
Contains exception handling, input validation, and Gemini AI integration.
"""

from flask import Flask, jsonify, request, abort, render_template_string, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_compress import Compress
from werkzeug.exceptions import HTTPException
import os
import requests

from config import Config
from data import ELECTION_TIMELINE, STATE_ELECTIONS, VOTER_DOCUMENTS, VOTER_RIGHTS, FAQ_DATA, CONCIERGE_FALLBACKS
from helpers import check_voter_eligibility, get_document_checklist

# Application setup
app = Flask(__name__, static_folder="static", static_url_path="")
app.config.from_object(Config)

# Enable CORS, Ratelimiting, and Compression
CORS(app)
Compress(app)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[Config.RATE_LIMIT],
    storage_uri=Config.RATE_LIMIT_STORAGE
)

@app.after_request
def add_security_headers(response):
    """Inject security headers into every response."""
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' https://www.googletagmanager.com https://maps.googleapis.com https://cdn.jsdelivr.net 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https://www.google-analytics.com; "
        "connect-src 'self' https://generativelanguage.googleapis.com https://translation.googleapis.com https://www.google-analytics.com;"
    )
    return response

class InvalidInputError(ValueError):
    """Raised when input validation fails."""
    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(f"Invalid {field}: {message}")

@app.errorhandler(InvalidInputError)
def handle_invalid_input(error):
    """Error handler for input validation."""
    response = {"error": "Invalid Input", "field": error.field, "message": str(error)}
    return jsonify(response), 400

@app.errorhandler(Exception)
def handle_general_exception(error):
    """Fallback error handler."""
    if isinstance(error, HTTPException):
        return jsonify({"error": error.description}), error.code
    return jsonify({"error": "An unexpected error occurred."}), 500

@app.route("/")
def serve_index():
    """Serve the single-page application (PWA)."""
    return app.send_static_file("index.html")

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint for Docker and readiness probes."""
    return jsonify({"status": "healthy", "version": Config.VERSION}), 200

@app.route("/api/timeline", methods=["GET"])
def get_timeline():
    """Returns the full election process timeline."""
    return jsonify(ELECTION_TIMELINE), 200

@app.route("/api/states", methods=["GET"])
def get_all_states():
    """Returns a list of all supported states with election info."""
    return jsonify(STATE_ELECTIONS), 200

@app.route("/api/state/<state_id>", methods=["GET"])
def get_state(state_id):
    """
    Returns state election details.
    Raises InvalidInputError if state_id is invalid.
    """
    if state_id not in STATE_ELECTIONS:
        raise InvalidInputError("state_id", f"State '{state_id}' is not supported.")
    return jsonify(STATE_ELECTIONS[state_id]), 200

@app.route("/api/documents", methods=["GET"])
def get_documents_checklist():
    """Returns the voter document checklist data."""
    return jsonify(VOTER_DOCUMENTS), 200

@app.route("/api/faq", methods=["GET"])
def get_faq_list():
    """Returns frequently asked questions and rights."""
    return jsonify({"faqs": FAQ_DATA, "rights": VOTER_RIGHTS}), 200

@app.route("/api/eligibility", methods=["POST"])
def check_eligibility():
    """
    Check voter eligibility based on age, citizenship, and residency.
    """
    data = request.get_json()
    if not data:
        raise InvalidInputError("json", "Missing JSON body.")
        
    try:
        age = int(data.get("age", 0))
    except ValueError:
        raise InvalidInputError("age", "Age must be an integer.")
        
    is_citizen = bool(data.get("is_citizen", False))
    is_resident = bool(data.get("is_resident", False))
    
    result = check_voter_eligibility(age, is_citizen, is_resident)
    return jsonify(result), 200

def _get_gemini_fallback(user_message: str):
    """Helper to return a fallback response if Gemini API fails or is missing."""
    msg_lower = user_message.lower()
    for fallback in CONCIERGE_FALLBACKS:
        if any(kw in msg_lower for kw in fallback["keywords"]):
            return fallback["response"]
    return "I recommend checking the official ECI website (eci.gov.in) or calling the 1950 Voter Helpline for accurate details."

@app.route("/api/concierge", methods=["POST"])
def use_concierge():
    """
    Gemini AI concierge for election questions.
    Validates input and falls back to keyword matching if API key missing.
    """
    data = request.get_json()
    if not data or "message" not in data:
        raise InvalidInputError("message", "Missing message field.")
        
    message = str(data["message"])
    if not message.strip():
        raise InvalidInputError("message", "Message cannot be empty.")
    if len(message) > Config.MAX_MESSAGE_LENGTH:
        raise InvalidInputError("message", f"Message exceeds {Config.MAX_MESSAGE_LENGTH} characters.")
        
    api_key = Config.GEMINI_API_KEY
    if not api_key:
        fallback_msg = _get_gemini_fallback(message)
        return jsonify({"reply": fallback_msg, "notice": "Offline Fallback Mode"}), 200
        
    # Build call to Google Gemini Model directly (REST API call payload approach)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{Config.GEMINI_MODEL}:generateContent?key={api_key}"
    
    system_prompt = (
        "You are VoteWise, an AI assistant that educates Indian citizens about the election process. "
        "You provide accurate, non-partisan information based on Election Commission of India (ECI) guidelines.\n"
        "Key facts: Form 6 for registration, age 18 on qualifying date, EPIC card needed, EVM has blue button, "
        "VVPAT 7 sec slip, NOTA available, Model Code of Conduct applies, 48 hours silence period, Polling 7 AM - 6 PM.\n"
        "Rules: Be concise (2-3 sentences max). Stay non-partisan. Cite ECI guidelines. Direct to eci.gov.in or 1950 if unsure. Use markdown for better formatting (like bolding key terms). When mentioning 'Form 6' or any registration form, format it as an HTML link to https://voters.eci.gov.in/ (e.g., <a href='https://voters.eci.gov.in/' target='_blank'>Form 6</a>)."
    )
    
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": system_prompt + "\n\nUser Question: " + message}]
            }
        ],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 200}
    }
    
    try:
        req = requests.post(url, json=payload, timeout=Config.GEMINI_TIMEOUT)
        if req.status_code == 200:
            gemini_res = req.json()
            reply = gemini_res.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            if not reply:
                reply = _get_gemini_fallback(message)
            return jsonify({"reply": reply.strip()}), 200
        else:
            return jsonify({"reply": _get_gemini_fallback(message)}), 200
    except Exception as e:
        return jsonify({"reply": _get_gemini_fallback(message)}), 200

@app.route("/api/translate", methods=["POST"])
def translate_text():
    """Google Cloud Translation API Integration."""
    data = request.get_json()
    if not data or "text" not in data:
        raise InvalidInputError("text", "Missing text field.")
        
    api_key = Config.GOOGLE_TRANSLATE_API_KEY
    if not api_key:
        return jsonify({"translated": data["text"] + " (Hindi Mode Simulated)"}), 200
        
    try:
        url = f"https://translation.googleapis.com/language/translate/v2?key={api_key}"
        payload = {
            "q": data["text"],
            "target": data.get("target", "hi")
        }
        res = requests.post(url, json=payload, timeout=5)
        if res.status_code == 200:
            translated = res.json()["data"]["translations"][0]["translatedText"]
            return jsonify({"translated": translated}), 200
        else:
            return jsonify({"translated": data["text"] + " (Hindi Mode Simulated)"}), 200
    except Exception:
        return jsonify({"translated": data["text"] + " (Hindi Mode Simulated)"}), 200

@app.route("/api/save-feedback", methods=["POST"])
def save_feedback():
    """Mock saving user experience to Firebase."""
    data = request.get_json()
    if not data or "rating" not in data:
        raise InvalidInputError("rating", "Missing rating.")
    
    rating = int(data.get("rating", 0))
    if rating < 1 or rating > 5:
        raise InvalidInputError("rating", "Rating must be between 1 and 5.")
        
    return jsonify({"status": "success", "message": "Feedback saved."}), 200

@app.route("/api/firebase-config", methods=["GET"])
def get_firebase_config():
    """Firebase config retrieval for client side (anonymous auth feature)."""
    return jsonify({"apiKey": Config.FIREBASE_API_KEY}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(Config.PORT), debug=Config.DEBUG)
