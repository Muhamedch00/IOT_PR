
function initCombinedGraph() {
    const ctx = document.getElementById('combinedChart').getContext('2d');

    fetch('/api/data')
        .then(response => response.json())
        .then(data => {
            const labels = data.labels;
            const temps = data.temps;
            const hums = data.hums;

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Température (°C)',
                            data: temps,
                            borderColor: 'rgb(231, 76, 60)', // Red
                            backgroundColor: 'rgba(231, 76, 60, 0.2)',
                            yAxisID: 'y',
                            tension: 0.3,
                            fill: true
                        },
                        {
                            label: 'Humidité (%)',
                            data: hums,
                            borderColor: 'rgb(52, 152, 219)', // Blue
                            backgroundColor: 'rgba(52, 152, 219, 0.2)',
                            yAxisID: 'y1',
                            tension: 0.3,
                            fill: true
                        }
                    ]
                },
                options: {
                    responsive: true,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {
                                display: true,
                                text: 'Température (°C)'
                            },
                            grid: {
                                color: 'rgba(200, 200, 200, 0.1)'
                            }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Humidité (%)'
                            },
                            grid: {
                                drawOnChartArea: false, // only want the grid lines for one axis to show up
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error loading graph data:', error);
            alert('Error fetching data for the graph!');
        });
}

// Call the function when the page loads
document.addEventListener('DOMContentLoaded', initCombinedGraph);
