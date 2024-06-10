document.getElementById('number-of-company').addEventListener('input', function() {
    const numberOfCompanies = parseInt(this.value, 10);
    const dynamicFieldsContainer = document.getElementById('dynamic-fields');
    dynamicFieldsContainer.innerHTML = '';

    if (!isNaN(numberOfCompanies) && numberOfCompanies > 0) {
        const csvPath = '../static/js/filtered_links.csv';

        // Make a request to fetch the CSV file
        const xhr = new XMLHttpRequest();
        xhr.open('GET', csvPath, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    // Parse CSV data
                    const csvData = xhr.responseText;
                    const rows = csvData.split('\n');
                    const companyNames = new Set();

                    // Skip the first row
                    rows.slice(1).forEach(row => {
                        const columns = row.split(',');
                        if (columns.length >= 2) {
                            let homeName = he.decode(columns[0].trim());
                            let linkName = he.decode(columns[1].trim());

                            // Remove leading apostrophe
                            homeName = homeName.replace(/^"/, '');
                            linkName = linkName.replace(/^"/, '');

                            companyNames.add(homeName);
                            companyNames.add(linkName);
                        }
                    });

                    // Convert the set to an array and sort it alphabetically
                    const sortedCompanyNames = Array.from(companyNames).sort();

                    // Create dynamic fields based on the retrieved service options
                    for (let i = 0; i < numberOfCompanies; i++) {
                        // Create the select field for the companies
                        const companySelect = document.createElement('select');
                        companySelect.name = `company-${i+1}`;
                        companySelect.classList.add('form-select', 'form-control', 'mb-2');

                        sortedCompanyNames.forEach(companyName => {
                            const companyOption = document.createElement('option');
                            companyOption.value = companyName;
                            companyOption.textContent = companyName;
                            companySelect.appendChild(companyOption);
                        });

                        // Append the companySelect to the dynamic fields container
                        dynamicFieldsContainer.appendChild(companySelect);

                        // Create the select field for the type
                        const typeSelect = document.createElement('select');
                        typeSelect.name = `type-${i+1}`;
                        typeSelect.classList.add('form-select', 'form-control', 'mb-2');

                        const typeOptions = [
                            { value: 'customer', text: 'customer' },
                            { value: 'partnership', text: 'partnership' },
                            { value: 'investment', text: 'investment' },
                            { value: 'competitor', text: 'competitor' },
                        ];

                        typeOptions.forEach(optionData => {
                            const option = document.createElement('option');
                            option.value = optionData.value;
                            option.textContent = optionData.text;
                            typeSelect.appendChild(option);
                        });

                        // Append the typeSelect to the dynamic fields container
                        dynamicFieldsContainer.appendChild(typeSelect);
                    }
                } else {
                    console.error('Failed to fetch CSV file. Please check the path and try again.');
                }
            }
        };
        xhr.send();
    }
});
