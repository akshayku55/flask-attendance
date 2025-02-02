import time
import base64
from flask import Flask, request, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

app = Flask(__name__, static_folder="static", template_folder="templates")

ERP_URL = "https://login.cgc.ac.in"
ATTENDANCE_URL = "https://student.cgc.ac.in/Attendance.aspx"

def get_attendance(username, password):
    """
    Logs into the ERP, fetches attendance, and takes a screenshot.
    Raises an exception if the credentials are invalid.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    try:
        # 1. Open Login Page
        driver.get(ERP_URL)
        time.sleep(2)

        # 2. Enter Credentials
        driver.find_element(By.ID, "txtuser").send_keys(username)
        driver.find_element(By.ID, "txtpass").send_keys(password)
        driver.find_element(By.ID, "txtpass").send_keys(Keys.RETURN)
        time.sleep(3)

        # OPTIONAL: Check if login failed (customize this check based on the actual page error)
        if "invalid" in driver.page_source.lower():
            raise Exception("Invalid credentials provided.")

        # 3. Navigate to Attendance Page
        driver.get(ATTENDANCE_URL)
        time.sleep(3)

        # 4. Extract Attendance Data
        try:
            attendance_div = driver.find_element(By.CSS_SELECTOR, "div.attendance-count")
            attendance_text = attendance_div.text.strip() or "N/A"
        except Exception:
            attendance_text = "N/A"

        # 5. Capture Screenshot
        screenshot_png = driver.get_screenshot_as_png()
        screenshot_b64 = base64.b64encode(screenshot_png).decode("utf-8")

        return {"attendance": attendance_text, "screenshot": screenshot_b64}
    finally:
        driver.quit()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/attendance", methods=["POST"])
def api_attendance():
    """
    API endpoint that accepts JSON credentials and returns attendance data.
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Roll Number and password are required"}), 400

    try:
        result = get_attendance(username, password)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # When deploying on Railway, set host and port appropriately.
    app.run(debug=True, host="0.0.0.0", port=5000)
