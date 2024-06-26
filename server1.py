from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from apscheduler.schedulers.background import BackgroundScheduler
from bll.bllengine import create_request
from Data_base.database_config import get_db_connection
from helper_folder.helper import send_notification
from recipient_logic import determine_recipient  # Ensure this import is correct
import logging
import atexit

app = Flask(__name__)
socketio = SocketIO(app)

connected_users = {}

# Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    user_id = request.args.get('user_id')  # Assume the client sends 'user_id' as a query parameter
    connected_users[user_id] = request.sid
    print(f'Client connected: {user_id}')

@socketio.on('disconnect')
def handle_disconnect():
    user_id = None
    for uid, sid in connected_users.items():
        if sid == request.sid:
            user_id = uid
            break
    if user_id:
        del connected_users[user_id]
    print(f'Client disconnected: {user_id}')

@socketio.on('chat message')
def handle_message(data):
    user_id = data.get('user_id')
    message = data.get('message')
    print(f'Message received from {user_id}: {message}')
    log_message(user_id, message)  # Log the message
    emit('chat message', {'user_id': user_id, 'message': message}, broadcast=True)  # Broadcast to all connected clients

def log_message(user_id, message):
    # Implement your logging logic here
    with open('chat_log.txt', 'a') as log_file:
        log_file.write(f'{user_id}: {message}\n')

# Function to check new job requests periodically
def check_new_job_requests():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM job_opening_requests WHERE status = 'new'"
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            # Prepare candidate information
            candidate_info = {
                'name': row['user_id'],
                'business_unit': row['business_unit'],
                'job_title': row['job_title'],
                'job_description': row['job_description'],
                'max_years_exp': row['max_years_exp'],
                'user_email': row['user_email']
            }

            # Determine recipient based on admin_id or other criteria
            recipient = determine_recipient(row)  # Implement determine_recipient function based on your logic

            # Send desktop notification
            success = send_notification(candidate_info, recipient)

            # Update the status to 'notified' after sending notification
            if success:
                update_query = "UPDATE job_opening_requests SET status = 'notified' WHERE job_request_id = %s"
                cursor.execute(update_query, (row['job_request_id'],))
                connection.commit()

        cursor.close()
        connection.close()

    except Exception as e:
        logging.error(f"Error in check_new_job_requests: {e}")

# Schedule job to run check_new_job_requests every 60 seconds
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_new_job_requests, trigger="interval", seconds=60)
scheduler.start()

# API endpoint to send desktop notifications
@app.route('/Desktop_notification', methods=['POST'])
def desktop_notification():
    try:
        data = request.get_json()  # Retrieve JSON data from the request

        # Extract request_data from JSON
        request_data = data.get('request_data', {})

        # Prepare candidate information
        candidate_info = {
            'reporting_manager': request_data.get('reporting_manager', ''),
            'business_unit': request_data.get('business_unit', ''),
            'user_email': request_data.get('user_email', ''),
            'admin_id': request_data.get('admin_id', ''),
            'name': request_data.get('name', ''),
            'job_title': request_data.get('job_title', ''),
            'max_years_exp': request_data.get('max_years_exp', ''),
            'company': request_data.get('company', ''),
            # Add more fields as needed
        }

        # Determine recipient based on your application logic
        recipient = determine_recipient(request_data)  # Call determine_recipient function

        # Send notification with recipient and get the updated candidate_info
        updated_candidate_info = send_notification(candidate_info, recipient)

        if updated_candidate_info:
            return jsonify(updated_candidate_info), 200  # Return the updated candidate_info
        else:
            return jsonify({"status": "failure"}), 500

    except Exception as e:
        logging.error(f"Error in desktop_notification endpoint: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# API endpoint to add job requests
@app.route('/add_job_request', methods=['POST'])
def add_job_request():
    try:
        data = request.get_json().get('request_data', {})

        # Handle empty salary fields
        data['min_salary'] = data.get('min_salary') or None
        data['max_salary'] = data.get('max_salary') or None

        # Handle empty datetime fields
        data['approved_on'] = data.get('approved_on') or None

        success = create_request('job_opening_requests', data)

        if success:
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "failure"}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    socketio.run(app, debug=True)
