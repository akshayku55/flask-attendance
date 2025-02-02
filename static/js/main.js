function toggleDarkMode() {
    document.body.classList.toggle("dark-mode");
}

function fetchAttendance() {
    let username = document.getElementById("username").value.trim();
    let password = document.getElementById("password").value.trim();
    let loading = document.getElementById("loading");
    let errorDiv = document.getElementById("error");
    let attendanceSection = document.getElementById("attendance-section");
    let screenshotContainer = document.getElementById("screenshot-container");

    if (!username || !password) {
        errorDiv.textContent = "Username and password are required!";
        errorDiv.classList.remove("hidden");
        return;
    }

    // Show loading state
    loading.classList.remove("hidden");
    errorDiv.classList.add("hidden");
    attendanceSection.classList.add("hidden");
    screenshotContainer.classList.add("hidden");

    fetch("/api/attendance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        loading.classList.add("hidden");

        if (data.error) {
            errorDiv.textContent = "Error: " + data.error;
            errorDiv.classList.remove("hidden");
        } else {
            document.getElementById("attendance").textContent = data.attendance;
            document.getElementById("screenshot").src = `data:image/png;base64,${data.screenshot}`;
            attendanceSection.classList.remove("hidden");
            screenshotContainer.classList.remove("hidden");
        }
    })
    .catch(error => {
        loading.classList.add("hidden");
        errorDiv.textContent = "Error retrieving attendance.";
        errorDiv.classList.remove("hidden");
    });
}
