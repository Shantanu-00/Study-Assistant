from twilio.rest import Client
from config import TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def send_whatsapp_message(to_number, message):
    from_number = f"whatsapp:{TWILIO_PHONE}"
    print(f"[DEBUG] Sending from: {from_number}, to: whatsapp:{to_number}")
    try:
        client.messages.create(
            body=message,
            from_=from_number,
            to=f"whatsapp:{to_number}"
        )
        print(f"[DEBUG] WhatsApp message sent to {to_number}: {message}")
    except Exception as e:
        print(f"[ERROR] Failed to send WhatsApp message: {e}")

def notify_guardian(username, event_type, timestamp):
    import sqlite3
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT guardian_phone, name FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()

    if result:
        guardian_phone, student_name = result
        message = f"Study Buddy Alert: {student_name} was caught {event_type} at {timestamp}."
        send_whatsapp_message(guardian_phone, message)