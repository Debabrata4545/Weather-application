import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from chat_service import get_chat_response
from music_service import search_music, get_recommendations

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

db.init_app(app)

with app.app_context():
    import models
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            logger.error("Invalid request: missing message")
            return jsonify({"error": "Missing message"}), 400

        user_message = data['message']
        logger.info(f"Received chat message: {user_message}")

        response = get_chat_response(user_message)
        logger.info(f"Chat response: {response}")

        return jsonify(response)
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({
            "response": "Sorry, something went wrong. Please try again.",
            "action": None,
            "query": None
        }), 500

@app.route("/search_music", methods=["POST"])
def search():
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            logger.error("Invalid request: missing query")
            return jsonify({"error": "Missing query"}), 400

        query = data['query']
        logger.info(f"Searching for music: {query}")

        results = search_music(query)
        logger.info(f"Found {len(results)} music results")

        return jsonify(results)
    except Exception as e:
        logger.error(f"Music search error: {str(e)}")
        return jsonify({"error": "Failed to search music"}), 500

@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        data = request.get_json()
        if not data or 'song_id' not in data:
            logger.error("Invalid request: missing song_id")
            return jsonify({"error": "Missing song ID"}), 400

        song_id = data['song_id']
        logger.info(f"Getting recommendations for song: {song_id}")

        recommendations = get_recommendations(song_id)
        logger.info(f"Found {len(recommendations)} recommendations")

        return jsonify(recommendations)
    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}")
        return jsonify({"error": "Failed to get recommendations"}), 500
