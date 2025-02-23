// Function to update all Chart.js colors based on the current theme
function updateAllCharts() {
    const isDarkTheme = document.body.getAttribute('data-theme') === 'dark';
    const textColor = isDarkTheme ? '#e0e0e0' : '#333'; // Light text for dark theme, dark text for light theme

    // Update all existing charts
    const charts = ['categoryChart', 'monthlySpendingChart', 'yearlySpendingChart'];
    charts.forEach(chartId => {
        const chart = Chart.getChart(chartId);
        if (chart) {
            chart.options.plugins.legend.labels.color = textColor;
            chart.options.plugins.tooltip.bodyColor = textColor;
            chart.options.plugins.tooltip.titleColor = textColor;
            chart.update();
        }
    });
}

// Call this function in `toggleTheme` and `setInitialTheme`
function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    const sunIcon = document.querySelector('.fa-sun');
    const moonIcon = document.querySelector('.fa-moon');

    if (currentTheme === 'dark') {
        body.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
        sunIcon.style.display = 'inline'; // Show sun icon
        moonIcon.style.display = 'none';  // Hide moon icon
    } else {
        body.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
        sunIcon.style.display = 'none';   // Hide sun icon
        moonIcon.style.display = 'inline'; // Show moon icon
    }

    // Update all charts
    updateAllCharts();
}

function setInitialTheme() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const sunIcon = document.querySelector('.fa-sun');
    const moonIcon = document.querySelector('.fa-moon');

    if (savedTheme) {
        document.body.setAttribute('data-theme', savedTheme);
        if (savedTheme === 'dark') {
            sunIcon.style.display = 'none';
            moonIcon.style.display = 'inline';
        } else {
            sunIcon.style.display = 'inline';
            moonIcon.style.display = 'none';
        }
    } else if (prefersDark) {
        document.body.setAttribute('data-theme', 'dark');
        sunIcon.style.display = 'none';
        moonIcon.style.display = 'inline';
    } else {
        document.body.setAttribute('data-theme', 'light');
        sunIcon.style.display = 'inline';
        moonIcon.style.display = 'none';
    }

    // Update all charts
    updateAllCharts();
}

// Add event listener to the toggle button
document.addEventListener('DOMContentLoaded', () => {
    setInitialTheme();

    const themeToggleButton = document.querySelector('.theme-toggle');
    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', toggleTheme);
    }
});