from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from bll.bllengine import create_request
from Data_base.database_config import get_db_connection
from helper_folder.helper import send_notification
#from recipient_logic import determine_recipient
import logging
# from flask_socketio import SocketIO, emit
import atexit
app = Flask(__name__)
# socketio = SocketIO(app)
# @socketio.on('connect')
# def handle_connect():
#     print('Client connected')

# @socketio.on('disconnect')
# def handle_disconnect():
#     print('Client disconnected')

# @socketio.on('chat message')
# def handle_message(message):
#     print('Message received:', message)
#     emit('chat message', message, broadcast=True)  # Broadcast the message to all connected clients

def check_new_job_requests():
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

        # Send desktop notification
        success = send_notification(candidate_info)
        
        # Update the status to 'notified' after sending notification
        if success:
            update_query = "UPDATE job_opening_requests SET status = 'notified' WHERE job_request_id = %s"
            cursor.execute(update_query, (row['job_request_id'],))
            connection.commit()

    cursor.close()
    connection.close()

scheduler = BackgroundScheduler()
scheduler.add_job(func=check_new_job_requests, trigger="interval", seconds=60)
scheduler.start()


#This send the notification about the interview candidate detail to the desktop 


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
        recipient = 'admin'  # Replace with determine_recipient(request_data) based on your logic

        # Send notification with recipient and get the updated candidate_info
        updated_candidate_info = send_notification(candidate_info, recipient)

        if updated_candidate_info:
            return jsonify(updated_candidate_info), 200  # Return the updated candidate_info
        else:
            return jsonify({"status": "failure"}), 500

    except Exception as e:
        logging.error(f"Error in desktop_notification endpoint: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
    

# This function store the data to the database 
@app.route('/add_job_request', methods=['POST'])
def add_job_request():
    try:
        data = request.get_json()
        request_data = data.get('request_data', {})

        # Handle empty salary fields
        request_data['min_salary'] = request_data.get('min_salary') or None
        request_data['max_salary'] = request_data.get('max_salary') or None

        # Handle empty datetime fields
        request_data['approved_on'] = request_data.get('approved_on') or None

        success = create_request('job_opening_requests', request_data)

        if success:
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "failure"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
    #socketio.run(app, debug=True)
    #app.run(debug=True,host='0.0.0.0',port=5000)


# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())







    
