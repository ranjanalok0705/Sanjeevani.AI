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
document.getElementById("get-location").addEventListener("click", function() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;

            // Display the location
            document.getElementById("location-result").innerHTML = 
                `<p>Latitude: ${latitude}, Longitude: ${longitude}</p>`;

            // Optionally, send this data to the server (FastAPI)
            fetch("/location", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    latitude: latitude,
                    longitude: longitude
                })
            }).then(response => response.json())
              .then(data => console.log("Location sent to server:", data))
              .catch(err => console.error("Error sending location to server:", err));

        }, function(error) {
            // Handle errors
            document.getElementById("location-result").innerHTML = `<p>Error: ${error.message}</p>`;
        });
    } else {
        document.getElementById("location-result").innerHTML = "<p>Geolocation is not supported by this browser.</p>";
    }
});
