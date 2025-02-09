// Function to fetch NGO data from FastAPI backend
async function fetchNGOs() {
    const response = await fetch('http://localhost:8000/ngos');  // URL to the FastAPI endpoint
    const ngos = await response.json();  // Parse the JSON data
   

    const ngoList = document.getElementById('ngo-list');

    ngos.forEach(ngo => {
        // Create a card for each NGO
        const ngoCard = document.createElement('div');
        ngoCard.classList.add('ngo-card');

        // Add content to the NGO card
        ngoCard.innerHTML = `
    <h3>${ngo["NGO Name"]}</h3>
    <p><strong>Location:</strong> ${ngo["City"]}</p>
    <p><strong>Contact:</strong> ${ngo["Contact"]}</p>
    <p><strong>Email:</strong> ${ngo["Email"]}</p>
    <p><strong>Categories:</strong> ${ngo["categories"]}</p>
`;


        // Append the card to the NGO list container
        ngoList.appendChild(ngoCard);
    });
}

// Call the function when the page loads
document.addEventListener('DOMContentLoaded', fetchNGOs);
