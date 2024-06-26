import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'passwd': '',
    'database': 'ta_notification_alerts',
    'port': 3307
}

def get_db_connection():
    return mysql.connector.connect(**db_config)
