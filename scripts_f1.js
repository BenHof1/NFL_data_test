let f1_weeklyData = {};

        // Method 1: Using fetch() to load JSON file
        async function f1_loadWeeklyData() {
            try {
                const response = await fetch('data/f1_results.json');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                f1_weeklyData = await response.json();
                console.log('Data loaded successfully:', f1_weeklyData);
                return f1_weeklyData;
            } catch (error) {
                console.error('Error loading data:', error);
                // Fallback to empty data or show error message
                showErrorMessage('Failed to load data. Please check if f1_results.json exists.');
                return {};
            }
        }


        function f1_loadWeeklyDataXHR() {
            return new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();
                xhr.open('GET', 'data/f1_results.json', true);
                xhr.onreadystatechange = function() {
                    if (xhr.readyState === 4) {
                        if (xhr.status === 200) {
                            try {
                                f1_weeklyData = JSON.parse(xhr.responseText);
                                resolve(f1_weeklyData);
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
            const noDataDiv = document.getElementById('f1NoData');
            noDataDiv.innerHTML = `<div style="color: red; font-weight: bold;">${message}</div>`;
        }

        // Initialize the page - now with async data loading
        document.addEventListener('DOMContentLoaded', async function() {
            // Show loading message
            document.getElementById('f1NoData').innerHTML = '<div style="color: #666;">Loading data...</div>';

            // Load data from external JSON file
            await f1_loadWeeklyData();

            // Initialize UI after data is loaded
            f1_setupEventListeners();

            // Reset loading message

        });


        function f1_setupEventListeners() {
            document.getElementById('F1').addEventListener('click', function() {
                // const selectedWeek = this.value;
                f1_displayWeekData();

            });
        }



        function f1_displayWeekData() {
            const data = f1_weeklyData;

            // Create table header

            // const headerRow = data[0];
                const headerRow = ['Grand Prix', 'Date','Laps', 'Time', 'Watchability Score', 'Rank', "Relative Score"]
            const thead = document.getElementById('f1TableHeader');
            thead.innerHTML = '';

            const headerRowElement = document.createElement('tr');
            headerRow.forEach(header => {
                const th = document.createElement('th');
                th.textContent = header;
                headerRowElement.appendChild(th);
            });
            thead.appendChild(headerRowElement);

            // Create table body
            const tbody = document.getElementById('f1TableBody');
            tbody.innerHTML = '';

            // Skip the first row (header) and add the rest
            for (const i in data){
                var row = data[i];
                const tr = document.createElement('tr');

                var count = 0;
                for (var i_1 in row) {
                    const td = document.createElement('td');
                    td.textContent = row[i_1];
                    tr.appendChild(td);
                };

                tbody.appendChild(tr);
            }

            // Show table and hide no-data message
            document.getElementById('f1Table').style.display = 'table';
            document.getElementById('f1NoData').style.display = 'none';
        }

        function f1_hideTable() {
            document.getElementById('f1DataTable').style.display = 'none';
            document.getElementById('f1NoData').style.display = 'block';
        }
