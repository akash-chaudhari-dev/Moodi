import time
import re


def get_otp(mailbox_or_id, client, timeout=120, poll_interval=3):
    """
    Polls the provided GetTestMail `client` for a message for `email_id`.
    Extracts and returns the first OTP found (4-8 digit number) or None on timeout.

    Parameters:
      - email_id: id returned by create_new() for the mailbox
      - client: an instance of GetTestMailClient
      - timeout: total seconds to wait before giving up
      - poll_interval: seconds between polls
    """
    deadline = time.time() + timeout
    attempts = 0
    while time.time() < deadline:
        attempts += 1
        try:
            msg = None
            # Try wait_for_message using various mailbox identifiers
            if hasattr(client, "wait_for_message"):
                tried = []
                for candidate in (mailbox_or_id, getattr(mailbox_or_id, "id", None), getattr(mailbox_or_id, "emailAddress", None)):
                    if candidate is None:
                        continue
                    tried.append(candidate)
                    try:
                        msg = client.wait_for_message(candidate, timeout=poll_interval)
                        print(f"[get_otp] wait_for_message succeeded with candidate={candidate}")
                        break
                    except TypeError:
                        # some implementations don't accept timeout param
                        try:
                            msg = client.wait_for_message(candidate)
                            print(f"[get_otp] wait_for_message succeeded without timeout with candidate={candidate}")
                            break
                        except Exception:
                            msg = None
                    except Exception:
                        msg = None

            # try get_messages
            if not msg and hasattr(client, "get_messages"):
                try:
                    mid = getattr(mailbox_or_id, "id", mailbox_or_id)
                    msgs = client.get_messages(mid)
                    msg = msgs[-1] if msgs else None
                    if msg:
                        print(f"[get_otp] get_messages returned {len(msgs)} messages, picked latest")
                except Exception:
                    msg = None

            # try get_message (single)
            if not msg and hasattr(client, "get_message"):
                try:
                    mid = getattr(mailbox_or_id, "id", mailbox_or_id)
                    msg = client.get_message(mid)
                    if msg:
                        print("[get_otp] get_message returned a message")
                except Exception:
                    msg = None

            # last resort: check mailbox_or_id.messages if it's a mailbox object
            if not msg:
                try:
                    maybe_msgs = getattr(mailbox_or_id, "messages", None)
                    if maybe_msgs:
                        msg = maybe_msgs[-1]
                        print("[get_otp] found message via mailbox.messages")
                except Exception:
                    pass

            if not msg:
                # no message yet
                time.sleep(poll_interval)
                continue


            # Safely extract textual content from the returned message.
            def _extract_text(obj):
                # If it's already a string or bytes, return a string
                if isinstance(obj, str):
                    return obj
                if isinstance(obj, bytes):
                    try:
                        return obj.decode('utf-8', errors='replace')
                    except Exception:
                        return str(obj)

                # If it's a dict-like, try common keys
                if isinstance(obj, dict):
                    for key in ("message", "body", "text", "content", "html", "data", "raw"):
                        if key in obj and obj[key]:
                            return _extract_text(obj[key])
                    # try scanning values
                    for v in obj.values():
                        t = _extract_text(v)
                        if t:
                            return t
                    return str(obj)

                # If it has attributes (object returned by client), try common attrs
                for attr in ("message", "body", "text", "content", "html", "subject"):
                    try:
                        if hasattr(obj, attr):
                            val = getattr(obj, attr)
                            t = _extract_text(val)
                            if t:
                                return t
                    except Exception:
                        continue

                # If it's a list/tuple, try elements
                if isinstance(obj, (list, tuple)):
                    for v in obj:
                        t = _extract_text(v)
                        if t:
                            return t

                # Fallback to string coercion
                try:
                    return str(obj)
                except Exception:
                    return None

            text = _extract_text(msg)
            if not isinstance(text, str):
                print(f"[get_otp] warning: extracted message content is not a string (type={type(text)}) - using str() fallback")
                try:
                    text = str(text)
                except Exception:
                    text = ""

            # Try OTP-specific patterns first
            patterns = [
                r"OTP code is[:\\s]*([0-9]{4,8})",
                r"Your One[- ]Time Password.*?([0-9]{4,8})",
                r"Your OTP code is[:\\s]*([0-9]{4,8})",
                r"\\b([0-9]{4,8})\\b",
            ]
            for pat in patterns:
                try:
                    m = re.search(pat, text, flags=re.IGNORECASE | re.DOTALL)
                except TypeError as te:
                    print(f"[get_otp] regex TypeError on text type {type(text)}: {te}")
                    m = None
                if m:
                    code = m.group(1)
                    print(f"[get_otp] extracted OTP {code} after {attempts} attempts")
                    return code

            # debugging: show excerpt
            try:
                snippet = text.strip().replace('\n', ' ')[:600]
                print(f"[get_otp] no OTP found in message excerpt: {snippet}")
            except Exception:
                pass

            time.sleep(poll_interval)
        except Exception as e:
            print(f"[get_otp] transient error: {e}")
            try:
                time.sleep(poll_interval)
            except Exception:
                pass
            continue

    return None
