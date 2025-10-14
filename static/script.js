let allTrips = [];
let trips = [];
const API_BASE = "/api"; // Flask backend URL

async function loadData() {
    try {
        const res = await fetch(`${API_BASE}/trips`);
        const data = await res.json();

        // Convert datetime strings to Date objects
        allTrips = data.map(trip => ({
            ...trip,
            pickup_datetime: new Date(trip.pickup_datetime),
            dropoff_datetime: new Date(trip.dropoff_datetime),
            passenger_count: parseInt(trip.passenger_count),
            trip_duration: parseInt(trip.trip_duration)
        }));

        trips = [...allTrips];

        // Update visualizations and table
        updateStats();
        createDurationChart();
        createPassengerCharts();
        createTimeChart();
        createMapChart();
        populateTable();
        setupTabs();
        setupFilters();
        setupSorting();
        updateTripCount();

    } catch (err) {
        console.error("Error loading trips:", err);
        alert("Failed to fetch data from API");
    }
}


// Color palette
const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1'];

// Global variables
let charts = {};
let currentSort = { field: null, direction: 'asc' };

// Parse CSV data
function parseCSV(csvData) {
    const lines = csvData.trim().split('\n');
    
    return lines.slice(1).map(line => {
        const values = line.split(',');
        return {
            id: values[0],
            vendor_id: parseInt(values[1]),
            pickup_datetime: new Date(values[2]),
            dropoff_datetime: new Date(values[3]),
            passenger_count: parseInt(values[4]),
            pickup_longitude: parseFloat(values[5]),
            pickup_latitude: parseFloat(values[6]),
            dropoff_longitude: parseFloat(values[7]),
            dropoff_latitude: parseFloat(values[8]),
            store_and_fwd_flag: values[9],
            trip_duration: parseInt(values[10])
        };
    });
}

// Initialize the dashboard
$(document).ready(function() {
    loadData();
});

// Update statistics cards
function updateStats() {
    const totalTrips = trips.length;
    const totalDuration = trips.reduce((sum, trip) => sum + trip.trip_duration, 0);
    const totalPassengers = trips.reduce((sum, trip) => sum + trip.passenger_count, 0);
    
    $('#stat-total-trips').text(totalTrips);
    $('#stat-avg-duration').text(Math.round(totalDuration / totalTrips) + 's');
    $('#stat-avg-passengers').text((totalPassengers / totalTrips).toFixed(1));
    $('#stat-routes').text(totalTrips);
}

// Create duration distribution chart
function createDurationChart() {
    const ctx = $('#chart-duration')[0].getContext('2d');
    
    const durationData = trips.map((trip, index) => ({
        label: `Trip ${index + 1}`,
        duration: Math.round(trip.trip_duration / 60),
        durationSec: trip.trip_duration
    })).sort((a, b) => a.duration - b.duration);
    
    if (charts.duration) charts.duration.destroy();
    
    charts.duration = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: durationData.map(d => d.label),
            datasets: [{
                label: 'Duration (minutes)',
                data: durationData.map(d => d.duration),
                backgroundColor: durationData.map((_, i) => colors[i % colors.length]),
                borderColor: durationData.map((_, i) => colors[i % colors.length]),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const item = durationData[context.dataIndex];
                            return `Duration: ${item.duration} min (${item.durationSec}s)`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Duration (min)' }
                },
                x: {
                    ticks: { maxRotation: 45, minRotation: 45 }
                }
            }
        }
    });
}

// Create passenger count charts
function createPassengerCharts() {
    const passengerCounts = {};
    trips.forEach(trip => {
        passengerCounts[trip.passenger_count] = (passengerCounts[trip.passenger_count] || 0) + 1;
    });
    
    const passengerData = Object.entries(passengerCounts).map(([count, trips]) => ({
        passengers: `${count} passenger${count === '1' ? '' : 's'}`,
        count: trips
    }));
    
    // Pie chart
    const ctxPie = $('#chart-passengers-pie')[0].getContext('2d');
    if (charts.passengersPie) charts.passengersPie.destroy();
    
    charts.passengersPie = new Chart(ctxPie, {
        type: 'pie',
        data: {
            labels: passengerData.map(d => d.passengers),
            datasets: [{
                data: passengerData.map(d => d.count),
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: getComputedStyle(document.documentElement).getPropertyValue('--color-card')
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.parsed} trips`;
                        }
                    }
                }
            }
        }
    });
    
    // Bar chart
    const ctxBar = $('#chart-passengers-bar')[0].getContext('2d');
    if (charts.passengersBar) charts.passengersBar.destroy();
    
    charts.passengersBar = new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: passengerData.map(d => d.passengers),
            datasets: [{
                label: 'Number of Trips',
                data: passengerData.map(d => d.count),
                backgroundColor: passengerData.map((_, i) => colors[i % colors.length]),
                borderColor: passengerData.map((_, i) => colors[i % colors.length]),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Number of Trips' }
                }
            }
        }
    });
}

// Create time of day chart
function createTimeChart() {
    const ctx = $('#chart-time')[0].getContext('2d');
    
    const hourCounts = {};
    trips.forEach(trip => {
        const hour = trip.pickup_datetime.getHours();
        hourCounts[hour] = (hourCounts[hour] || 0) + 1;
    });
    
    const timeData = Object.entries(hourCounts)
        .map(([hour, count]) => ({ hour: `${hour}:00`, trips: count }))
        .sort((a, b) => parseInt(a.hour) - parseInt(b.hour));
    
    if (charts.time) charts.time.destroy();
    
    charts.time = new Chart(ctx, {
        type: 'line',
        data: {
            labels: timeData.map(d => d.hour),
            datasets: [{
                label: 'Number of Trips',
                data: timeData.map(d => d.trips),
                borderColor: '#8884d8',
                backgroundColor: 'rgba(136, 132, 216, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 5,
                pointBackgroundColor: '#8884d8',
                pointBorderColor: '#8884d8',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: true, position: 'top' }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Number of Trips' }
                },
                x: {
                    title: { display: true, text: 'Time of Day' }
                }
            }
        }
    });
}

// Create pickup location scatter chart
function createMapChart() {
    const ctx = $('#chart-map')[0].getContext('2d');
    
    const mapData = trips.map((trip, index) => ({
        x: (trip.pickup_longitude + 74.02) * 1000,
        y: (trip.pickup_latitude - 40.7) * 1000,
        label: `Trip ${index + 1}`,
        passengers: trip.passenger_count
    }));
    
    if (charts.map) charts.map.destroy();
    
    charts.map = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Pickup Locations',
                data: mapData.map(d => ({ x: d.x, y: d.y })),
                backgroundColor: mapData.map(d => colors[d.passengers % colors.length]),
                borderColor: mapData.map(d => colors[d.passengers % colors.length]),
                borderWidth: 1,
                pointRadius: 8,
                pointHoverRadius: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: true, position: 'top' },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const item = mapData[context.dataIndex];
                            return [item.label, `Passengers: ${item.passengers}`];
                        }
                    }
                }
            },
            scales: {
                x: { title: { display: true, text: 'Longitude (normalized)' } },
                y: { title: { display: true, text: 'Latitude (normalized)' } }
            }
        }
    });
}

// Populate data table
function populateTable() {
    const tbody = $('#table-body');
    tbody.empty();
    
    trips.forEach(trip => {
        const row = $('<tr>').html(`
            <td>${trip.id}</td>
            <td>Vendor ${trip.vendor_id}</td>
            <td>${trip.pickup_datetime.toLocaleString()}</td>
            <td>${Math.round(trip.trip_duration / 60)} min</td>
            <td>${trip.passenger_count}</td>
            <td>${trip.pickup_latitude.toFixed(4)}, ${trip.pickup_longitude.toFixed(4)}</td>
        `);
        tbody.append(row);
    });
}

// Setup tab switching
function setupTabs() {
    $('.tab-trigger').on('click', function() {
        const tabName = $(this).data('tab');
        
        $('.tab-trigger').removeClass('active');
        $('.tab-content').removeClass('active');
        
        $(this).addClass('active');
        $(`#tab-${tabName}`).addClass('active');
        
        // Update chart on tab switch
        if (charts[tabName]) {
            charts[tabName].update();
        }
    });
}

// Setup filters
function setupFilters() {
    $('#search-id, #filter-vendor, #filter-passengers, #filter-duration, #filter-month').on('input change', applyFilters);
    
    $('#reset-filters').on('click', function() {
        $('#search-id').val('');
        $('#filter-vendor').val('');
        $('#filter-passengers').val('');
        $('#filter-duration').val('');
        $('#filter-month').val('');
        applyFilters();
    });
}

// Apply filters
function applyFilters() {
    const searchId = $('#search-id').val().toLowerCase();
    const filterVendor = $('#filter-vendor').val();
    const filterPassengers = $('#filter-passengers').val();
    const filterDuration = $('#filter-duration').val();
    const filterMonth = $('#filter-month').val();
    
    trips = allTrips.filter(trip => {
        // Search by ID
        if (searchId && !trip.id.toLowerCase().includes(searchId)) {
            return false;
        }
        
        // Filter by vendor
        if (filterVendor && trip.vendor_id !== parseInt(filterVendor)) {
            return false;
        }
        
        // Filter by passengers
        if (filterPassengers) {
            const passengerCount = parseInt(filterPassengers);
            if (passengerCount === 6 && trip.passenger_count < 6) {
                return false;
            } else if (passengerCount < 6 && trip.passenger_count !== passengerCount) {
                return false;
            }
        }
        
        // Filter by duration
        if (filterDuration) {
            const [min, max] = filterDuration.split('-').map(Number);
            if (trip.trip_duration < min || (max && trip.trip_duration > max)) {
                return false;
            }
        }
        
        // Filter by month
        if (filterMonth) {
            const month = parseInt(filterMonth);
            if (trip.pickup_datetime.getMonth() !== month) {
                return false;
            }
        }
        
        return true;
    });
    
    // Update everything with filtered data
    updateStats();
    updateCharts();
    populateTable();
    updateTripCount();
}

// Update all charts
function updateCharts() {
    createDurationChart();
    createPassengerCharts();
    createTimeChart();
    createMapChart();
}

// Setup table sorting
function setupSorting() {
    $('.sortable').on('click', function() {
        const field = $(this).data('sort');
        
        // Toggle sort direction
        if (currentSort.field === field) {
            currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
        } else {
            currentSort.field = field;
            currentSort.direction = 'asc';
        }
        
        // Remove sorting classes from all headers
        $('.sortable').removeClass('asc desc');
        
        // Add sorting class to current header
        $(this).addClass(currentSort.direction);
        
        // Sort and update table
        sortTrips();
        populateTable();
    });
}

// Sort trips
function sortTrips() {
    trips.sort((a, b) => {
        let valueA = a[currentSort.field];
        let valueB = b[currentSort.field];
        
        // Handle dates
        if (valueA instanceof Date) {
            valueA = valueA.getTime();
            valueB = valueB.getTime();
        }
        
        // Handle strings
        if (typeof valueA === 'string') {
            valueA = valueA.toLowerCase();
            valueB = valueB.toLowerCase();
        }
        
        if (currentSort.direction === 'asc') {
            return valueA > valueB ? 1 : valueA < valueB ? -1 : 0;
        } else {
            return valueA < valueB ? 1 : valueA > valueB ? -1 : 0;
        }
    });
}

// Update trip count display
function updateTripCount() {
    $('#showing-count').text(trips.length);
    $('#total-count').text(allTrips.length);
}