# recipient_logic.py

def determine_recipient(request_data):
    # Example logic based on request_data fields or user roles
    if request_data.get('admin_id') == 'admin123':
        return 'admin'
    elif request_data.get('admin_id') == 'superadmin456':
        return 'super_admin'
    else:
        # Default case or handle other scenarios
        return 'default_recipient'
