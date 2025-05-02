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

//Bill Overview Line Chart: Total bill cost over each month
const lineCtx = document.getElementById('lineChart').getContext('2d');
const lineChart = new Chart(lineCtx, {
  type: 'line',
  data: {
    labels: util_Data.month_labels,
    datasets: [{
      label: 'Total Monthly Bill Cost',
      data: util_Data.totalBill,
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

//Monthly Overview Bar Chart: Selected Month cost over each month
const barCtx = document.getElementById('barChart').getContext('2d');
const barChart = new Chart(barCtx, {
  type: 'bar',
  data: {
    labels: util_Data.util_labels,
    datasets: [{
      label: 'Costs by Utility',
      data:[(util_Data.electricity[util_Data.electricity.length -1]), //latest month data: Replace with selected date data. 
      (util_Data.water[util_Data.water.length -1]),
      (util_Data.gas[util_Data.gas.length -1]),
      (util_Data.wifi[util_Data.wifi.length -1])],
      backgroundColor: util_Data.util_colours
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

//Utilities Analytics Chart
const utilityCtx = document.getElementById('utilityChart').getContext('2d');
const utilityChart = new Chart(utilityCtx, {
  type: 'line',
  data: {
    labels: util_Data.month_labels,
    datasets: [{
      label: 'Electrical Bill Cost',
      data: util_Data.electricity, //electricity utility data: Replace with selected utility data.
      borderColor: util_Data.util_colours[0],
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

// Creates Monthly Table for the Monthly Overview Bar Chart
function populatemonthlyTable() {
  const tableThread = document.querySelector('#monthlyTable thead');
  const tableBody = document.querySelector('#monthlyTable tbody');

  // Clear previous <thead> content
  tableThread.innerHTML = '';

  // Build <thead>
  const threadRow = document.createElement('tr');
  threadRow.innerHTML = `
    <th style="background-color: #f0f0f0;" >Utility</th>
    <th style="background-color: #f0f0f0;" >${util_Data.util_labels[0]}</th>
    <th style="background-color: #f0f0f0;" >${util_Data.util_labels[1]}</th>
    <th style="background-color: #f0f0f0;" >${util_Data.util_labels[2]}</th>
    <th style="background-color: #f0f0f0;" >${util_Data.util_labels[3]}</th>
  `;
  tableThread.appendChild(threadRow);

  // Clear previous <tbody> content
  tableBody.innerHTML = '';
  const bodyRow = document.createElement('tr');

  // Build <tbody>
  bodyRow.innerHTML = `
    <td style="background-color: #f0f0f0;"><b>Bill Cost<b></td>
    <td>$${util_Data.electricity[util_Data.electricity.length -1]}</td>
    <td>$${util_Data.water[util_Data.water.length -1]}</td>
    <td>$${util_Data.gas[util_Data.gas.length -1]}</td>
    <td>$${util_Data.wifi[util_Data.wifi.length -1]}</td>
  `;

  tableBody.appendChild(bodyRow);
}

// Creates Utility Table for the Utilities Analytics Chart
function populateutilityTable() {
  const tableThread = document.querySelector('#utilityTable thead');
  const tableBody = document.querySelector('#utilityTable tbody');

  // Clear previous <thead> content
  tableThread.innerHTML = '';

  // Build <thead>
  const threadRow = document.createElement('tr');
  threadRow.innerHTML = `
    <th style="background-color: #f0f0f0;" >Month</th>
    <th style="background-color: #f0f0f0;" >${util_Data.month_labels[0]}</th>
    <th style="background-color: #f0f0f0;" >${util_Data.month_labels[1]}</th>
    <th style="background-color: #f0f0f0;" >${util_Data.month_labels[2]}</th>
    <th style="background-color: #f0f0f0;" >${util_Data.month_labels[3]}</th>
    <th style="background-color: #f0f0f0;" >${util_Data.month_labels[4]}</th>
  `;
  tableThread.appendChild(threadRow);

  // Clear previous <tbody> content
  tableBody.innerHTML = '';
  const bodyRow = document.createElement('tr');

  // Build <tbody>
  bodyRow.innerHTML = `
    <td style="background-color: #f0f0f0;"><b>Bill Cost<b></td>
    <td>$${util_Data.electricity[0]}</td>
    <td>$${util_Data.electricity[1]}</td>
    <td>$${util_Data.electricity[2]}</td>
    <td>$${util_Data.electricity[3]}</td>
    <td>$${util_Data.electricity[4]}</td>
  `;

  tableBody.appendChild(bodyRow);
}



populatemonthlyTable();

populateutilityTable();
