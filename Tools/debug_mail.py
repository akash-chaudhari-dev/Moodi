from Tools.generate_email import generate_temp_email
import time


def dump_messages(client, mailbox):
    mid = getattr(mailbox, "id", None)
    print(f"Mailbox id: {mid}")
    print(f"Mailbox object: {mailbox}")
    print("Attempting to list messages using known client methods...")

    # try several client methods and print results
    tried = []
    if hasattr(client, "get_messages"):
        try:
            msgs = client.get_messages(mid)
            print(f"get_messages returned {len(msgs)} messages")
            for i, m in enumerate(msgs[-10:], start=1):
                print(f"--- message {i} ---")
                for attr in ("subject", "message", "body", "text", "content", "html"):
                    if hasattr(m, attr):
                        print(f"{attr}: {getattr(m, attr)[:500]}")
                print(str(m)[:1000])
            tried.append("get_messages")
        except Exception as e:
            print(f"get_messages failed: {e}")

    if hasattr(client, "get_message"):
        try:
            m = client.get_message(mid)
            print("get_message returned:")
            print(str(m)[:1000])
            tried.append("get_message")
        except Exception as e:
            print(f"get_message failed: {e}")

    if hasattr(client, "wait_for_message"):
        try:
            print("Calling wait_for_message with 5s timeout to try to receive any recent mail...")
            m = client.wait_for_message(mailbox, timeout=5)
            print("wait_for_message returned:")
            print(str(m)[:1000])
            tried.append("wait_for_message")
        except Exception as e:
            print(f"wait_for_message failed or returned nothing quickly: {e}")

    if not tried:
        print("No known client retrieval methods found; mailbox object keys:")
        try:
            print(dir(mailbox))
        except Exception:
            pass


if __name__ == '__main__':
    print("Creating test mailbox...")
    email, mailbox, client = generate_temp_email()
    print(f"Use this address in the web form: {email}")
    print("Now trigger Send OTP on the site (or forward an email to this address). Polling for 60s...")

    deadline = time.time() + 60
    seen = set()
    while time.time() < deadline:
        try:
            dump_messages(client, mailbox)
        except Exception as e:
            print(f"Error dumping messages: {e}")
        time.sleep(5)

    print("Done polling.")
