function updateDashboard() {
    fetch('/latest/')
        .then(response => response.json())
        .then(data => {
            document.getElementById('temp-val').textContent = data.temperature + ' °C';
            document.getElementById('hum-val').textContent = data.humidity + ' %';

            // Update time for both
            const timeString = timeAgo(data.timestamp);
            document.getElementById('temp-time').textContent = timeString;
            document.getElementById('hum-time').textContent = timeString;
        })
        .catch(error => console.error('Error fetching data:', error));
}

function timeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);

    let interval = Math.floor(seconds / 86400);
    if (interval >= 1) return "il y a " + interval + " jours";

    interval = Math.floor(seconds / 3600);
    if (interval >= 1) return "il y a " + interval + " heures";

    interval = Math.floor(seconds / 60);
    if (interval >= 1) return "il y a " + interval + " minutes";

    return "il y a quelques secondes";
}

// Handle manual data entry
document.getElementById('data-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const temp = document.getElementById('temp-input').value;
    const hum = document.getElementById('hum-input').value;

    fetch('/api/post', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            temp: temp,
            hum: hum
        })
    })
        .then(response => {
            if (response.ok) {
                alert('Données envoyées avec succès !');
                document.getElementById('data-form').reset();
                updateDashboard(); // Refresh immediately
            } else {
                alert('Erreur lors de l\'envoi des données.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Erreur réseau.');
        });
});

// Update every 5 seconds
setInterval(updateDashboard, 5000);

// Initial call
updateDashboard();

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
