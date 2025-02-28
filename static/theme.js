// Helper to update the visibility of theme icons based on the active theme
function updateThemeIcons(theme) {
    const sunIcon = document.querySelector('.fa-sun');
    const moonIcon = document.querySelector('.fa-moon');
    if (theme === 'dark') {
      sunIcon.style.display = 'none';
      moonIcon.style.display = 'inline';
    } else {
      sunIcon.style.display = 'inline';
      moonIcon.style.display = 'none';
    }
  }
  
  // Update all Chart.js instances to reflect the current theme colors
  function updateAllCharts() {
    const isDarkTheme = document.body.dataset.theme === 'dark';
    const textColor = isDarkTheme ? '#e0e0e0' : '#333';
    ['categoryChart', 'monthlySpendingChart', 'yearlySpendingChart'].forEach(chartId => {
      const chart = Chart.getChart(chartId);
      if (chart) {
        chart.options.plugins.legend.labels.color = textColor;
        // Update tooltip colors
        const tooltipOptions = chart.options.plugins.tooltip;
        tooltipOptions.bodyColor = textColor;
        tooltipOptions.titleColor = textColor;
        chart.update();
      }
    });
  }
  
  // Set the initial theme based on localStorage or system preferences
  function setInitialTheme() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = savedTheme || (prefersDark ? 'dark' : 'light');
    document.body.dataset.theme = theme;
    localStorage.setItem('theme', theme);
    updateThemeIcons(theme);
    updateAllCharts();
  }
  
  // Toggle the current theme and update storage, icons, and charts
  function toggleTheme() {
    const currentTheme = document.body.dataset.theme;
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.body.dataset.theme = newTheme;
    localStorage.setItem('theme', newTheme);
    updateThemeIcons(newTheme);
    updateAllCharts();
  }
  
  // Initialize theme and add event listener once DOM is ready
  document.addEventListener('DOMContentLoaded', () => {
    setInitialTheme();
    const themeToggleButton = document.querySelector('.theme-toggle');
    if (themeToggleButton) {
      themeToggleButton.addEventListener('click', toggleTheme);
    }
  });
  