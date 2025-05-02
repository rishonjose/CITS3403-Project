// Test Input Data source
const util_Data = {
  util_labels: ['Electricity', 'Water', 'Gas', 'Wi-fi'], // Name of utilities
  util_colours: ['orange', 'blue', 'green', 'violet'], // Colour of utilities 
  month_labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'], // Months of utilities data
  totalBill: [150, 175, 125, 155, 85],  // Total bill costs per month
  electricity: [35, 32, 37, 30, 33], // electricity costs per month
  water: [45, 60, 50, 40, 55], // water costs per month
  gas: [30, 25, 20, 35, 30], // gas costs per month
  wifi: [40, 58, 18, 50, 45] // Wi-fi costs per month
};
// Replace later with user data fetched from webpage database



//Bill Overview Doughnut Chart: Most recent month data
const pieCtx = document.getElementById('doughnut').getContext('2d');
const pieChart = new Chart(pieCtx, {
  type: 'doughnut',
  data: {
    labels: util_Data.util_labels,
    datasets: [{
      data: [(util_Data.electricity[util_Data.electricity.length -1]), // Data includes latest month utilites
      (util_Data.water[util_Data.water.length -1]),
      (util_Data.gas[util_Data.gas.length -1]),
      (util_Data.wifi[util_Data.wifi.length -1])],
      backgroundColor: util_Data.util_colours
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
