// Initialize Bootstrap modals
const addTouristModal = new bootstrap.Modal(document.getElementById('addTouristModal'));
const addDestinationModal = new bootstrap.Modal(document.getElementById('addDestinationModal'));
const recordVisitModal = new bootstrap.Modal(document.getElementById('recordVisitModal'));

// Function to show the add tourist form
function showAddTouristForm() {
    addTouristModal.show();
}

// Function to show the add destination form
function showAddDestinationForm() {
    addDestinationModal.show();
}

// Function to show the record visit form
function showRecordVisitForm() {
    loadTouristsForVisit();
    loadDestinationsForVisit();
    recordVisitModal.show();
}

// Function to load tourists list
function loadTourists() {
    fetch('/api/tourists')
        .then(response => response.json())
        .then(tourists => {
            const touristsList = document.getElementById('touristsList');
            touristsList.innerHTML = '';
            
            tourists.forEach(tourist => {
                const touristItem = document.createElement('div');
                touristItem.className = 'tourist-item';
                touristItem.innerHTML = `
                    <h5>${tourist.name}</h5>
                    <p>Nationality: ${tourist.nationality}<br>
                    Age: ${tourist.age}</p>
                `;
                touristsList.appendChild(touristItem);
            });
        })
        .catch(error => console.error('Error loading tourists:', error));
}

// Function to load destinations list
function loadDestinations() {
    fetch('/api/destinations')
        .then(response => response.json())
        .then(destinations => {
            const destinationsList = document.getElementById('destinationsList');
            destinationsList.innerHTML = '';
            
            destinations.forEach(destination => {
                const destinationItem = document.createElement('div');
                destinationItem.className = 'destination-item';
                destinationItem.innerHTML = `
                    <h5>${destination.name}</h5>
                    <p>Location: ${destination.city}, ${destination.country}<br>
                    Price: $${destination.price}</p>
                `;
                destinationsList.appendChild(destinationItem);
            });
        })
        .catch(error => console.error('Error loading destinations:', error));
}

// Function to load tourists for visit form
function loadTouristsForVisit() {
    fetch('/api/tourists')
        .then(response => response.json())
        .then(tourists => {
            const touristSelect = document.getElementById('visitTourist');
            touristSelect.innerHTML = '<option value="">Select Tourist</option>';
            
            tourists.forEach(tourist => {
                const option = document.createElement('option');
                option.value = tourist.id;
                option.textContent = `${tourist.name} (${tourist.nationality})`;
                touristSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error loading tourists for visit:', error));
}

// Function to load destinations for visit form
function loadDestinationsForVisit() {
    fetch('/api/destinations')
        .then(response => response.json())
        .then(destinations => {
            const destinationSelect = document.getElementById('visitDestination');
            destinationSelect.innerHTML = '<option value="">Select Destination</option>';
            
            destinations.forEach(destination => {
                const option = document.createElement('option');
                option.value = destination.id;
                option.textContent = `${destination.name} (${destination.city}, ${destination.country})`;
                destinationSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error loading destinations for visit:', error));
}

// Handle tourist form submission
document.getElementById('addTouristForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const touristData = {
        name: document.getElementById('touristName').value,
        nationality: document.getElementById('touristNationality').value,
        age: parseInt(document.getElementById('touristAge').value)
    };

    fetch('/api/tourists', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(touristData)
    })
    .then(response => response.json())
    .then(data => {
        addTouristModal.hide();
        loadTourists();
        document.getElementById('addTouristForm').reset();
    })
    .catch(error => console.error('Error adding tourist:', error));
});

// Handle destination form submission
document.getElementById('addDestinationForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const destinationData = {
        name: document.getElementById('destinationName').value,
        city: document.getElementById('destinationCity').value,
        country: document.getElementById('destinationCountry').value,
        price: document.getElementById('destinationPrice').value
    };

    fetch('/api/destinations', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(destinationData)
    })
    .then(response => response.json())
    .then(data => {
        addDestinationModal.hide();
        loadDestinations();
        document.getElementById('addDestinationForm').reset();
    })
    .catch(error => console.error('Error adding destination:', error));
});

// Handle visit form submission
document.getElementById('recordVisitForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const visitData = {
        tourist_id: parseInt(document.getElementById('visitTourist').value),
        destination_id: parseInt(document.getElementById('visitDestination').value),
        rating: parseInt(document.getElementById('visitRating').value)
    };

    fetch('/api/visits', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(visitData)
    })
    .then(response => response.json())
    .then(data => {
        recordVisitModal.hide();
        document.getElementById('recordVisitForm').reset();
    })
    .catch(error => console.error('Error recording visit:', error));
});

// Load data when page loads
document.addEventListener('DOMContentLoaded', () => {
    loadTourists();
    loadDestinations();
}); 