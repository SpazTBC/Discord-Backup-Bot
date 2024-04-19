from flask import Flask, request
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/api', methods=['POST'])
def upload_files():
    if 'backup.json' not in request.files or 'roles_backup.json' not in request.files or 'command_log.txt' not in request.files:
        return 'Required files not provided', 400
    
    # Get guild ID from custom header
    guild_id = request.headers.get('X-Guild-ID')
    print(f"Received guild ID: {guild_id}")  # Add this line to log the received guild ID
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

    # Save files to guild-specific upload folder
    backup_file.save(os.path.join(guild_upload_folder, backup_file.filename))
    roles_backup_file.save(os.path.join(guild_upload_folder, roles_backup_file.filename))
    log_file.save(os.path.join(guild_upload_folder, log_file.filename))

    return 'Files uploaded successfully', 200



if __name__ == '__main__':
    app.run(debug=True)
