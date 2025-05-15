// static/js/visualiseData.js

// Global toggle functions (used by onclick attributes)
function toggleMonthlyView() {
  const chart = document.getElementById('barChart');
  const table = document.getElementById('monthlyTable');
  const button = event.target;
  if (table.style.display === 'none' || table.style.display === '') {
    table.style.display = 'block';
    chart.style.display = 'none';
    button.textContent = 'Switch to Chart View';
  } else {
    table.style.display = 'none';
    chart.style.display = 'block';
    button.textContent = 'Switch to Table View';
  }
}

function toggleUtilityView() {
  const chart = document.getElementById('utilityChart');
  const table = document.getElementById('utilityTable');
  const button = event.target;
  if (table.style.display === 'none' || table.style.display === '') {
    table.style.display = 'block';
    chart.style.display = 'none';
    button.textContent = 'Switch to Chart View';
  } else {
    table.style.display = 'none';
    chart.style.display = 'block';
    button.textContent = 'Switch to Table View';
  }
}

// Main initialization
document.addEventListener('DOMContentLoaded', () => {
  fetch('/api/analytics')
    .then(response => response.json())
    .then(util_Data => {
      const { util_labels, util_colours, month_labels, totalBill, util_data } = util_Data;
      const latestIdx = month_labels.length - 1;

      // Doughnut Chart (most recent month)
      const pieCtx = document.getElementById('doughnut').getContext('2d');
      new Chart(pieCtx, {
        type: 'doughnut',
        data: {
          labels: util_labels,
          datasets: [{
            data: util_labels.map(label => util_data[label][latestIdx]),
            backgroundColor: util_colours
          }]
        },
        options: {
          responsive: true,
          plugins: {
            tooltip: {
              callbacks: {
                label: ctx => `${ctx.label}: $${ctx.parsed}`
              }
            }
          }
        }
      });

      // Line Chart (total bill over months)
      const lineCtx = document.getElementById('lineChart').getContext('2d');
      new Chart(lineCtx, {
        type: 'line',
        data: {
          labels: month_labels,
          datasets: [{
            label: 'Total Monthly Bill Cost',
            data: totalBill,
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            fill: true
          }]
        },
        options: {
          responsive: true,
          scales: {
            y: { beginAtZero: true, ticks: { callback: v => '$' + v } }
          }
        }
      });

      // Bar Chart (utilities for selected month)
      const barCtx = document.getElementById('barChart').getContext('2d');
      const barChart = new Chart(barCtx, {
        type: 'bar',
        data: {
          labels: util_labels,
          datasets: [{
            label: 'Costs by Utility',
            data: util_labels.map(label => util_data[label][latestIdx]),
          }]
        },
        options: {
          responsive: true,
          scales: { y: { beginAtZero: true, ticks: { callback: v => '$' + v } } }
        }
      });

      // Utility Line Chart
      const utilityCtx = document.getElementById('utilityChart').getContext('2d');
      const utilityChart = new Chart(utilityCtx, {
        type: 'line',
        data: {
          labels: month_labels,
          datasets: [{
            label: util_labels[0],
            data: util_data[util_labels[0]],
            borderColor: util_colours[0],
            backgroundColor: 'rgba(255,165,0,0.2)',
            fill: true
          }]
        },
        options: { responsive: true, scales: { y: { beginAtZero: true } } }
      });

      // DOM references
      const monthSelect = document.getElementById('monthSelect');
      const utilitySelect = document.getElementById('utilitySelect');
      const selectedMonthHeading = document.getElementById('selectedMonthHeading');
      const selectedUtilityHeading = document.getElementById('selectedUtilityHeading');
      const monthlyTable = document.getElementById('monthlyTable');
      const utilityTable = document.getElementById('utilityTable');

      // Populate dropdowns
      function populateMonthDropdown() {
        monthSelect.innerHTML = '';
        month_labels.forEach((month, idx) => {
          const opt = document.createElement('option');
          opt.value = month;
          opt.textContent = month;
          if (idx === latestIdx) opt.selected = true;
          monthSelect.appendChild(opt);
        });
      }
      function populateUtilityDropdown() {
        utilitySelect.innerHTML = '';
        util_labels.forEach(util => {
          const opt = document.createElement('option');
          opt.value = util;
          opt.textContent = util;
          utilitySelect.appendChild(opt);
        });
      }

      // Populate tables
      function populateMonthlyTable(idx) {
        const thead = monthlyTable.querySelector('thead');
        const tbody = monthlyTable.querySelector('tbody');
        thead.innerHTML = `<tr><th>Utility</th>${util_labels.map(u => `<th>${u}</th>`).join('')}</tr>`;
        tbody.innerHTML = `<tr><td><b>Bill Cost</b></td>${util_labels.map(u => `<td>$${util_data[u][idx]}</td>`).join('')}</tr>`;
      }
      function populateUtilityTable(util) {
        const thead = utilityTable.querySelector('thead');
        const tbody = utilityTable.querySelector('tbody');
        thead.innerHTML = `<tr><th>Month</th><th>Bill Cost</th></tr>`; // 1. Replace header with just “Month” and “Bill Cost”
        tbody.innerHTML = ''; // 2. Clear old rows
        // 3. For each month, append a row [month | cost]
        month_labels.forEach((month, idx) => {
          const cost = util_data[util][idx] || 0;
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td>${month}</td>
            <td>$${cost}</td>
          `;
          tbody.appendChild(tr);
        });
      }

      //  Monthly‐Summary Renderer
      function renderMonthlySummary(idx) {
        // calculate totals & breakdown for that month
        const total   = totalBill[idx];
        const breakdown = util_labels.map(label => util_data[label][idx]);
        const avg     = (total / util_labels.length).toFixed(2);
        const maxIdx  = breakdown.indexOf(Math.max(...breakdown));
        const topUtil = util_labels[maxIdx];
        const topAmt  = breakdown[maxIdx].toFixed(2);

        // build your HTML
        const html = `
          <h3>${month_labels[idx]} Summary</h3>
          <p><strong>Total spend:</strong> $${total.toFixed(2)}</p>
          <p><strong>Average per utility:</strong> $${avg}</p>
          <p><strong>Top utility:</strong> ${topUtil} ($${topAmt})</p>
        `;

        document.getElementById('monthlySummary').innerHTML = html;
      }

      // Initial UI setup
      populateMonthDropdown();
      populateUtilityDropdown();
      selectedUtilityHeading.textContent = `${utilitySelect.value} Analytics`;
      populateMonthlyTable(latestIdx);
      populateUtilityTable(utilitySelect.value);
      // render summary for most-recent month on page load
      renderMonthlySummary(latestIdx);

      // Dropdown event listeners
      monthSelect.addEventListener('change', () => {
        const i = month_labels.indexOf(monthSelect.value);
        barChart.data.datasets[0].data = util_labels.map(u => util_data[u][i]);
        barChart.update();
        populateMonthlyTable(i);
        renderMonthlySummary(i);
      });
      utilitySelect.addEventListener('change', () => {
        const u = utilitySelect.value;
        selectedUtilityHeading.textContent = `${u} Analytics`;
        utilityChart.data.datasets[0].label = u;
        utilityChart.data.datasets[0].data = util_data[u];
        utilityChart.data.datasets[0].borderColor = util_colours[util_labels.indexOf(u)];
        utilityChart.update();
        populateUtilityTable(u);
      });

    })
    .catch(err => console.error('Analytics fetch failed:', err));
  });

// ——— EDIT‐MODAL HANDLER ———
document.addEventListener('DOMContentLoaded', () => {
  const editModal   = document.getElementById('editModal');
  const editForm    = document.getElementById('editForm');
  const closeBtn    = document.getElementById('editClose');

  // open modal when any “Edit” button is clicked
  document.querySelectorAll('.edit-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const { id, category, units, cost, start, end } = btn.dataset;
      editForm.action = `/entry/${id}/edit`;
      document.getElementById('editCategory').value = category;
      document.getElementById('editUnits').value   = units;
      document.getElementById('editCost').value    = cost;
      document.getElementById('editStart').value   = start;
      document.getElementById('editEnd').value     = end;
      editModal.style.display = 'flex';
    });
  });

  // close modal on “×”
  closeBtn.addEventListener('click', () => {
    editModal.style.display = 'none';
  });

  // also close if background clicked
  editModal.addEventListener('click', e => {
    if (e.target === editModal) editModal.style.display = 'none';
  });
});
