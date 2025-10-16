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
        updateInsights();

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

// Initialize dashboard with function
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
    $('#stat-avg-passengers').text(Math.round(totalPassengers / totalTrips));
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
    $('#search-id, #filter-vendor, #filter-passengers, #filter-duration, #filter-month, #filter-location').on('input change', applyFilters);
    
    $('#reset-filters').on('click', function() {
        $('#search-id').val('');
        $('#filter-vendor').val('');
        $('#filter-passengers').val('');
        $('#filter-duration').val('');
        $('#filter-month').val('');
        $('#filter-location').val('');
        applyFilters();
    });
}

// Apply filters
async function applyFilters() {
    const searchId = $('#search-id').val().toLowerCase();
    const filterVendor = $('#filter-vendor').val();
    const filterPassengers = $('#filter-passengers').val();
    const filterDuration = $('#filter-duration').val();
    const filterMonth = $('#filter-month').val();
    const filterLocation = $('#filter-location').val().toLowerCase();

    trips = allTrips.filter(trip => {
        // Search by Trip ID
        if (searchId && !trip.id.toLowerCase().includes(searchId)) 
            return false;

        // Filter by Vendor
        if (filterVendor && trip.vendor_id.toString() !== filterVendor) 
            return false;

        // Filter by Passengers
        if (filterPassengers) {
            if (filterPassengers === "6+" && trip.passenger_count < 6) 
                return false;
            else if (filterPassengers !== "6+" && trip.passenger_count.toString() !== filterPassengers) 
                return false;
        }

        // Filter by Duration range
        if (filterDuration) {
            const [min, max] = filterDuration.split('-');
            const duration = trip.trip_duration; // in seconds
            if (max && duration < parseInt(min) || (max && duration > parseInt(max))) 
                return false;
            if (!max && parseInt(min) && duration < parseInt(min)) 
                return false;
        }

        // Filter by Month (based on pickup_datetime)
        if (filterMonth && trip.pickup_datetime.getMonth() + 1 !== parseInt(filterMonth)) 
            return false;

        // Filter by Location — using pickup_latitude & longitude
        if (filterLocation) {
            const loc = filterLocation;
            if (loc === "midtown" && !(trip.pickup_latitude >= 40.74 && trip.pickup_latitude <= 40.77)) 
                return false;
            if (loc === "downtown" && !(trip.pickup_latitude < 40.72)) 
                return false;
            if (loc === "uptown" && !(trip.pickup_latitude > 40.78)) 
                return false;
            if (loc === "brooklyn" && !(trip.pickup_longitude < -73.95)) 
                return false;
            if (loc === "queens" && !(trip.pickup_longitude > -73.95 && trip.pickup_latitude > 40.7)) 
                return false;
            if (loc === "bronx" && !(trip.pickup_latitude > 40.84)) 
                return false;
        }

        return true;
    });

    // Update UI
    updateStats();
    populateTable();
    createDurationChart();
    createPassengerCharts();
    createTimeChart();
    createMapChart();
    updateTripCount();
    updateInsights();
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

// Sort trips manually without using built-insort
function sortTrips() {
    const field = currentSort.field;
    const direction = currentSort.direction;

    trips = selectionSort(trips, field, direction);
}

// Selection sort algorithm implementation
function selectionSort(trips_array, key, direction = 'asc') {
    const trip_arr = [...trips_array];
    const n = trip_arr.length;

    for (let i = 0; i < n - 1; i++) {
        let actualIndex = i;

        for (let j = i + 1; j < n; j++) {
            let valueA = trip_arr[j][key];
            let valueB = trip_arr[actualIndex][key];

            // Handle dates
            if (valueA instanceof Date) valueA = valueA.getTime();
            if (valueB instanceof Date) valueB = valueB.getTime();

            // Handle strings
            if (typeof valueA === 'string') valueA = valueA.toLowerCase();
            if (typeof valueB === 'string') valueB = valueB.toLowerCase();

            const condition = direction === 'asc'
                ? valueA < valueB
                : valueA > valueB;

            if (condition) {
                actualIndex = j;
            }
        }

        // Swap elements
        if (actualIndex !== i) {
            const temp = trip_arr[i];
            trip_arr[i] = trip_arr[actualIndex];
            trip_arr[actualIndex] = temp;
        }
    }

    return trip_arr;
}

// Update trip count display
function updateTripCount() {
    $('#showing-count').text(trips.length);
    $('#total-count').text(allTrips.length);
}

// Insights and stories for our dashboard
function updateInsights() {
    if (!trips.length) {
        $('#insights-text').html("<p>No data available for the selected filters.</p>");
        $('#story-section').html("");
        return;
    }

    const totalTrips = trips.length;
    const totalDuration = trips.reduce((s, t) => s + t.trip_duration, 0);
    const totalPassengers = trips.reduce((s, t) => s + t.passenger_count, 0);
    const avgDuration = Math.round(totalDuration / totalTrips / 60);
    const avgPassengers = (totalPassengers / totalTrips).toFixed(1);

    // Peak hour calculation
    const hourCounts = {};
    trips.forEach(t => {
        const h = t.pickup_datetime.getHours();
        hourCounts[h] = (hourCounts[h] || 0) + 1;
    });
    const [peakHour, peakTrips] = Object.entries(hourCounts).sort((a,b)=>b[1]-a[1])[0];

    // Vendor with most trips
    const vendorCounts = {};
    trips.forEach(t => {
        vendorCounts[t.vendor_id] = (vendorCounts[t.vendor_id] || 0) + 1;
    });
    const [topVendor, topVendorTrips] = Object.entries(vendorCounts).sort((a,b)=>b[1]-a[1])[0];

    // Location context
    const location = $('#filter-location').val();
    const locationText = location ? ` in <b>${location}</b>` : "";

    $('#insights-text').html(`
        <div class="insight-card">trips${locationText} had <b>${totalTrips}</b> trips</div>
        <div class="insight-card">There are <b>${totalTrips}</b> trips analyzed</div>
        <div class="insight-card">The average duration for a trip is <b>${avgDuration} min</b></div>
        <div class="insight-card">Average passengers per trip are <b>${avgPassengers}</b></div>
        <div class="insight-card">Trips mostly occur around <b>${peakHour}:00</b> (${peakTrips} trips)</div>
        <div class="insight-card">There is a strong preference for <b>Vendor ${topVendor}</b> (${topVendorTrips} trips)</div>
    `);

    generateStory(avgDuration, avgPassengers, peakHour, location);
}

function generateStory(avgDuration, avgPassengers, peakHour, location) {
    let story = "";
    const area = location ? location.charAt(0).toUpperCase() + location.slice(1) : "the city";

    if (avgDuration < 10) {
        story += `We see that most trips in ${area} are short, which suggests dense urban mobility zones. `;
    } else if (avgDuration < 25) {
        story += `We see that moderate average durations may indicate people moving across nearby neighbourhoods in ${area}. `;
    } else {
        story += `We see that there are long trip times in ${area}, indicating citywide or interurban movements. `;
    }

    if (avgPassengers <= 1.5) {
        story += `The majority of trips in ${area} carry solo passengers. Most people prefer to travel alone. `;
    } else {
        story += "People travelled in groups as evidenced by higher passenger counts to probably share costs or travel with family";
    }

    story += `There is a flurry of activity around ${peakHour}:00. This pattern shows some preferred common commuting hours.`;

    $('#story-section').html(`<p>${story}</p>`);
}
