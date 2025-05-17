// static/js/sharedVisualiseData.js

// ————— Toggle between Chart and Table Views —————
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

// ————— Main Initialization —————
document.addEventListener('DOMContentLoaded', () => {
  // Fetch analytics just for this shared group
  fetch(`/api/analytics/shared/${SHARE_GROUP_ID}`)
    .then(response => response.json())
    .then(util_Data => {
      const { util_labels, util_colours, month_labels, totalBill, util_data } = util_Data;
      const latestIdx = month_labels.length - 1;

      // Tips mapped by category
      const tipsMap = {
        Electricity: [
          "Unplug appliances when not in use",
          "Switch to LED or energy-efficient bulbs",
          "Run heavy appliances (washer/dryer) off-peak"
        ],
        Water: [
          "Fix leaky faucets promptly",
          "Install a low-flow shower head",
          "Only run dishwasher/washing machine with full loads"
        ],
        Gas: [
          "Use a lid on pots and pans to cook more efficiently",
          "Service your gas heater annually",
          "Lower thermostat by 1°C to save ~10% gas"
        ],
        WiFi: [
          "Restart your router monthly",
          "Update firmware for security",
          "Disable guest networks when not needed"
        ],
        Other: [
          "Track subscriptions—cancel unused ones",
          "Bundle services for volume discounts",
          "Review quarterly spending patterns"
        ]
      };

      // — Doughnut Chart (last month’s breakdown) :contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}
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

      // — Line Chart (total spend over time) :contentReference[oaicite:2]{index=2}:contentReference[oaicite:3]{index=3}
      const lineCtx = document.getElementById('lineChart').getContext('2d');
      new Chart(lineCtx, {
        type: 'line',
        data: {
          labels: month_labels,
          datasets: [{
            label: 'Total Spend',
            data: totalBill,
            fill: true,
            borderColor: 'black',
            tension: 0.3
          }]
        },
        options: { responsive: true }
      });

      // — Bar Chart (month breakdown) :contentReference[oaicite:4]{index=4}:contentReference[oaicite:5]{index=5}
      const barCtx = document.getElementById('barChart').getContext('2d');
      const barChart = new Chart(barCtx, {
        type: 'bar',
        data: {
          labels: util_labels,
          datasets: [{
            label: 'Cost per Utility',
            data: util_labels.map(u => util_data[u][latestIdx]),
            backgroundColor: util_colours
          }]
        },
        options: { responsive: true }
      });

      // — Populate dropdowns & render tables/cards :contentReference[oaicite:6]{index=6}:contentReference[oaicite:7]{index=7}
      function populateMonthDropdown() {
        month_labels.forEach(m => {
          const opt = document.createElement('option');
          opt.value = opt.text = m;
          document.getElementById('monthSelect').appendChild(opt);
        });
      }
      function populateUtilityDropdown() {
        util_labels.forEach(u => {
          const opt = document.createElement('option');
          opt.value = opt.text = u;
          document.getElementById('utilitySelect').appendChild(opt);
        });
      }

      function populateMonthlyTable(idx) {
        const tbl = document.getElementById('monthlyTable');
        tbl.querySelector('thead').innerHTML = `<tr>${util_labels.map(u => `<th>${u}</th>`).join('')}</tr>`;
        tbl.querySelector('tbody').innerHTML = `<tr>${util_labels.map(u => `<td>$${util_data[u][idx].toFixed(2)}</td>`).join('')}</tr>`;
      }
      function populateUtilityTable(util) {
        const tbl = document.getElementById('utilityTable');
        tbl.querySelector('thead').innerHTML = '<tr><th>Month</th><th>Amount</th></tr>';
        tbl.querySelector('tbody').innerHTML = month_labels.map((m,i) =>
          `<tr><td>${m}</td><td>$${util_data[util][i].toFixed(2)}</td></tr>`
        ).join('');
      }

      function renderMonthlySummary(idx) {
        const total = totalBill[idx];
        const avg = (total / util_labels.length).toFixed(2);
        const topUtil = util_labels.reduce((a,b) =>
          util_data[a][idx] > util_data[b][idx] ? a : b
        );
        const topAmt = util_data[topUtil][idx].toFixed(2);
        document.getElementById('monthlySummary').innerHTML = `
          <h3>${month_labels[idx]} Summary</h3>
          <p><strong>Total spend:</strong> $${total.toFixed(2)}</p>
          <p><strong>Average per utility:</strong> $${avg}</p>
          <p><strong>Top utility:</strong> ${topUtil} ($${topAmt})</p>
        `;
      }

      function updateUtilityCards(util, idx) {
        const arr = util_data[util];
        const cost = arr[idx];
        const avgMonth = (arr.reduce((a,b)=>a+b,0)/arr.length).toFixed(2);
        // days in month:
        const [mon,yr] = month_labels[idx].split(' ');
        const days = new Date(`${mon} 1, ${yr}`).getMonth()+1,
              totalDays = new Date(yr, days, 0).getDate();
        const avgDay = (cost/totalDays).toFixed(2);

        document.getElementById('monthlyUsageInsights').innerHTML = `
          <h3>Monthly Usage Insights</h3>
          <p><strong>${util}</strong> this month: $${cost.toFixed(2)}</p>
          <p><strong>Avg monthly:</strong> $${avgMonth}</p>
          <p><strong>Avg daily:</strong> $${avgDay}</p>
        `;
        document.getElementById('averageUsageInsights').innerHTML = `
          <h3>Average Usage Insights</h3>
          <p>Overall avg per month: $${avgMonth}</p>
        `;
        const tipsEl = document.getElementById('tipsToSave');
        tipsEl.innerHTML = `
          <h3>Tips to Save</h3>
          <ul>${(tipsMap[util]||[]).map(t=>`<li>${t}</li>`).join('')}</ul>
        `;
      }

      // Initial render
      populateMonthDropdown();
      populateUtilityDropdown();
      renderMonthlySummary(latestIdx);
      populateMonthlyTable(latestIdx);
      populateUtilityTable(document.getElementById('utilitySelect').value);
      updateUtilityCards(document.getElementById('utilitySelect').value, latestIdx);

      // Dropdown listeners
      document.getElementById('monthSelect').addEventListener('change', e => {
        const i = month_labels.indexOf(e.target.value);
        barChart.data.datasets[0].data = util_labels.map(u => util_data[u][i]);
        barChart.update();
        renderMonthlySummary(i);
        populateMonthlyTable(i);
      });
      document.getElementById('utilitySelect').addEventListener('change', e => {
        const u = e.target.value;
        updateUtilityCards(u, latestIdx);
        document.getElementById('utilityChart').remove(); // destroy old?
        // (Or update existing chart same as above)
      });

    })
    .catch(err => console.error('Shared analytics fetch failed:', err));
});

// ————— Edit‐Modal Handler (unchanged) —————
document.addEventListener('DOMContentLoaded', () => {
  const editModal = document.getElementById('editModal');
  const editForm  = document.getElementById('editForm');
  const closeBtn  = document.getElementById('editClose');

  document.querySelectorAll('.edit-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const { id, category, units, cost, start, end } = btn.dataset;
      editForm.action = `/entry/${id}/edit`;
      document.getElementById('editCategory').value = category;
      document.getElementById('editUnits').value    = units;
      document.getElementById('editCost').value     = cost;
      document.getElementById('editStart').value    = start;
      document.getElementById('editEnd').value      = end;
      editModal.style.display = 'flex';
    });
  });

  closeBtn.addEventListener('click', () => editModal.style.display = 'none');
  editModal.addEventListener('click', e => { if (e.target === editModal) editModal.style.display = 'none'; });
});
