// Test Input Data source
const util_Data = {
  util_labels: ['Electricity', 'Water', 'Gas', 'Wifi'], // Name of utilities
  util_colours: ['orange', 'blue', 'green', 'violet'], // Colour of utilities 
  month_labels: ['Jan 2025', 'Feb 2025', 'Mar 2025', 'Apr 2025', 'May 2025'], // Months of utilities data
  totalBill: [150, 175, 125, 155, 85],  // Total bill costs per month
  Electricity: [35, 32, 37, 30, 33], // Electricity costs per month
  Water: [45, 60, 50, 40, 55], // Water costs per month
  Gas: [30, 25, 20, 35, 30], // Gas costs per month
  Wifi: [40, 58, 18, 50, 45] // Wi-fi costs per month
};
// Replace later with user data fetched from webpage database



//Bill Overview Doughnut Chart: Most recent month data
const pieCtx = document.getElementById('doughnut').getContext('2d');
const pieChart = new Chart(pieCtx, {
  type: 'doughnut',
  data: {
    labels: util_Data.util_labels,
    datasets: [{
      data: [(util_Data.Electricity[util_Data.Electricity.length -1]), // Data includes latest month utilites
      (util_Data.Water[util_Data.Water.length -1]),
      (util_Data.Gas[util_Data.Gas.length -1]),
      (util_Data.Wifi[util_Data.Wifi.length -1])],
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
      data:[(util_Data.Electricity[util_Data.Electricity.length -1]), //latest month data: Replace with selected date data. 
      (util_Data.Water[util_Data.Water.length -1]),
      (util_Data.Gas[util_Data.Gas.length -1]),
      (util_Data.Wifi[util_Data.Wifi.length -1])],
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

//Utilities Analytics Chart
const utilityCtx = document.getElementById('utilityChart').getContext('2d');
const utilityChart = new Chart(utilityCtx, {
  type: 'line',
  data: {
    labels: util_Data.month_labels,
    datasets: [{
      label: 'Electrical Bill Cost',
      data: util_Data.Electricity, //Electricity utility data: Replace with selected utility data.
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


// Creates Month dropdown for the Monthly Overview
function populateMonthDropdown() {
  const select = document.getElementById('monthSelect');
  select.innerHTML = ''; // Clear existing options

  util_Data.month_labels.forEach((month, index) => {
    const option = document.createElement('option');
    option.value = month;
    option.textContent = month;
    if (index === util_Data.month_labels.length - 1) {
      option.selected = true; // Default to most recent month
    }
    select.appendChild(option);
  });
}


// Creates Monthly Table for the Monthly Overview Bar Chart
function populatemonthlyTable(monthIndex) {
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
    <td style="background-color: #f0f0f0;"><b>Bill Cost</b></td>
    <td>$${util_Data.Electricity[monthIndex]}</td>
    <td>$${util_Data.Water[monthIndex]}</td>
    <td>$${util_Data.Gas[monthIndex]}</td>
    <td>$${util_Data.Wifi[monthIndex]}</td>
  `;

  tableBody.appendChild(bodyRow);
}

// Creates Utility dropdown for the Utility Analytics
function populateUtilityDropdown() {
  const select = document.getElementById('utilitySelect');
  select.innerHTML = ''; // Clear existing options

  util_Data.util_labels.forEach((util, index) => {
    const option = document.createElement('option');
    option.value = util;
    option.textContent = util;
    select.appendChild(option);
  });
}


// Creates Utility Table for the Utilities Analytics Chart
function populateutilityTable(utility) {
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
    <td>$${util_Data[utility][0]}</td>
    <td>$${util_Data[utility][1]}</td>
    <td>$${util_Data[utility][2]}</td>
    <td>$${util_Data[utility][3]}</td>
    <td>$${util_Data[utility][4]}</td>
  `;

  tableBody.appendChild(bodyRow);
}

populateMonthDropdown();
populateUtilityDropdown();


// Switch chart data to Selected Month dropdown option 
const monthSelect = document.getElementById("monthSelect");
const monnthheading = document.getElementById("selectedMonthHeading");
monnthheading.innerHTML = `<b>${util_Data.month_labels[util_Data.month_labels.length -1]} Analytics</b>`;

monthSelect.addEventListener("change", () => {
  const selectedMonth = monthSelect.value;
  monnthheading.innerHTML = `<b>${selectedMonth} Analytics</b>`;

  const monthIndex = util_Data.month_labels.indexOf(selectedMonth);

  // Update Bar Chart
  barChart.data.datasets[0].data = [
    util_Data.Electricity[monthIndex],
    util_Data.Water[monthIndex],
    util_Data.Gas[monthIndex],
    util_Data.Wifi[monthIndex]
  ];
  barChart.update();

  // Update Monthly Table
  populatemonthlyTable(monthIndex);
});

// Switch chart data to Selected Month dropdown option 
const utilitySelect = document.getElementById("utilitySelect");
const utilityheading = document.getElementById("selectedUtilityHeading");
utilityheading.innerHTML = `<b>${utilitySelect.value} Analytics</b>`;

utilitySelect.addEventListener("change", () => {
  const selectedUtility = utilitySelect.value;
  utilityheading.innerHTML = `<b>${utilitySelect.value} Analytics</b>`;

  // Update Bar Chart
  utilityChart.data.datasets[0].data = util_Data[selectedUtility];
  utilityChart.update();

  // Update Monthly Table
  populateutilityTable(selectedUtility);
});

populatemonthlyTable(util_Data.month_labels.length -1);
populateutilityTable(utilitySelect.value);
