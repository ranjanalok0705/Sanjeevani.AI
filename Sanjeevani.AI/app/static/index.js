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

// Predict disaster
function setupPredictionForm() {
    const form = document.getElementById("prediction-form");
    form.addEventListener("submit", event => {
        event.preventDefault();
        const inputData = document.getElementById("input-data").value;

        fetch(`${API_BASE_URL}/predict/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: inputData }),
        })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById("prediction-result");
                resultDiv.innerHTML = `<p>Prediction: ${data.prediction}</p><p>Severity: ${data.severity}</p>`;
            })
            .catch(error => console.error("Error predicting disaster:", error));
    });
}

// Initializel̥
document.addEventListener("DOMContentLoaded", () => {
    loadNGOs();
    setupPredictionForm();
});
