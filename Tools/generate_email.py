from gettestmail.client import GetTestMailClient
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("GETTESTMAIL_API_KEY")

def generate_temp_email(timeout=10):
    # expires_at = "2023-04-01T00:00:00Z"

    client = GetTestMailClient(API_KEY)
    test_mail = client.create_new()
    # return the mailbox object (test_mail) so callers can pass it back to the client
    return test_mail.emailAddress, test_mail, client