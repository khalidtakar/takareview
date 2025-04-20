document.addEventListener('DOMContentLoaded', function() {
    // Initialize Radar Chart with improved configuration
    const radarCtx = document.querySelector('.radar-chart');
    if (radarCtx) {
        new Chart(radarCtx, {
            type: 'radar',
            data: {
                labels: ['Positive', 'Negative', 'Neutral', 'Confidence', 'Accuracy', 'Consistency'],
                datasets: [{
                    label: 'Sentiment Analysis Metrics',
                    data: [85, 75, 65, 90, 80, 85],
                    borderColor: 'rgba(80, 156, 244, 1)',  // Bright blue
                    backgroundColor: 'rgba(80, 156, 244, 0.2)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(80, 156, 244, 1)',
                    pointBorderColor: '#ggg',
                    pointHoverBackgroundColor: '#ggg',
                    pointHoverBorderColor: 'rgba(80, 156, 244, 1)'
                }]
            },
            options: {
                elements: {
                    line: {
                        borderWidth: 5
                    }
                },
                scales: {
                    r: {
                        angleLines: {
                            color: 'rgba(20, 20, 20, 0.2)'
                        },
                        grid: {
                            color: 'rgba(20, 20, 20, 0.2)'
                        },
                        pointLabels: {
                            color: 'var(--text-color)',
                            font: {
                                size: 12
                            }
                        },
                        ticks: {
                            backdropColor: 'transparent',
                            color: 'var(--text-color)',
                            callback: function(value) {
                                return value + '%';
                            }
                        },
                        suggestedMin: 0,
                        suggestedMax: 100
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    // Initialize Trend Chart with time range filter
    const trendCtx = document.getElementById('trendChart');
    let trendChart;

    function updateTrendChart(timeRange) {
        const data = getTrendData(timeRange);
        
        if (trendChart) {
            trendChart.destroy();
        }

        trendChart = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Positive',
                        data: data.positive,
                        borderColor: 'rgb(80, 250, 123)',
                        tension: 0.4,
                        fill: false
                    },
                    {
                        label: 'Negative',
                        data: data.negative,
                        borderColor: 'rgb(255, 85, 85)',
                        tension: 0.4,
                        fill: false
                    },
                    {
                        label: 'Neutral',
                        data: data.neutral,
                        borderColor: 'rgb(189, 147, 249)',
                        tension: 0.4,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            color: 'rgba(20, 20, 20, 0.1)'
                        },
                        ticks: {
                            color: 'var(--text-color)',
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(20, 20, 20, 0.1)'
                        },
                        ticks: {
                            color: 'var(--text-color)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: 'var(--text-color)'
                        }
                    }
                }
            }
        });
    }

    // Handle time range filter changes
    const timeRangeFilter = document.getElementById('timeRangeFilter');
    if (timeRangeFilter) {
        timeRangeFilter.addEventListener('change', function() {
            updateTrendChart(this.value);
        });

        // Initial chart render
        updateTrendChart('daily');
    }

    // Get the modal elements
    const modal = document.getElementById('sentimentDetailsModal');
    const viewDetailsBtn = document.querySelector('.btn-primary');
    const closeModal = document.querySelector('.close-modal');

    // Open modal when clicking View Details
    if (viewDetailsBtn) {
        viewDetailsBtn.addEventListener('click', function(e) {
            e.preventDefault();
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
        });
    }

    // Close modal when clicking X
    if (closeModal) {
        closeModal.addEventListener('click', function() {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto'; // Restore scrolling
        });
    }

    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    });

    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display === 'block') {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    });
});

// Function to get trend data based on time range
function getTrendData(timeRange) {
    // This should be replaced with actual data from your backend
    return trendData[timeRange] || trendData;
} 