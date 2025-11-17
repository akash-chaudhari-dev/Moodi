from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import random
from data.names import names as names_list  # list of names
from data.dates import dates as dob_list  # list of dates
from data.phone import phone as phone_list  # list of phone numbers
from data.gender import genders as gender_list

from Tools.generate_email import generate_temp_email
from Tools.get_otp import get_otp

# Same password for all
password = "yourpassword"

# URL of the login page
url = r"https://my.moodi.org/login"

# Set up the Edge driver
driver = webdriver.Edge()

# Global waits to slow the whole process (user requested slower, lots of sleeps)
WAIT_SHORT = 1.0
WAIT_MED = 1.0
WAIT_LONG = 4.0

def fill_input(driver, xpath_list, value, field_name, attempts=3, wait_between=None):
    if wait_between is None:
        wait_between = WAIT_SHORT
    for attempt in range(attempts):
        for xp in xpath_list:
            try:
                field = WebDriverWait(driver, 6).until(
                    EC.element_to_be_clickable((By.XPATH, xp))
                )
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", field)
                try:
                    field.click()
                except:
                    pass
                try:
                    field.clear()
                except:
                    pass
                field.send_keys(value)
                time.sleep(WAIT_SHORT)
                print(f"{field_name} '{value}' entered successfully! (attempt {attempt+1})")
                return True
            except Exception:
                continue
    time.sleep(wait_between)
    print(f"❌ Could not find or fill {field_name} after {attempts} attempts.")
    return False


def set_date_field(driver, xpath_list, value, field_name="Date of Birth"):
    """
    Robustly set a date-like input. Attempts:
      1) normal click/clear/send_keys + ENTER/TAB
      2) JS set value, remove readonly, dispatch input/change/focusout/blur
      3) open calendar and click the day cell matching the day in value

    Returns True if the visible input value matches `value` after attempts.
    """
    # helper to read current value
    def _get_value(el):
        try:
            return el.get_attribute("value") or ""
        except Exception:
            return ""

    day_part = None
    try:
        # value expected format dd/mm/yyyy
        day_part = str(int(value.split("/")[0]))
    except Exception:
        day_part = None

    attempts = 3
    for attempt in range(attempts):
        for xp in xpath_list:
            try:
                el = WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.XPATH, xp)))
            except Exception:
                continue

            # operate only once on this element
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)

                # if already set correctly, nothing to do
                cur = _get_value(el)
                if cur and cur.strip() == value:
                    print(f"{field_name} already has desired value '{value}'")
                    return True

                # robust clear first
                try:
                    el.click()
                except Exception:
                    pass
                try:
                    el.clear()
                except Exception:
                    pass
                try:
                    driver.execute_script("arguments[0].value = ''; arguments[0].dispatchEvent(new Event('input',{bubbles:true}));", el)
                except Exception:
                    pass
                try:
                    el.send_keys(Keys.CONTROL + 'a')
                    el.send_keys(Keys.DELETE)
                except Exception:
                    try:
                        el.send_keys(Keys.BACKSPACE * 10)
                    except Exception:
                        pass
                time.sleep(WAIT_SHORT / 2)

                # Preferred: JS set value exactly (prevents concatenation)
                try:
                    js = (
                        "arguments[0].removeAttribute('readonly');"
                        "arguments[0].focus();"
                        f"arguments[0].value = '{value}';"
                        "var ev = new Event('input', {bubbles:true}); arguments[0].dispatchEvent(ev);"
                        "var ev2 = new Event('change', {bubbles:true}); arguments[0].dispatchEvent(ev2);"
                        "arguments[0].blur();"
                    )
                    driver.execute_script(js, el)
                    time.sleep(WAIT_SHORT)
                    cur = _get_value(el)
                    if cur and cur.strip() == value:
                        # try to commit the value by sending Enter/Tab and re-dispatching events
                        try:
                            el.send_keys(Keys.ENTER)
                        except Exception:
                            pass
                        try:
                            el.send_keys(Keys.TAB)
                        except Exception:
                            pass
                        try:
                            driver.execute_script("var ev = new Event('input', {bubbles:true}); arguments[0].dispatchEvent(ev); var ev2 = new Event('change', {bubbles:true}); arguments[0].dispatchEvent(ev2); arguments[0].blur();", el)
                        except Exception:
                            pass
                        time.sleep(WAIT_SHORT / 2)
                        cur = _get_value(el)
                        if cur and cur.strip() == value:
                            print(f"{field_name} set via JS to '{value}' (attempt {attempt+1})")
                            return True
                except Exception:
                    pass

                # fallback: typing only if JS didn't work
                try:
                    el.click()
                except Exception:
                    pass
                try:
                    el.send_keys(value)
                    time.sleep(WAIT_SHORT)
                    try:
                        el.send_keys(Keys.ENTER)
                    except Exception:
                        pass
                    try:
                        el.send_keys(Keys.TAB)
                    except Exception:
                        pass
                    try:
                        driver.execute_script("var ev = new Event('input', {bubbles:true}); arguments[0].dispatchEvent(ev); var ev2 = new Event('change', {bubbles:true}); arguments[0].dispatchEvent(ev2); arguments[0].blur();", el)
                    except Exception:
                        pass
                except Exception:
                    pass

                cur = _get_value(el)
                if cur and cur.strip() == value:
                    print(f"{field_name} '{value}' entered successfully by typing (attempt {attempt+1})")
                    return True

                # Calendar click fallback: click visible day cell only when necessary
                if day_part:
                    # attempt to find calendar container that's visible
                    try:
                        containers = driver.find_elements(By.XPATH, "//div[contains(@class,'datepicker') or contains(@class,'calendar')]")
                    except Exception:
                        containers = []

                    # build xpaths for day within a container
                    found = False
                    for container in containers:
                        try:
                            # search inside this container for a day cell
                            for dx in [f".//td[normalize-space()='{day_part}']", f".//button[normalize-space()='{day_part}']", f".//div[contains(@class,'day') and normalize-space()='{day_part}']"]:
                                try:
                                    cell = container.find_element(By.XPATH, dx)
                                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", cell)
                                    try:
                                        cell.click()
                                    except Exception:
                                        try:
                                            driver.execute_script("arguments[0].click();", cell)
                                        except Exception:
                                            pass
                                    time.sleep(WAIT_SHORT)
                                    cur = _get_value(el)
                                    if cur and cur.strip() == value:
                                        # commit and ensure value persists
                                        try:
                                            el.send_keys(Keys.TAB)
                                        except Exception:
                                            pass
                                        try:
                                            driver.execute_script("var ev = new Event('input', {bubbles:true}); arguments[0].dispatchEvent(ev); var ev2 = new Event('change', {bubbles:true}); arguments[0].dispatchEvent(ev2); arguments[0].blur();", el)
                                        except Exception:
                                            pass
                                        time.sleep(WAIT_SHORT / 2)
                                        cur = _get_value(el)
                                        if cur and cur.strip() == value:
                                            print(f"{field_name} set by clicking calendar day '{day_part}'")
                                            return True
                                    found = True
                                    break
                                except Exception:
                                    continue
                        except Exception:
                            continue

                    # if no container found, try global day xpaths once
                    if not found:
                        for dx in [f"//td[normalize-space()='{day_part}']", f"//button[normalize-space()='{day_part}']", f"//div[contains(@class,'day') and normalize-space()='{day_part}']"]:
                            try:
                                cell = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, dx)))
                                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", cell)
                                try:
                                    cell.click()
                                except Exception:
                                    try:
                                        driver.execute_script("arguments[0].click();", cell)
                                    except Exception:
                                        pass
                                time.sleep(WAIT_SHORT)
                                cur = _get_value(el)
                                if cur and cur.strip() == value:
                                    print(f"{field_name} set by clicking calendar day '{day_part}'")
                                    return True
                            except Exception:
                                continue

            finally:
                # after operating on this element, if we've set value, return; otherwise try next xpath
                cur = _get_value(el)
                if cur and cur.strip() == value:
                    return True

        # short wait between attempts
        time.sleep(WAIT_SHORT)

    print(f"❌ Could not set {field_name} to '{value}' after {attempts} attempts")
    return False

def safe_click(driver, xpath_list, name="element", attempts=3, wait_between=None):
    if wait_between is None:
        wait_between = WAIT_SHORT
    for attempt in range(attempts):
        for xp in xpath_list:
            try:
                el = WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.XPATH, xp)))
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                try:
                    el.click()
                except Exception:
                    try:
                        driver.execute_script("arguments[0].click();", el)
                    except:
                        raise
                print(f"{name} clicked successfully! (attempt {attempt+1})")
                return True
            except Exception:
                continue
    time.sleep(wait_between)
    print(f"❌ Could not click {name} after {attempts} attempts.")
    return False

while True:
    # generate email automatically from API (no manual email entry)
    try:
        # generate_temp_email should return (email_address, mailbox_object, client)
        res = generate_temp_email()
        if isinstance(res, tuple) and len(res) == 3:
            temp_email, mailbox, client = res
            email_id = getattr(mailbox, 'id', None)
        elif isinstance(res, tuple) and len(res) == 2:
            temp_email, mailbox = res
            client = None
            email_id = getattr(mailbox, 'id', None)
        else:
            raise Exception(f"Unexpected return from generate_temp_email: {res}")
        email = temp_email
        print(f"Generated temp email: {email} (mailbox id: {email_id})")
    except Exception as e:
        print(f"Failed to generate temp email: {e}")
        time.sleep(2)
        continue

    driver.get(url)

    try:
        if not safe_click(driver, ["//button[contains(., 'Login with Email OTP')]", "//button[contains(., 'Login with Email')]"], name="Login with Email OTP"):
            print("Failed to click 'Login with Email OTP' button; skipping this email.")
            continue

        time.sleep(2)

        fill_input(driver, ["//input[@placeholder='Enter your email']", "//input[@type='email']"], email, "Email")

        if not safe_click(driver, ["//button[contains(text(),'Send OTP')]", "//button[contains(.,'Send OTP')]"] , name="Send OTP"):
            print("Failed to click 'Send OTP' button; skipping this email.")
            continue
        time.sleep(3)

        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            driver.switch_to.alert.accept()
            print("Alert dismissed successfully!")
        except:
            pass

        # Prepare random profile data early so we can verify page state after OTP verification
        random_name = random.choice(names_list)
        index_of_name = names_list.index(random_name)

        gender_of_random_name = gender_list[index_of_name]
        if gender_of_random_name == "M":
            Gender = "Male"
        else:
            Gender = "Female"

        random_dob = random.choice(dob_list)
        # dob_list entries expected as 'ddmmyyyy' or similar; build 'dd/mm/yyyy'
        random_dob = random_dob[:2] + "/" + random_dob[2:4] + "/" + random_dob[4:]
        random_phone = random.choice(phone_list)

        # Fetch OTP automatically using the email_id from the API.
        otp = None
        try:
            # First try: 120s
            otp = get_otp(mailbox, client, timeout=120)
            if not otp:
                print("OTP not received within 120s, retrying an additional 60s...")
                otp = get_otp(mailbox, client, timeout=60)
            if otp:
                print(f"Fetched OTP automatically: {otp}")
            else:
                print("OTP not received; skipping this account.")
                continue
        except Exception as e:
            print(f"Automatic OTP fetch failed: {e}")
            continue

        fill_input(driver, ["//input[@placeholder='Enter OTP']", "//input[@name='otp']"], otp, "OTP")

        if not safe_click(driver, ["//button[contains(text(),'Verify OTP')]", "//button[contains(.,'Verify OTP')]" ] , name="Verify OTP"):
            print("Failed to click 'Verify OTP' button; skipping this email.")
            continue
        time.sleep(3)
        print("OTP verification attempted - checking post-verification page state...")

        time.sleep(WAIT_MED)

        # After verification, the registration form (including Full Name input) should appear.
        # Confirm the 'Full Name' input exists and optionally that it contains the name we plan to enter.
        name_xpaths = ["//input[@placeholder='Full Name']", "//input[@name='name']"]
        name_found = False
        try:
            # try to find the name input quickly
            time.sleep(WAIT_SHORT)
            el_name = WebDriverWait(driver, 6).until(
    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Full Name']"))
)
            name_found = True
            cur_val = (el_name.get_attribute('value') or '').strip()
            if cur_val:
                print(f"Name input present with value '{cur_val}'")
        except Exception:
            name_found = False

        # If the name input did not appear, wait 60s and attempt a single 'Resend OTP' then retry OTP
        if not name_found:
            print("Name input not found after OTP verification; waiting 60s then attempting to resend OTP and retry verification.")
            time.sleep(40)
            resend_xpaths = ["//button[contains(.,'Resend OTP')]", "//button[contains(.,'Resend') and contains(.,'OTP')]", "//button[contains(.,'Resend')]"]
            if safe_click(driver, resend_xpaths, name="Resend OTP"):
                # try fetch new OTP and verify once
                try:
                    new_otp = get_otp(mailbox, client, timeout=120)
                    if not new_otp:
                        print("Resend attempted but OTP not received; skipping this account.")
                        continue
                    print(f"Fetched new OTP after resend: {new_otp}")
                    fill_input(driver, ["//input[@placeholder='Enter OTP']", "//input[@name='otp']"], new_otp, "OTP (resend)")
                    if not safe_click(driver, ["//button[contains(text(),'Verify OTP')]", "//button[contains(.,'Verify OTP')]"] , name="Verify OTP (after resend)"):
                        print("Failed to click 'Verify OTP' after resend; skipping this email.")
                        continue
                    time.sleep(2)
                except Exception as e:
                    print(f"Error during resend OTP flow: {e}")
                    continue
            else:
                print("Resend OTP button not found or not clickable; skipping this account.")
                continue

        fill_input(driver, ["//input[@placeholder='Full Name']", "//input[@name='name']"], random_name, "Full Name")
        # Use robust setter for date fields because some datepickers ignore plain send_keys
        set_date_field(driver, ["//input[@placeholder='DOB (dd/mm/yyyy)']", "//input[@name='dob']"], random_dob, "Date of Birth")
        fill_input(driver, ["//input[@placeholder='Phone']", "//input[@name='phone']"], random_phone, "Phone Number")
        fill_input(driver, ["//input[@placeholder='Select or Enter Gender']", "//input[@name='gender']"], f"{Gender}", "Gender")

        safe_click(driver, ["//button[contains(text(),'NEXT')]"] , name="NEXT after Gender")

        fill_input(driver, ["//input[@placeholder='Select or Enter State/UT']", "//input[@name='state']"], "Maharashtra", "State")
        fill_input(driver, ["//input[@placeholder='Select or Enter City']", "//input[@name='city']"], "Aurangabad", "City")
        fill_input(driver, ["//input[@placeholder='Select or Enter College']", "//input[@name='college']"], "csmss", "College")
        fill_input(driver, ["//input[@placeholder='Select or Enter Stream']", "//input[@name='stream']"], "Engineering", "Stream")
        fill_input(driver, ["//input[@placeholder='Select or Enter Year of Study']", "//input[@name='year']"], "Second", "Year")

        safe_click(driver, ["//button[contains(text(),'NEXT')]"] , name="NEXT after Year")

        if safe_click(driver, ["//button[contains(text(),'NEXT')]", "//button[contains(.,'NEXT')]"] , name="NEXT"):
            time.sleep(1)
            safe_click(driver, ["//button[contains(text(),'NEXT')]", "//button[contains(.,'NEXT')]"] , name="NEXT (second click)")

        fill_input(driver, ["//input[@placeholder='e.g. CCP138468']", "//input[@name='referral']"], "CCP514843", "Referral Code")

        safe_click(driver, ["//button[contains(text(),'Submit')]", "//button[contains(.,'Submit')]"] , name="Submit")

        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(1)

    except Exception as e:
        print(f"Unhandled error while processing '{email}': {e}")
        try:
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(1)
        except:
            pass
        continue

    driver.quit()