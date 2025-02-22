document.addEventListener('DOMContentLoaded', function() {
    // Timeline chart
    const ctx = document.querySelector('.timeline-chart');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jun 5', 'Jun 6', 'Jun 7', 'Jun 8', 'Jun 9', 'Jun 10', 'Jun 11'],
            datasets: [{
                label: 'Positive',
                data: [20, 45, 60, 70, 75, 80, 85],
                borderColor: '#2e7d32',
                tension: 0.4
            }, {
                label: 'Negative',
                data: [80, 55, 40, 30, 25, 20, 15],
                borderColor: '#c62828',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}); 