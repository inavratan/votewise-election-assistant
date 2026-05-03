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
from markupsafe import escape
import os
import requests
import logging
import google.generativeai as genai
from google.cloud import translate_v2 as translate
import google.cloud.logging
from google.cloud import firestore

from config import Config
from data import ELECTION_TIMELINE, STATE_ELECTIONS, VOTER_DOCUMENTS, VOTER_RIGHTS, FAQ_DATA, CONCIERGE_FALLBACKS
from helpers import check_voter_eligibility, get_document_checklist

# Application setup
app = Flask(__name__, static_folder="static", static_url_path="")
app.config.from_object(Config)

# Google Cloud Integrations
try:
    logging_client = google.cloud.logging.Client()
    logging_client.setup_logging()
    logging.info("Google Cloud Logging initialized.")
except Exception as e:
    print("Warning: Google Cloud Logging failed to initialize:", e)

try:
    db = firestore.Client()
    logging.info("Firestore Client initialized.")
except Exception as e:
    print("Warning: Firestore failed to initialize:", e)
    db = None

# Enable CORS, Ratelimiting, and Compression
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:8080", "https://votewise.app"]}})
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
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com https://cdn.jsdelivr.net https://*.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://*.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com https://*.gstatic.com; "
        "connect-src 'self' https://generativelanguage.googleapis.com https://www.google-analytics.com; "
        "img-src 'self' data:; "
        "frame-ancestors 'none';"
    )
    response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    # Add cache headers for static API data
    if request.path in ['/api/timeline', '/api/states', '/api/documents', '/api/faq']:
        response.headers['Cache-Control'] = f'public, max-age={Config.CACHE_TTL_SECONDS}'
        response.headers['ETag'] = f'"{Config.VERSION}-{request.path}"'
    elif request.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store'
        
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
        
    if age < 0 or age > 150:
        raise InvalidInputError("age", "Age must be between 1 and 150.")
        
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
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(Config.GEMINI_MODEL)
        
        system_prompt = (
            "You are VoteWise, an AI assistant that educates Indian citizens about the election process. "
            "You provide accurate, non-partisan information based on Election Commission of India (ECI) guidelines.\n"
            "Key facts: Form 6 for registration, age 18 on qualifying date, EPIC card needed, EVM has blue button, "
            "VVPAT 7 sec slip, NOTA available, Model Code of Conduct applies, 48 hours silence period, Polling 7 AM - 6 PM.\n"
            "Rules: Be concise (2-3 sentences max). Stay non-partisan. Cite ECI guidelines. Direct to eci.gov.in or 1950 if unsure. Use markdown for better formatting (like bolding key terms). When mentioning 'Form 6' or any registration form, format it as an HTML link to https://voters.eci.gov.in/ (e.g., <a href='https://voters.eci.gov.in/' target='_blank'>Form 6</a>)."
        )
        
        response = model.generate_content(
            system_prompt + "\n\nUser Question: " + message,
            generation_config={"temperature": 0.2, "max_output_tokens": 200}
        )
        
        logging.info("Gemini SDK successfully generated content.")
        return jsonify({"reply": str(escape(response.text)), "source": "gemini"}), 200
    except Exception as e:
        logging.error(f"Gemini SDK failed: {e}")
        return jsonify({"reply": _get_gemini_fallback(message)}), 200

@app.route('/api/translate', methods=['POST'])
def translate():
    """Translate text using Google Cloud Translation API."""
    data = request.get_json() or {}
    text = data.get('text', '').strip()
    target = data.get('target', 'hi')
    
    if not text:
        raise InvalidInputError("text", "Text is required for translation.")
    if len(text) > Config.MAX_TEXT_LENGTH:
        raise InvalidInputError("text", "Text is too long.")
    
    api_key = Config.GOOGLE_TRANSLATE_API_KEY
    if not api_key:
        # Graceful fallback: return original text with language indicator
        return jsonify({"translated": text, "language": target, "source": "fallback"})
    
    try:
        translate_client = translate.Client()
        result = translate_client.translate(text, target_language=target)
        logging.info("Translate SDK successfully processed request.")
        return jsonify({"translated": result["translatedText"], "language": target, "source": "google"})
    except Exception as e:
        logging.error(f"Translation SDK failed: {e}")
        return jsonify({"translated": text, "language": target, "source": "fallback"})

@app.route("/api/save-feedback", methods=["POST"])
def save_feedback():
    """Mock saving user experience to Firebase."""
    data = request.get_json()
    if not data or "rating" not in data:
        raise InvalidInputError("rating", "Missing rating.")
    
    rating = int(data.get("rating", 0))
    if rating < 1 or rating > 5:
        raise InvalidInputError("rating", "Rating must be between 1 and 5.")
        
    try:
        if db:
            db.collection("user_feedback").add({"rating": rating})
            logging.info(f"Feedback rating {rating} written to Firestore.")
    except Exception as e:
        logging.error(f"Firestore write failed: {e}")
        
    return jsonify({"status": "success", "message": "Feedback saved."}), 200

@app.route("/api/firebase-config", methods=["GET"])
def get_firebase_config():
    """Firebase config retrieval for client side (anonymous auth feature)."""
    return jsonify({"apiKey": Config.FIREBASE_API_KEY}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(Config.PORT), debug=Config.DEBUG)
