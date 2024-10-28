from flask import Flask, request, jsonify, abort
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlite3
import logging

# Initialize the Flask application
app = Flask(__name__)

# Set up caching
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})

# Initialize Flask-Limiter with rate-limiting per API key
limiter = Limiter(key_func=lambda: request.headers.get("X-API-KEY"), app=app, default_limits=["5 per minute"])

# Set up logging
logging.basicConfig(level=logging.INFO)

# Database setup function
def init_db():
    conn = sqlite3.connect('data_store.db')
    cursor = conn.cursor()
    # Create data and api_keys tables if they do not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            api_key TEXT PRIMARY KEY
        )
    ''')
    # Insert predefined API keys
    api_keys = [('validapi1',), ('validapi2',), ('validapi3',)]
    cursor.executemany("INSERT OR IGNORE INTO api_keys (api_key) VALUES (?)", api_keys)
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Helper function to execute database queries
def query_db(query, args=(), one=False):
    conn = sqlite3.connect('data_store.db')
    cursor = conn.cursor()
    cursor.execute(query, args)
    result = cursor.fetchone() if one else cursor.fetchall()
    conn.commit()
    conn.close()
    return result

# Check if an API key is valid
def is_valid_api_key(api_key):
    result = query_db("SELECT 1 FROM api_keys WHERE api_key = ?", (api_key,), one=True)
    return bool(result)

# Decorator for API key requirement
def require_api_key(func):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("X-API-KEY")
        if not api_key or not is_valid_api_key(api_key):
            abort(401, description="Invalid or missing API Key")
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# GET route to retrieve data by key with caching
@app.route('/data/<key>', methods=['GET'])
@limiter.limit("5 per minute")  # Limit this route to 5 requests per minute
@require_api_key
def get_data(key):
    logging.info(f"Fetching data for key: {key}")
    
    # Check cache first
    cached_value = cache.get(key)
    if cached_value is not None:
        return jsonify({"data": {key: cached_value}, "source": "cache"})

    # Query database if not found in cache
    result = query_db("SELECT value FROM data WHERE key = ?", (key,), one=True)
    if result:
        value = result[0]
        cache.set(key, value)  # Cache the result
        return jsonify({"data": {key: value}, "source": "database"})
    else:
        logging.error(f"Key not found: {key}")
        return jsonify({"error": "Key not found"}), 404

# POST route to add new data
@app.route('/data', methods=['POST'])
@limiter.limit("5 per minute")  # Limit this route to 5 requests per minute
@require_api_key
def post_data():
    request_data = request.get_json()
    key = request_data.get("key")
    value = request_data.get("value")

    logging.info(f"Adding data for key: {key}")

    # Check if key exists
    if query_db("SELECT 1 FROM data WHERE key = ?", (key,), one=True):
        logging.error(f"Attempted to add duplicate key: {key}")
        return jsonify({"error": "Key already exists"}), 400

    # Insert new data into the database and cache it
    query_db("INSERT INTO data (key, value) VALUES (?, ?)", (key, value))
    cache.set(key, value)  # Cache the new entry
    return jsonify({"message": "Data added successfully", key: value}), 201

# PUT route to update existing data
@app.route('/data/<key>', methods=['PUT'])
@limiter.limit("5 per minute")  # Limit this route to 5 requests per minute
@require_api_key
def put_data(key):
    logging.info(f"Updating data for key: {key}")
    
    # Check if key exists
    if not query_db("SELECT 1 FROM data WHERE key = ?", (key,), one=True):
        logging.error(f"Key not found for update: {key}")
        return jsonify({"error": "Key not found"}), 404

    request_data = request.get_json()
    value = request_data.get("value")
    
    # Update data in the database and cache
    query_db("UPDATE data SET value = ? WHERE key = ?", (value, key))
    cache.set(key, value)  # Update the cache
    return jsonify({"message": "Data updated successfully", key: value})

# GET route to retrieve all data
@app.route('/data', methods=['GET'])
@limiter.limit("5 per minute")  # Limit this route to 5 requests per minute
def get_all_data():
    # Query all data from the database
    results = query_db("SELECT key, value FROM data")
    
    # Ensure no None values and convert to a dictionary
    data_dict = {key: (value if value is not None else "") for key, value in results}
    
    return jsonify(data_dict)


# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
