let weeklyData = {};

        // Method 1: Using fetch() to load JSON file
        async function loadWeeklyData() {
            try {
                const response = await fetch('data/nfl_results.json');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                weeklyData = await response.json();
                console.log('Data loaded successfully:', weeklyData);
                return weeklyData;
            } catch (error) {
                console.error('Error loading data:', error);
                // Fallback to empty data or show error message
                showErrorMessage('Failed to load data. Please check if nfl_results.json exists.');
                return {};
            }
        }

        // Method 2: Alternative using XMLHttpRequest (for older browser support)
        function loadWeeklyDataXHR() {
            return new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();
                xhr.open('GET', 'data/nfl_results.json', true);
                xhr.onreadystatechange = function() {
                    if (xhr.readyState === 4) {
                        if (xhr.status === 200) {
                            try {
                                weeklyData = JSON.parse(xhr.responseText);
                                resolve(weeklyData);
                            } catch (e) {
                                reject(new Error('Invalid JSON format'));
                            }
                        } else {
                            reject(new Error(`Failed to load file: ${xhr.status}`));
                        }
                    }
                };
                xhr.send();
            });
        }

        // Error display function
        function showErrorMessage(message) {
            const noDataDiv = document.getElementById('noData');
            noDataDiv.innerHTML = `<div style="color: red; font-weight: bold;">${message}</div>`;
        }

        // Initialize the page - now with async data loading
        document.addEventListener('DOMContentLoaded', async function() {
            // Show loading message
            document.getElementById('noData').innerHTML = '<div style="color: #666;">Loading data...</div>';

            // Load data from external JSON file
            await loadWeeklyData();

            // Initialize UI after data is loaded
            populateWeekDropdown();
            setupEventListeners();

            // Reset loading message
            if (Object.keys(weeklyData).length === 0) {
                document.getElementById('noData').innerHTML = 'No data available or failed to load data.';
            } else {
                document.getElementById('noData').innerHTML = 'Please select a week to view data';
            }
        });

        function populateWeekDropdown() {
            const select = document.getElementById('weekSelect');

            // Clear existing options except the first one
            select.innerHTML = '<option value="">-- Choose a week --</option>';

            // Add options for each week
            Object.keys(weeklyData).sort((a, b) => parseInt(a) - parseInt(b)).forEach(week => {
                const option = document.createElement('option');
                option.value = week;
                option.textContent = `${week}`;
                select.appendChild(option);
            });
        }

        function setupEventListeners() {
            document.getElementById('weekSelect').addEventListener('change', function() {
                const selectedWeek = this.value;
                if (selectedWeek) {
                    displayWeekData(selectedWeek);
                } else {
                    hideTable();
                }
            });
        }

        function displayWeekData(week) {
            const data = weeklyData[week];
            if (!data || data.length === 0) {
                hideTable();
                return;
            }

            // Show week info
            document.getElementById('selectedWeek').textContent = `${week}`;
            document.getElementById('rowCount').textContent = data.length ; // Subtract header row
            document.getElementById('weekInfo').style.display = 'block';

            // Create table header

            // const headerRow = data[0];
                const headerRow = ['Game', 'Result']
            const thead = document.getElementById('tableHeader');
            thead.innerHTML = '';

            const headerRowElement = document.createElement('tr');
            headerRow.forEach(header => {
                const th = document.createElement('th');
                th.textContent = header;
                headerRowElement.appendChild(th);
            });
            thead.appendChild(headerRowElement);

            // Create table body
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';

            // Skip the first row (header) and add the rest
            for (let i = 0; i < data.length; i++) {
                const row = data[i];
                const tr = document.createElement('tr');

                row.forEach(cell => {
                    const td = document.createElement('td');
                    td.textContent = cell;
                    tr.appendChild(td);
                });

                tbody.appendChild(tr);
            }

            // Show table and hide no-data message
            document.getElementById('dataTable').style.display = 'table';
            document.getElementById('noData').style.display = 'none';
        }

        function hideTable() {
            document.getElementById('dataTable').style.display = 'none';
            document.getElementById('weekInfo').style.display = 'none';
            document.getElementById('noData').style.display = 'block';
        }

        // Function to update data dynamically (you can call this to load your actual data)
        function updateWeeklyData(newData) {
            Object.assign(weeklyData, newData);
            populateWeekDropdown();
            // Reset selection
            document.getElementById('weekSelect').value = '';
            hideTable();
        }