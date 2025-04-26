//Bill Overview Doughnut Chart
const pieCtx = document.getElementById('doughnut').getContext('2d');
const pieChart = new Chart(pieCtx, {
  type: 'doughnut',
  data: {
    labels: ['Electricity', 'Water', 'Gas', 'Wi-Fi'],
    datasets: [{
      data: [45, 25, 15, 15],
      backgroundColor: ['orange', 'blue', 'green', 'violet']
    }],
  },
  options: {
    responsive: true,
    plugins: {
      tooltip: {
        callbacks: {
          label: function (context) {
            const label = context.label || '';
            const value = context.parsed;
            return `${label}: ${value}%`;
          }
        }
      }
    }
  }
});

//Bill Overview Line Chart
const lineCtx = document.getElementById('lineChart').getContext('2d');
const lineChart = new Chart(lineCtx, {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    datasets: [{
      label: 'Total Monthly Bill Cost',
      data: [150, 175, 125, 155, 85],
      borderColor: 'rgba(75, 192, 192, 1)',
      backgroundColor: 'rgba(75, 192, 192, 0.2)',
      fill: true
    }]
  },
  options: {
    responsive: true,
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function (value) {
            return '$' + value;
          }
        }
      }
    }
  }
});

//Monthly Overview Bar Chart
const barCtx = document.getElementById('barChart').getContext('2d');
const barChart = new Chart(barCtx, {
  type: 'bar',
  data: {
    labels: ['Electricity', 'Water', 'Gas', 'Wi-Fi'],
    datasets: [{
      label: 'Costs by Utility',
      data: [120, 60, 40, 75],
      backgroundColor: ['orange', 'blue', 'green', 'violet']
    }]
  },
  options: {
    responsive: true,
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function (value) {
            return '$' + value;
          }
        }
      }
    }
  }
});

//Toggle Monthly Table/Chart
function toggleMonthlyView() {
  const chartCanvas = document.getElementById('barChart');
  const table = document.getElementById('monthlyTable');
  const button = event.target;

  if (table.style.display === 'none') {
    table.style.display = 'block';
    chartCanvas.style.display = 'none';
    button.textContent = 'Switch to Chart View';
  } else {
    table.style.display = 'none';
    chartCanvas.style.display = 'block';
    button.textContent = 'Switch to Table View';
  }
}

//Change Monthly Card Label
const monthSelect = document.getElementById("monthSelect");
const heading = document.getElementById("selectedMonthHeading");

monthSelect.addEventListener("change", () => {
  const selectedMonth = monthSelect.value;
  heading.innerHTML = `<b>${selectedMonth} Analytics</b>`;
});

//Utilities Analytics Table
const utilityCtx = document.getElementById('utilityChart').getContext('2d');
const utilityChart = new Chart(utilityCtx, {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    datasets: [{
      label: 'Electrical Bill Cost',
      data: [35, 32, 37, 30, 33],
      borderColor: 'orange',
      backgroundColor: 'rgba(255,165,0,0.2)',
      fill: true
    }]
  },
  options: {
    responsive: true,
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});

//Toggle Utilities Table/Chart
function toggleUtilityView() {
  const chartCanvas = document.getElementById('utilityChart');
  const table = document.getElementById('utilityTable');
  const button = event.target;

  if (table.style.display === 'none') {
    table.style.display = 'block';
    chartCanvas.style.display = 'none';
    button.textContent = 'Switch to Chart View';
  } else {
    table.style.display = 'none';
    chartCanvas.style.display = 'block';
    button.textContent = 'Switch to Table View';
  }
}