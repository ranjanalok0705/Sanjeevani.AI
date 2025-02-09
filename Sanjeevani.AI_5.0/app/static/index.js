// URL to the FastAPI backend
const API_BASE_URL = "http://127.0.0.1:8000";

// Load NGO data
function loadNGOs() {
    fetch(`${API_BASE_URL}/ngos/`)
        .then(response => response.json())
        .then(data => {
            const ngoList = document.getElementById("ngo-list");
            ngoList.innerHTML = "";
            data.forEach(ngo => {
                const ngoCard = document.createElement("div");
                ngoCard.classList.add("ngo-card");
                ngoCard.innerHTML = `
                    <h3>${ngo.name}</h3>
                    <p>Location: ${ngo.location}</p>
                    <p>Contact: ${ngo.contact}</p>
                    <p>Services: ${ngo.services}</p>
                `;
                ngoList.appendChild(ngoCard);
            });
        })
        .catch(error => console.error("Error fetching NGOs:", error));
}


// Initialize
document.addEventListener("DOMContentLoaded", () => {
    loadNGOs();
});
// document.getElementById("get-location").addEventListener("click", function() {
//     if (navigator.geolocation) {
//         navigator.geolocation.getCurrentPosition(function(position) {
//             const latitude = position.coords.latitude;
//             const longitude = position.coords.longitude;

//             // Display the location
//             document.getElementById("location-result").innerHTML = 
//                 `<p>Latitude: ${latitude}, Longitude: ${longitude}</p>`;

//             // Optionally, send this data to the server (FastAPI)
//             fetch("/location", {
//                 method: "POST",
//                 headers: {
//                     "Content-Type": "application/json",
//                 },
//                 body: JSON.stringify({
//                     latitude: latitude,
//                     longitude: longitude
//                 })
//             }).then(response => response.json())
//               .then(data => console.log("Location sent to server:", data))
//               .catch(err => console.error("Error sending location to server:", err));

//         }, function(error) {
//             // Handle errors
//             document.getElementById("location-result").innerHTML = `<p>Error: ${error.message}</p>`;
//         });
//     } else {
//         document.getElementById("location-result").innerHTML = "<p>Geolocation is not supported by this browser.</p>";
//     }
// });

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("filterform");
    if (!form) {  // Check if form exists
        console.error("Form not found! Ensure the form exists in the DOM.");
        return;}
    form.addEventListener("submit", function (event) {
        const selectedSeverity = document.getElementById("severity").value;
        localStorage.setItem("selectedSeverity", selectedSeverity); // Store in localStorage
        console.log("Stored Severity:", selectedSeverity);
    });
});
document.addEventListener("DOMContentLoaded", function () {
    const requestButtons = document.querySelectorAll(".request");

    requestButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const row = button.closest("tr"); // Get the closest table row

            if (!row) return; // Exit if row not found

            // Extract NGO details from table row
            const ngoId = row.cells[0].innerText;
            const ngoName = row.cells[1].innerText;
            const city = row.cells[2].innerText;
            const contact = row.cells[3].innerText;
            const email = row.cells[4].innerText;
            const category = row.cells[5].innerText;

            // Retrieve stored severity from localStorage
            const selectedSeverity = localStorage.getItem("selectedSeverity");

            if (!selectedSeverity) {
                alert("Please select a severity level before submitting.");
                return;
            }

            // Dummy User Details (Replace these with actual values)
            const phoneNumber = "USER_PHONE_NUMBER";
            const username = "USER_USERNAME";
            const location = "USER_LOCATION";

            // Log Data for Debugging
            console.log("NGO Details:", { ngoId, ngoName, city, contact, email, category });
            console.log("User Details:", { phoneNumber, username, location, severity: selectedSeverity });

            // Send the data to the backend
            fetch("/send-notification/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    org_email: email,
                    ngo_id: ngoId,
                    severity: selectedSeverity, // Include stored severity
                    phone_number: phoneNumber,
                    username: username,
                    location: location,
                }),
            })
            .then(response => response.json())
            .then(data => {
                alert("Notification sent successfully.");
            })
            .catch(error => {
                console.error("Error:", error);
            });
        });
    });
});
localStorage.removeItem("selectedSeverity");
