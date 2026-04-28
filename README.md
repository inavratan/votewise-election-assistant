# VoteWise Election Education Assistant

## Problem Statement
Indian citizens, especially first-time voters, often find the election process confusing. Due to a lack of centralized, engaging education tools, voters struggle with registration deadlines, polling booth procedures, required documents, EVM operations, and combating misinformation during elections.

## Solution
**VoteWise** is an AI-powered interactive progressive web app (PWA) that acts as an all-in-one companion for citizens. It provides a complete election process walkthrough, voter eligibility checks, document checklists, and a 24/7 Gemini-powered AI concierge that strictly answers questions based on Election Commission of India guidelines.

## Architecture & Technology Stack
VoteWise uses a lightweight, high-performance architecture:
*   **Backend:** Python Flask providing JSON REST APIs.
*   **AI Integration:** Google Gemini AI Model via precise REST payload calls.
*   **Frontend:** Vanilla JS / HTML / CSS (Single Page App style, PWA enabled).
*   **Server Runtime:** `gunicorn` with multi-worker threading inside a Docker container.

### Assumptions
*   All data provided in the app is based on statically curated ECI guidelines embedded within `data.py`. It does not rely on live ECI database scraping.
*   The Firebase endpoint is mocked / conceptually established for anonymous authentication and usage rating aggregation securely over Cloud Firestore architecture.
*   The translation route is prepared as an endpoint payload simulation for Cloud Translation capabilities.

## Google Cloud Services Employed
1.  **Google Cloud Run:** Hosts the Dockerized Flask application.
2.  **Google Gemini AI:** Used to drive the Concierge election chatbot assistant.
3.  **Google Fonts:** Specifically providing `DM Sans` and `Material Symbols Outlined`.
4.  **Google Maps Platform:** Prepared mapping scripts for polling booth localization.
5.  **Google Analytics (GA4):** Embedded `gtag` code for measuring interaction and tab navigations.
6.  **Google Translate API:** Referenced architectural block for English/Hindi localization.
7.  **Firebase:** Prepared endpoint mock and logic flows for user ratings storage.
8.  **Google Calendar API:** Contextual workflow capability documented for "Save Election Date".
9.  **Google Cloud Build:** Docker image build pipeline enabler.
10. **Google Cloud Content Delivery Network (CDN):** For accelerating PWA asset delivery statically.

## How to run locally

### Pre-requisites
Ensure you have Python 3.11+ installed.

### Setup Steps
1. Navigate to the project directory.
2. Install the core requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Set optional environment variable for Gemini logic:
   ```bash
   export GEMINI_API_KEY="your-api-key"
   ```
4. Start the Flask application:
   ```bash
   python app.py
   ```
5. Alternatively, via Docker:
   ```bash
   docker build -t votewise -f Dockerfile .
   docker run -p 8080:8080 votewise
   ```

### Testing
Run `pytest` in the directory:
```bash
pytest test_app.py -v
```
All 18 comprehensive tests will validate routing, security, fallback systems, algorithms, and PWA assets.
