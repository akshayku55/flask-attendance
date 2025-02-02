import time
import base64
from datetime import datetime

from flask import Flask, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

app = Flask(__name__)

# -------------------------------------------------------------
# 1. Hard-coded Credentials & URLs
# -------------------------------------------------------------
USERNAME = "2338393"
PASSWORD = "akshay@200444"
ERP_URL = "https://login.cgc.ac.in"
ATTENDANCE_URL = "https://student.cgc.ac.in/Attendance.aspx"


def get_attendance():
    """
    Logs into the ERP using Selenium in headless mode,
    scrapes attendance, and takes a screenshot.
    Returns (attendance_text, screenshot_base64).
    """

    # Configure Chrome in headless mode
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-notifications")
    options.add_argument("--no-sandbox")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(options=options)

    try:
        # 1. Log in
        driver.get(ERP_URL)
        time.sleep(2)  # or use explicit waits if needed

        driver.find_element(By.ID, "txtuser").send_keys(USERNAME)
        driver.find_element(By.ID, "txtpass").send_keys(PASSWORD)
        driver.find_element(By.ID, "txtpass").send_keys(Keys.RETURN)
        time.sleep(3)

        # 2. Navigate to the attendance page
        driver.get(ATTENDANCE_URL)
        time.sleep(3)

        # 3. Scrape attendance count
        try:
            attendance_div = driver.find_element(By.CSS_SELECTOR, "div.attendance-count")
            attendance_text = attendance_div.text.strip() or "N/A"
        except Exception as e:
            print(f"Error scraping attendance: {e}")
            attendance_text = "N/A"

        # 4. Take a screenshot and convert to Base64
        screenshot_png = driver.get_screenshot_as_png()
        screenshot_b64 = base64.b64encode(screenshot_png).decode("utf-8")

        return attendance_text, screenshot_b64

    finally:
        driver.quit()


# -------------------------------------------------------------
# 2. Flask Routes
# -------------------------------------------------------------
@app.route("/")
def index():
    """
    Serves a basic HTML page with a button that fetches attendance
    data from the /api/attendance endpoint.
    """
    return render_template("index.html")


@app.route("/api/attendance")
def api_attendance():
    """
    Endpoint to get attendance info (in JSON form).
    Called by JavaScript in 'index.html'.
    """
    try:
        attendance_text, screenshot_b64 = get_attendance()
        return jsonify({
            "attendance": attendance_text,
            "screenshot": screenshot_b64
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Host on 0.0.0.0 to allow access from other devices on the same network
    app.run(debug=True, host="0.0.0.0", port=5000)
