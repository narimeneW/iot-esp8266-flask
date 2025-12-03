from flask import Flask, render_template, request, jsonify
from redis import Redis
from datetime import datetime
import psycopg2
import os
import json
from apscheduler.schedulers.background import BackgroundScheduler
import time

app = Flask(__name__)
redis = Redis(host="redis", db=0, socket_timeout=5, charset="utf-8", decode_responses=True)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'postgres'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'iotdb'),
    'user': os.getenv('DB_USER', 'iotuser'),
    'password': os.getenv('DB_PASSWORD', 'iotpassword')
}

def get_db_connection():
    """Create a database connection"""
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    """Initialize the database table"""
    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS names (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            cur.close()
            conn.close()
            print("Database initialized successfully")
            return
        except psycopg2.OperationalError as e:
            retry_count += 1
            print(f"Database connection failed (attempt {retry_count}/{max_retries}): {e}")
            if retry_count < max_retries:
                time.sleep(2)
            else:
                print("Failed to initialize database after maximum retries")

def sync_cache_to_db():
    """Cron job to sync Redis cache to PostgreSQL"""
    try:
        # Get all items from Redis
        items = redis.lrange('names', 0, -1)

        if not items:
            print("No items to sync")
            return

        conn = get_db_connection()
        cur = conn.cursor()

        synced_count = 0
        for item_str in items:
            try:
                # Parse the JSON string
                item = json.loads(item_str)
                name = item.get('name')
                created_at = item.get('created_at')

                # Check if this entry already exists
                cur.execute(
                    'SELECT id FROM names WHERE name = %s AND created_at = %s',
                    (name, created_at)
                )

                if not cur.fetchone():
                    # Insert new entry
                    cur.execute(
                        'INSERT INTO names (name, created_at) VALUES (%s, %s)',
                        (name, created_at)
                    )
                    synced_count += 1
            except json.JSONDecodeError:
                print(f"Failed to parse item: {item_str}")
                continue

        conn.commit()
        cur.close()
        conn.close()
        print(f"Synced {synced_count} new entries to database")

        # Clear the Redis cache after successful sync
        if synced_count > 0:
            redis.delete('names')
            print(f"Cleared {synced_count} entries from Redis cache")
    except Exception as e:
        print(f"Error syncing cache to database: {e}")

# Initialize database
init_db()

# Set up the scheduler for periodic sync
scheduler = BackgroundScheduler()
scheduler.add_job(func=sync_cache_to_db, trigger="interval", minutes=3)
scheduler.start()

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        name = request.json['name']

        # Create object with name and timestamp
        entry = {
            'name': name,
            'created_at': datetime.now().isoformat()
        }

        # Store as JSON string in Redis
        redis.rpush('names', json.dumps(entry))

        return jsonify(entry)

    if request.method == 'GET':
        # Get all entries from Redis
        items = redis.lrange('names', 0, -1)

        # Parse JSON strings back to objects
        entries = []
        for item in items:
            try:
                entries.append(json.loads(item))
            except json.JSONDecodeError:
                # Handle old format (plain strings)
                entries.append({'name': item, 'created_at': None})

        return jsonify(entries)

@app.route('/db-data')
def get_db_data():
    """Fetch all data from the database"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT name, created_at, synced_at FROM names ORDER BY synced_at DESC')
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Convert to list of dictionaries
        entries = []
        for row in rows:
            entries.append({
                'name': row[0],
                'created_at': row[1].isoformat() if row[1] else None,
                'synced_at': row[2].isoformat() if row[2] else None
            })

        return jsonify(entries)
    except Exception as e:
        print(f"Error fetching database data: {e}")
        return jsonify([])

@app.route('/action')
def do():
    # Get all entries from Redis
    items = redis.lrange('names', 0, -1)

    # Parse JSON strings back to objects
    entries = []
    for item in items:
        try:
            entries.append(json.loads(item))
        except json.JSONDecodeError:
            # Handle old format (plain strings)
            entries.append({'name': item, 'created_at': None})

    templateData = {'name': entries}
    return render_template('index.html', **templateData)

# Shutdown scheduler when app stops
import atexit
atexit.register(lambda: scheduler.shutdown())
