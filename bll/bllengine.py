from Data_base.database_config import get_db_connection
from helper_folder.helper import send_notification
import logging
def create_request(table_name, request_data):
    db_connection = get_db_connection()
    my_database = db_connection.cursor()
    columns = ', '.join(request_data.keys())
    values = ', '.join(['%s'] * len(request_data))
    sql_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
    try:
        my_database.execute(sql_query, tuple(request_data.values()))
        db_connection.commit()
        log_notification(request_data)
        return True
    except Exception as err:
        logging.error(f"Database error: {err}")
        print("Database error", err)
        return False
    finally:
        my_database.close()
        db_connection.close()
    

def log_notification(request_data):
    candidate_name = request_data.get('name')
    business_unit = request_data.get('business_unit')
    job_title = request_data.get('job_title')
    job_description = request_data.get('job_description')
    max_years_exp = request_data.get('max_years_exp')
    user_email = request_data.get('user_email')

    # Log notification to console or file
    logging.info(f"New job request added: Candidate {candidate_name}, Business Unit {business_unit}, Job Title {job_title}, Description {job_description}, Max Years Exp {max_years_exp}, Email {user_email}")




def get_columns_datatypes(database_name, table_name):
    db_connection = get_db_connection()
    my_database = db_connection.cursor(dictionary=True)
    sql_query = f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '{database_name}' AND TABLE_NAME = '{table_name}'"
    try:
        my_database.execute(sql_query)
        output = my_database.fetchall()
    except Exception as err:
        print("Exception error ...>", err)
        output = {"Error": "Error occurred at database"}
    finally:
        db_connection.close()
        my_database.close()
    return output

def insert_into_table(tablename, fields, data, args=None):
    db_connection = get_db_connection()
    my_database = db_connection.cursor()
    sql_query = f"INSERT INTO {tablename}({fields}) VALUES({data})"
    try:
        my_database.execute(sql_query, args)
        db_connection.commit()
        my_database.execute("SELECT LAST_INSERT_ID()")
        last_inserted_id = my_database.fetchone()[0]
        retVal = {"message": "Success", "last_insert_id": last_inserted_id}
    except Exception as err:
        print("Exception error message---->", err)
        retVal = {"message": "Failed", "last_insert_id": None}
    finally:
        my_database.close()
        db_connection.close()
    return retVal

def check_new_job_requests():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = "SELECT * FROM job_opening_requests WHERE status = 'new'"
    cursor.execute(query)
    rows = cursor.fetchall()
    
    for row in rows:
        # Create candidate_info dictionary
        candidate_info = {
            'name': row['user_id'],
            'business_unit': row['business_unit'],
            'job_title': row['job_title'],
            'job_description': row['job_description'],
            'max_years_exp': row['max_years_exp'],
            'user_email': row['user_email']
        }

        # Example logic to determine the recipient
        if row.get('priority') == 'high':
            recipient = 'super_admin'
        else:
            recipient = 'admin'

        # Send desktop notification
        send_notification(candidate_info, recipient)
        
        # Update the status to 'notified' after sending notification
        update_query = "UPDATE job_opening_requests SET status = 'notified' WHERE job_request_id = %s"
        cursor.execute(update_query, (row['job_request_id'],))
        connection.commit()

    cursor.close()
    connection.close()

