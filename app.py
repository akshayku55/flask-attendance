import time
import base64
from datetime import datetime
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

app = Flask(__name__)

ERP_URL = "https://login.cgc.ac.in"
ATTENDANCE_URL = "https://student.cgc.ac.in/Attendance.aspx"

def get_attendance(username, password):
    """
    Logs into the ERP, fetches attendance, and takes a screenshot.
    """

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Selenium in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)

    try:
        # ✅ 1. Open Login Page
        driver.get(ERP_URL)
        time.sleep(2)

        # ✅ 2. Enter Credentials
        driver.find_element(By.ID, "txtuser").send_keys(username)
        driver.find_element(By.ID, "txtpass").send_keys(password)
        driver.find_element(By.ID, "txtpass").send_keys(Keys.RETURN)
        time.sleep(3)

        # ✅ 3. Navigate to Attendance Page
        driver.get(ATTENDANCE_URL)
        time.sleep(3)

        # ✅ 4. Extract Attendance Data
        try:
            attendance_div = driver.find_element(By.CSS_SELECTOR, "div.attendance-count")
            attendance_text = attendance_div.text.strip() or "N/A"
        except:
            attendance_text = "N/A"

        # ✅ 5. Capture Screenshot
        screenshot_png = driver.get_screenshot_as_png()
        screenshot_b64 = base64.b64encode(screenshot_png).decode("utf-8")

        return {"attendance": attendance_text, "screenshot": screenshot_b64}

    finally:
        driver.quit()

@app.route("/api/attendance", methods=["POST"])
def api_attendance():
    """
    Accepts ERP credentials from frontend and fetches attendance dynamically.
    """
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        result = get_attendance(username, password)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return "Attendance API is Running"

if __name__ == "__main__": 
    app.run(debug=True, host="0.0.0.0", port=5000)
