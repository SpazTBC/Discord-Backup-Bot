from flask import Flask, request, jsonify, abort
import os
import json
import threading
import time

app = Flask(__name__)

# Define upload folder for storing backup files
UPLOAD_FOLDER = 'uploads'
BACKUP_COUNT_FILE = 'backup_count.txt'

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize global guild_id
guild_id = None

# Initialize backup count
backup_count = 0

# Load initial backup count
if os.path.exists(BACKUP_COUNT_FILE):
    with open(BACKUP_COUNT_FILE, 'r') as f:
        backup_count = int(f.read())

# Function to get user list from user_list.json file in guild upload folder
def get_user_list(guild_id):
    guild_upload_folder = os.path.join(UPLOAD_FOLDER, str(guild_id))
    user_list_path = os.path.join(guild_upload_folder, 'user_list.json')
    if os.path.exists(user_list_path):
        with open(user_list_path, 'r') as f:
            user_list_data = json.load(f)
        return user_list_data.get('users', [])
    else:
        return []

# Function to get user count from user_list.json file in guild upload folder
def get_user_count(guild_id):
    return len(get_user_list(guild_id))

# Route to handle file uploads from Discord bot
@app.route('/api/upload', methods=['POST'])
def upload_files():
    global guild_id, backup_count
    
    # Check if required files are provided
    if 'backup.json' not in request.files or 'roles_backup.json' not in request.files or 'command_log.txt' not in request.files or 'user_list.json' not in request.files:
        return 'Required files not provided', 400
    
    # Get guild ID from custom header
    guild_id = request.headers.get('X-Guild-ID')
    #print(f"Received guild ID: {guild_id}")  # Log the received guild ID
    
    # Check if guild ID is provided
    if not guild_id:
        return 'Guild ID not provided', 400
    
    # Convert guild ID to string
    guild_id = str(guild_id)
    
    # Create directory for guild if it doesn't exist
    guild_upload_folder = os.path.join(UPLOAD_FOLDER, guild_id)
    if not os.path.exists(guild_upload_folder):
        os.makedirs(guild_upload_folder)
    
    # Get files from request
    backup_file = request.files['backup.json']
    roles_backup_file = request.files['roles_backup.json']
    log_file = request.files['command_log.txt']
    user_list_file = request.files['user_list.json']

    # Save files to guild-specific upload folder
    backup_file.save(os.path.join(guild_upload_folder, backup_file.filename))
    roles_backup_file.save(os.path.join(guild_upload_folder, roles_backup_file.filename))
    log_file.save(os.path.join(guild_upload_folder, log_file.filename))
    user_list_file.save(os.path.join(guild_upload_folder, user_list_file.filename))
    
    # Update backup count
    backup_count += 1
    with open(BACKUP_COUNT_FILE, 'w') as f:
        f.write(str(backup_count))

    return 'Files uploaded successfully', 200

# Route to get backup status
@app.route('/api/backup/status', methods=['GET'])
def get_backup_status():
    return jsonify({'status': 'pending'})

# Route to get backup count
@app.route('/api/backup/count', methods=['GET'])
def get_backup_count():
    global backup_count
    return jsonify({'count': backup_count})

# Route to get user count
@app.route('/api/user/count', methods=['GET'])
def get_user_count_route():
    global guild_id
    if not guild_id:
        abort(400, 'Guild ID not provided')
    return jsonify({'count': get_user_count(guild_id)})

# Route to get user list
@app.route('/api/user/list', methods=['GET'])
def get_user_list_route():
    global guild_id
    if not guild_id:
        abort(400, 'Guild ID not provided')
    user_list = get_user_list(guild_id)
    return jsonify({'users': user_list})


# List to store pending requests
pending_requests = []

# Route to get pending requests
@app.route('/api/pending-requests', methods=['GET'])
def get_pending_requests():
    global pending_requests
    if request.method == 'POST':
        pending_requests.append(request.json)  # Assuming JSON data is sent in POST requests
        return jsonify({'message': 'Request received and added to pending list'}), 200
    else:
        if pending_requests:
            return jsonify({'pending_requests': pending_requests}), 200
        else:
            return '', 200


if __name__ == '__main__':
    app.run(debug=True)
