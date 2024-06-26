import platform
import subprocess
from plyer import notification

def send_notification(candidate_info, recipient):
    try:
        # Extract information from candidate_info
        name = candidate_info.get('name', '')
        business_unit = candidate_info.get('business_unit', '')
        job_title = candidate_info.get('job_title', '')
        job_description = candidate_info.get('job_description', '')
        max_years_exp = candidate_info.get('max_years_exp', '')
        user_email = candidate_info.get('user_email', '')

        # Prepare notification message
        title = f"New Job Request: {job_title}"
        message = (
            f"Candidate Name: {name}\n"
            f"Business Unit: {business_unit}\n"
            f"Job Title: {job_title}\n"
            f"Job Description: {job_description}\n"
            f"Max Years of Experience: {max_years_exp}\n"
            f"User Email: {user_email}"
        )

        # Example: Check recipient and send notification based on recipient's role or ID
        if recipient == 'admin':
            # Send notification to admin
            send_admin_notification(title, message)
        elif recipient == 'super_admin':
            # Send notification to super admin
            send_super_admin_notification(title, message)
        else:
            # Handle other cases or invalid recipients
            raise ValueError(f"Invalid recipient: {recipient}")

        # Return the candidate_info on success
        return candidate_info

    except Exception as e:
        print(f"Error sending desktop notification: {e}")
        return None

    finally:
        # Perform cleanup or finalization tasks here, e.g., logging, updating database
        print("Notification attempt completed.")

def send_admin_notification(title, message):
    send_desktop_notification(title, message)

def send_super_admin_notification(title, message):
    send_desktop_notification(title, message)

def send_desktop_notification(title, message):
    try:
        if platform.system() == "Darwin":
            # macOS
            subprocess.run(['osascript', '-e', f'display notification "{message}" with title "{title}"'])
        elif platform.system() == "Linux":
            # Linux using notify-send
            subprocess.run(['notify-send', title, message])
        elif platform.system() == "Windows":
            # Windows using plyer.notification
            notification.notify(
                title=title,
                message=message
            )
    except Exception as e:
        print(f"Error sending desktop notification: {e}")
