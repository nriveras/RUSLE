/**
 * RUSLE Web Application JavaScript
 */

// State management
const state = {
    sessionId: null,
    jobId: null,
    uploadedFile: null,
    map: null,
    layers: {},
    isProcessing: false
};

// API endpoints
const API = {
    upload: '/api/upload',
    process: '/api/process',
    visualize: (jobId) => `/api/visualize/${jobId}`,
    statistics: (jobId) => `/api/process/${jobId}/statistics`,
    export: (jobId) => `/api/process/${jobId}/export`,
    legend: '/api/legend'
};

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    initializeMap();
    initializeFileUpload();
    initializeForm();
    loadLegend();
});

/**
 * Initialize Leaflet map
 */
function initializeMap() {
    state.map = L.map('map', {
        center: [-33.45, -70.65], // Santiago, Chile default
        zoom: 9
    });
    
    // Add base layers
    const baseLayers = {
        'CartoDB Positron': L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
        }),
        'OpenStreetMap': L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }),
        'Satellite': L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: 'Tiles &copy; Esri'
        })
    };
    
    baseLayers['CartoDB Positron'].addTo(state.map);
    
    // Add layer control for base maps
    L.control.layers(baseLayers, {}, { position: 'topright' }).addTo(state.map);
}

/**
 * Initialize file upload handlers
 */
function initializeFileUpload() {
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    
    // Prevent defaults for drag events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    // Highlight on drag
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => {
            dropArea.classList.add('dragover');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => {
            dropArea.classList.remove('dragover');
        }, false);
    });
    
    // Handle drop
    dropArea.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    }, false);
    
    // Handle click upload
    dropArea.addEventListener('click', () => {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });
}

/**
 * Prevent default drag behaviors
 */
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

/**
 * Handle uploaded file
 */
async function handleFile(file) {
    // Validate file type
    const validTypes = ['.zip', '.geojson'];
    const fileExt = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));
    
    if (!validTypes.includes(fileExt)) {
        showAlert('error', 'Please upload a ZIP file containing shapefile components or a GeoJSON file.');
        return;
    }
    
    // Validate file size (50MB max)
    if (file.size > 50 * 1024 * 1024) {
        showAlert('error', 'File too large. Maximum size is 50MB.');
        return;
    }
    
    state.uploadedFile = file;
    showFileInfo(file);
    
    // Upload to server
    await uploadFile(file);
}

/**
 * Display uploaded file info
 */
function showFileInfo(file) {
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    
    fileName.textContent = file.name;
    fileInfo.classList.remove('hidden');
}

/**
 * Remove uploaded file
 */
function removeFile() {
    state.uploadedFile = null;
    state.sessionId = null;
    
    document.getElementById('file-info').classList.add('hidden');
    document.getElementById('file-input').value = '';
    
    // Remove AOI layer from map
    if (state.layers.aoi) {
        state.map.removeLayer(state.layers.aoi);
        delete state.layers.aoi;
    }
}

/**
 * Upload file to server
 */
async function uploadFile(file) {
    showLoading('Uploading file...');
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(API.upload, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }
        
        const data = await response.json();
        state.sessionId = data.session_id;
        
        // Show AOI on map
        await showAOIOnMap(data);
        
        showAlert('success', `File uploaded successfully! Area: ${data.area_km2.toFixed(2)} km²`);
        
    } catch (error) {
        showAlert('error', error.message);
        removeFile();
    } finally {
        hideLoading();
    }
}

/**
 * Show AOI boundary on map
 */
async function showAOIOnMap(uploadData) {
    // Fetch GeoJSON preview
    try {
        const response = await fetch(`/api/upload/${state.sessionId}/preview`);
        if (response.ok) {
            const geojson = await response.json();
            
            // Remove existing AOI layer
            if (state.layers.aoi) {
                state.map.removeLayer(state.layers.aoi);
            }
            
            // Add new AOI layer
            state.layers.aoi = L.geoJSON(geojson, {
                style: {
                    color: '#2e7d32',
                    weight: 2,
                    fillOpacity: 0.1
                }
            }).addTo(state.map);
            
            // Fit map to AOI
            state.map.fitBounds(state.layers.aoi.getBounds());
        }
    } catch (error) {
        console.error('Failed to show AOI:', error);
    }
}

/**
 * Initialize form submission
 */
function initializeForm() {
    const form = document.getElementById('rusle-form');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await processRUSLE();
    });
    
    // Set default dates (last year)
    const today = new Date();
    const lastYear = new Date(today);
    lastYear.setFullYear(lastYear.getFullYear() - 1);
    
    document.getElementById('date-to').value = today.toISOString().split('T')[0];
    document.getElementById('date-from').value = lastYear.toISOString().split('T')[0];
}

/**
 * Process RUSLE calculation
 */
async function processRUSLE() {
    // Validate inputs
    const adminRegion = document.getElementById('admin-region').value.trim();
    
    if (!state.sessionId && !adminRegion) {
        showAlert('error', 'Please upload a shapefile or enter an administrative region name.');
        return;
    }
    
    const dateFrom = document.getElementById('date-from').value;
    const dateTo = document.getElementById('date-to').value;
    
    if (!dateFrom || !dateTo) {
        showAlert('error', 'Please specify both start and end dates.');
        return;
    }
    
    if (new Date(dateFrom) >= new Date(dateTo)) {
        showAlert('error', 'Start date must be before end date.');
        return;
    }
    
    showLoading('Processing RUSLE calculation...');
    state.isProcessing = true;
    
    try {
        const requestBody = {
            date_from: dateFrom,
            date_to: dateTo,
            dem_source: document.getElementById('dem-source').value,
            export_scale: parseInt(document.getElementById('export-scale').value)
        };
        
        if (state.sessionId) {
            requestBody.session_id = state.sessionId;
        } else {
            requestBody.admin_region = adminRegion;
        }
        
        const response = await fetch(API.process, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Processing failed');
        }
        
        const data = await response.json();
        state.jobId = data.job_id;
        
        // Display results
        await displayResults(data);
        
        showAlert('success', `RUSLE calculation completed in ${data.computation_time.toFixed(2)}s`);
        
    } catch (error) {
        showAlert('error', error.message);
    } finally {
        hideLoading();
        state.isProcessing = false;
    }
}

/**
 * Display RUSLE results on map
 */
async function displayResults(data) {
    // Clear existing result layers
    Object.keys(state.layers).forEach(key => {
        if (key !== 'aoi' && state.layers[key]) {
            state.map.removeLayer(state.layers[key]);
            delete state.layers[key];
        }
    });
    
    // Add soil loss layer
    if (data.soil_loss_tile_url) {
        state.layers.soilLoss = L.tileLayer(data.soil_loss_tile_url, {
            attribution: 'Google Earth Engine'
        }).addTo(state.map);
    }
    
    // Update layer controls
    updateLayerControls(data.factors);
    
    // Show results section
    document.getElementById('results-section').classList.remove('hidden');
    
    // Load statistics
    await loadStatistics();
}

/**
 * Update layer control checkboxes
 */
function updateLayerControls(factors) {
    const layerControl = document.getElementById('layer-list');
    layerControl.innerHTML = '';
    
    // Soil loss layer (always visible by default)
    addLayerControl('soilLoss', 'Soil Loss (ton/ha/yr)', true, state.layers.soilLoss);
    
    // Add factor layers
    if (factors) {
        Object.entries(factors).forEach(([key, factor]) => {
            const layerId = `factor_${key}`;
            if (factor.tile_url) {
                state.layers[layerId] = L.tileLayer(factor.tile_url, {
                    attribution: 'Google Earth Engine'
                });
                addLayerControl(layerId, factor.name, false);
            }
        });
    }
}

/**
 * Add layer control checkbox
 */
function addLayerControl(layerId, name, visible, layer) {
    const layerList = document.getElementById('layer-list');
    
    const item = document.createElement('div');
    item.className = 'layer-item';
    
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = `layer-${layerId}`;
    checkbox.checked = visible;
    checkbox.addEventListener('change', () => toggleLayer(layerId, checkbox.checked));
    
    const label = document.createElement('label');
    label.htmlFor = `layer-${layerId}`;
    label.textContent = name;
    
    item.appendChild(checkbox);
    item.appendChild(label);
    layerList.appendChild(item);
}

/**
 * Toggle layer visibility
 */
function toggleLayer(layerId, visible) {
    const layer = state.layers[layerId];
    if (!layer) return;
    
    if (visible) {
        layer.addTo(state.map);
    } else {
        state.map.removeLayer(layer);
    }
}

/**
 * Load and display statistics
 */
async function loadStatistics() {
    if (!state.jobId) return;
    
    try {
        const response = await fetch(API.statistics(state.jobId));
        if (response.ok) {
            const data = await response.json();
            displayStatistics(data.statistics);
        }
    } catch (error) {
        console.error('Failed to load statistics:', error);
    }
}

/**
 * Display statistics in the UI
 */
function displayStatistics(stats) {
    const container = document.getElementById('stats-container');
    container.innerHTML = '';
    
    const statItems = [
        { key: 'soil_loss_mean', label: 'Mean', unit: 't/ha/yr' },
        { key: 'soil_loss_min', label: 'Min', unit: 't/ha/yr' },
        { key: 'soil_loss_max', label: 'Max', unit: 't/ha/yr' },
        { key: 'soil_loss_stdDev', label: 'Std Dev', unit: 't/ha/yr' }
    ];
    
    statItems.forEach(item => {
        const value = stats[item.key];
        if (value !== undefined) {
            const card = document.createElement('div');
            card.className = 'stat-card';
            card.innerHTML = `
                <div class="stat-value">${formatNumber(value)}</div>
                <div class="stat-label">${item.label}</div>
            `;
            container.appendChild(card);
        }
    });
}

/**
 * Load legend information
 */
async function loadLegend() {
    try {
        const response = await fetch(API.legend);
        if (response.ok) {
            const data = await response.json();
            displayLegend(data.soil_loss_classes);
        }
    } catch (error) {
        console.error('Failed to load legend:', error);
    }
}

/**
 * Display legend
 */
function displayLegend(classes) {
    const legend = document.getElementById('legend');
    legend.innerHTML = '';
    
    classes.forEach(cls => {
        const item = document.createElement('div');
        item.className = 'legend-item';
        item.innerHTML = `
            <div class="legend-color" style="background: ${cls.color}"></div>
            <span>${cls.range}: ${cls.label}</span>
        `;
        legend.appendChild(item);
    });
}

/**
 * Export results to Google Drive
 */
async function exportToDrive() {
    if (!state.jobId) {
        showAlert('error', 'No results to export. Please run the calculation first.');
        return;
    }
    
    showLoading('Starting export to Google Drive...');
    
    try {
        const response = await fetch(API.export(state.jobId), {
            method: 'POST'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Export failed');
        }
        
        const data = await response.json();
        showAlert('success', `Export started! Check your Google Drive folder: ${data.folder}`);
        
    } catch (error) {
        showAlert('error', error.message);
    } finally {
        hideLoading();
    }
}

/**
 * Show loading overlay
 */
function showLoading(message = 'Loading...') {
    const overlay = document.getElementById('loading-overlay');
    const text = document.getElementById('loading-text');
    text.textContent = message;
    overlay.classList.remove('hidden');
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    document.getElementById('loading-overlay').classList.add('hidden');
}

/**
 * Show alert message
 */
function showAlert(type, message) {
    const container = document.getElementById('alert-container');
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    container.appendChild(alert);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

/**
 * Format number for display
 */
function formatNumber(num, decimals = 2) {
    if (num === null || num === undefined) return '-';
    return parseFloat(num).toFixed(decimals);
}

/**
 * Switch tabs
 */
function switchTab(tabId) {
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabId);
    });
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === tabId);
    });
}
