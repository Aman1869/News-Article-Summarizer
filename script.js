document.getElementById('scrape-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const url = document.getElementById('news-url').value;
    const loading = document.getElementById('loading');
    const percentageMeter = document.getElementById('percentage-meter');
    const resultContainer = document.getElementById('result');

    // Show loading spinner and percentage meter, hide previous results
    loading.style.display = 'block';
    percentageMeter.style.display = 'block';
    resultContainer.classList.remove('show');
    resultContainer.innerHTML = '';

    // Initialize percentage
    let percentage = 0;

    // Function to update percentage meter
    const updatePercentage = () => {
        if (percentage < 99) {
            percentage += 1;
            percentageMeter.textContent = `${percentage}%`;
        }
    };

    // Start updating percentage meter
    const interval = setInterval(updatePercentage, 30); // Adjusted interval for smoother update

    try {
        const response = await fetch('http://127.0.0.1:5000/scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url })
        });

        const result = await response.json();

        // Ensure fetch completes and percentage hits 99%
        await new Promise(resolve => {
            const waitInterval = setInterval(() => {
                if (percentage >= 99) {
                    clearInterval(waitInterval);
                    resolve();
                }
            }, 30);
        });

        // Set percentage to 100% after receiving response
        percentage = 100;
        percentageMeter.textContent = `${percentage}%`;

        // Delay to keep percentage at 100% for a brief moment
        await new Promise(resolve => setTimeout(resolve, 100));

        // Hide loading elements once fetch is complete
        clearInterval(interval);
        loading.style.display = 'none';
        percentageMeter.style.display = 'none';

        if (response.ok) {
            resultContainer.innerHTML = `
                <h2>${result.title}</h2>
                <p>${result.summary}</p>
                <p><strong>Date:</strong> ${result.date}</p>
                <p><strong>Source:</strong> <a href="${result.source}" target="_blank" rel="noopener noreferrer">${result.source}</a></p>
            `;
            resultContainer.classList.add('show');
        } else {
            resultContainer.innerHTML = `<p>Error: ${result.error}</p>`;
        }
    } catch (error) {
        resultContainer.innerHTML = `<p>Error: ${error.message}</p>`;
        loading.style.display = 'none';
        percentageMeter.style.display = 'none';
    }
});

// Theme Toggle Functionality
const themeToggleButton = document.getElementById('theme-toggle-button');
themeToggleButton.addEventListener('click', () => {
    const body = document.body;
    const isDarkMode = body.classList.contains('dark-theme');

    if (isDarkMode) {
        body.classList.remove('dark-theme');
        body.classList.add('light-theme');
        themeToggleButton.textContent = 'Switch to Dark Mode';
    } else {
        body.classList.remove('light-theme');
        body.classList.add('dark-theme');
        themeToggleButton.textContent = 'Switch to Light Mode';
    }
});
