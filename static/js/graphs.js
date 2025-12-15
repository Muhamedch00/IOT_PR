
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
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('combinedChart')) {
        initCombinedGraph();
    }
});

function initGraph(type) {
    const canvasId = type === 'temp' ? 'tempChart' : 'humChart';
    const canvas = document.getElementById(canvasId);

    if (!canvas) return; // Exit if canvas doesn't exist on this page

    const ctx = canvas.getContext('2d');

    fetch('/api/data')
        .then(response => response.json())
        .then(data => {
            const labels = data.labels;
            const values = type === 'temp' ? data.temps : data.hums;
            const label = type === 'temp' ? 'Température (°C)' : 'Humidité (%)';
            // Neon Red for Temp, Neon Blue for Hum to match theme
            const color = type === 'temp' ? 'rgb(255, 77, 77)' : 'rgb(0, 242, 255)';
            const bgColor = type === 'temp' ? 'rgba(255, 77, 77, 0.2)' : 'rgba(0, 242, 255, 0.2)';

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: label,
                        data: values,
                        borderColor: color,
                        backgroundColor: bgColor,
                        borderWidth: 2,
                        tension: 0.4, // Smoother curve
                        fill: true,
                        pointBackgroundColor: color,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: '#fff', // White text for dark mode
                                font: {
                                    family: 'Orbitron'
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: '#a0a0a0',
                                font: {
                                    family: 'Roboto'
                                }
                            }
                        },
                        x: {
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: '#a0a0a0',
                                font: {
                                    family: 'Roboto'
                                },
                                maxTicksLimit: 10
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error loading graph data:', error);
        });
}
