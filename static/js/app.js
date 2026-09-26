const state = {
  currentView: 'dashboard',
  dashboard: null,
  transactions: [],
  budgets: [],
  goals: [],
  recurring: [],
  notifications: []
};

async function apiRequest(url, method = 'GET', body = null) {
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' }
  };
  if (body) options.body = JSON.stringify(body);

  try {
    const res = await fetch(url, options);
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error || `HTTP ${res.status}`);
    }
    return data.data;
  } catch (err) {
    handleApiError(err);
    throw err;
  }
}

function handleApiError(err) {
  console.error('[FinLedger API Error]:', err);
  showToast(err.message || 'An error occurred.', 'error');
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toastWrap');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerText = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

function formatCurrency(amt) {
  const val = Number(amt) || 0;
  return '₹' + val.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatDate(dateStr) {
  if (!dateStr) return 'N/A';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' });
  } catch (e) {
    return dateStr;
  }
}

function navigateTo(viewName) {
  state.currentView = viewName;

  document.querySelectorAll('.nav-item-link').forEach(link => {
    if (link.dataset.view === viewName) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });

  document.querySelectorAll('.view-section').forEach(sec => sec.classList.remove('active'));

  const target = document.getElementById(`view-${viewName}`);
  if (target) target.classList.add('active');

  if (viewName === 'dashboard') loadDashboardView();
  else if (viewName === 'transactions') loadTransactionsView();
  else if (viewName === 'budgets') loadBudgetsView();
  else if (viewName === 'goals') loadGoalsView();
  else if (viewName === 'analytics') loadAnalyticsView();
  else if (viewName === 'reports') loadReportsView();
}

async function loadDashboardView() {
  try {
    const data = await apiRequest('/api/dashboard');
    state.dashboard = data;
    renderDashboard(data);
  } catch (e) {
    console.error(e);
  }
}

function renderDashboard(data) {
  const container = document.getElementById('dashboardContent');
  if (!container) return;

  const cashFlowMax = Math.max(...data.cash_flow.map(c => Math.max(c.income, c.expenses)), 1);

  const cashFlowHtml = data.cash_flow.map(c => {
    const incH = Math.round((c.income / cashFlowMax) * 150);
    const expH = Math.round((c.expenses / cashFlowMax) * 150);
    return `
      <div class="cashflow-col">
        <div class="bar-pair">
          <div class="bar-inc" style="height: ${incH}px;" data-tooltip="Inc: ₹${c.income.toLocaleString()}"></div>
          <div class="bar-exp" style="height: ${expH}px;" data-tooltip="Exp: ₹${c.expenses.toLocaleString()}"></div>
        </div>
        <span class="col-label">${c.month}</span>
      </div>
    `;
  }).join('');

  const catRankedHtml = data.category_breakdown.slice(0, 5).map(cb => `
    <div class="cat-rank-item">
      <span class="cat-name">${cb.category}</span>
      <span class="cat-amt">${formatCurrency(cb.amount)} <small style="color:#64748b;">(${cb.percentage}%)</small></span>
    </div>
  `).join('');

  const bUsageHtml = data.budget_usage.map(bu => `
    <div style="margin-bottom:1.1rem;">
      <div style="display:flex; justify-content:space-between; font-size:0.875rem; margin-bottom:0.35rem;">
        <strong>${bu.category}</strong>
        <span>${formatCurrency(bu.spent)} / ${formatCurrency(bu.budget_amount)} (${bu.percentage}%)</span>
      </div>
      <div style="height:8px; background:#e2e8f0; border-radius:4px; overflow:hidden;">
        <div style="height:100%; width:${Math.min(100, bu.percentage)}%; background-color:${bu.percentage > 100 ? '#e11d48' : (bu.percentage >= 85 ? '#d97706' : '#059669')}; border-radius:4px; transition: width 0.5s ease;"></div>
      </div>
    </div>
  `).join('');

  const goalsHtml = data.goals.map(g => `
    <div style="margin-bottom:1.1rem;">
      <div style="display:flex; justify-content:space-between; font-size:0.875rem; margin-bottom:0.35rem;">
        <strong>${g.name}</strong>
        <span>${formatCurrency(g.saved_amount)} / ${formatCurrency(g.target_amount)}</span>
      </div>
      <div style="height:10px; background:#e2e8f0; border-radius:5px; overflow:hidden;">
        <div style="height:100%; width:${g.percentage}%; background:linear-gradient(90deg, #059669, #10b981); border-radius:5px; transition: width 0.5s ease;"></div>
      </div>
    </div>
  `).join('');

  const insightsHtml = data.insights.map(i => `<li style="margin-bottom:0.6rem; font-size:0.925rem; color:#334155;">💡 ${i}</li>`).join('');

  container.innerHTML = `
    <div class="metrics-snapshot-grid">
      <div class="metric-card">
        <div class="metric-card-lbl">Available Balance</div>
        <div class="metric-card-val">${formatCurrency(data.balance)}</div>
        <div class="metric-card-sub">Net Liquid Wealth</div>
      </div>
      <div class="metric-card">
        <div class="metric-card-lbl">Total Income</div>
        <div class="metric-card-val emerald">${formatCurrency(data.total_income)}</div>
        <div class="metric-card-sub">Current Month Total</div>
      </div>
      <div class="metric-card">
        <div class="metric-card-lbl">Total Expenses</div>
        <div class="metric-card-val red">${formatCurrency(data.total_expenses)}</div>
        <div class="metric-card-sub">Current Month Outflow</div>
      </div>
      <div class="metric-card">
        <div class="metric-card-lbl">Savings Rate</div>
        <div class="metric-card-val gold">${data.savings_rate}%</div>
        <div class="metric-card-sub">Monthly Retained %</div>
      </div>
    </div>

    <div class="dashboard-grid-layout">
      <div class="card-panel">
        <div class="card-panel-header">
          <h2 class="panel-title">Monthly Cash Flow Trend</h2>
          <span style="font-size:0.825rem; color:#64748b; font-weight:600;">Income vs Expenses</span>
        </div>
        <div class="cashflow-bars-container">
          ${cashFlowHtml}
        </div>
      </div>

      <div class="card-panel">
        <div class="card-panel-header">
          <h2 class="panel-title">Top Expense Categories</h2>
        </div>
        <div class="category-ranked-list">
          ${catRankedHtml || '<p>No expenses recorded yet.</p>'}
        </div>
      </div>
    </div>

    <div class="dashboard-grid-layout">
      <div class="card-panel">
        <div class="card-panel-header">
          <h2 class="panel-title">Category Budgets Overview</h2>
        </div>
        ${bUsageHtml}
      </div>

      <div class="card-panel">
        <div class="card-panel-header">
          <h2 class="panel-title">Savings Goals Tracker</h2>
        </div>
        ${goalsHtml}
      </div>
    </div>

    <div class="card-panel">
      <div class="card-panel-header">
        <h2 class="panel-title">Smart Financial Insights</h2>
      </div>
      <ul style="list-style:none; padding:0;">
        ${insightsHtml}
      </ul>
    </div>
  `;
}

async function loadTransactionsView() {
  try {
    const data = await apiRequest('/api/transactions');
    state.transactions = data;
    renderTransactions(data);
  } catch (e) {
    console.error(e);
  }
}

function renderTransactions(txns) {
  const container = document.getElementById('transactionsTableBody');
  if (!container) return;

  if (txns.length === 0) {
    container.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:2rem; color:#64748b;">No transactions found.</td></tr>`;
    return;
  }

  container.innerHTML = txns.map(t => `
    <tr>
      <td><code>${t.id}</code></td>
      <td><span class="type-pill ${t.type.toLowerCase()}">${t.type}</span></td>
      <td><strong>${t.description}</strong></td>
      <td>${t.category}</td>
      <td>${formatDate(t.date)}</td>
      <td><strong>${formatCurrency(t.amount)}</strong></td>
      <td>
        <button onclick="viewTransactionDetails('${t.id}')" style="background:#e2e8f0; border:none; padding:0.3rem 0.65rem; border-radius:6px; font-size:0.8rem; font-weight:600; cursor:pointer;">View</button>
        <button onclick="deleteTransaction('${t.id}')" style="background:#fff1f2; color:#e11d48; border:none; padding:0.3rem 0.65rem; border-radius:6px; font-size:0.8rem; font-weight:600; cursor:pointer; margin-left:0.3rem;">Delete</button>
      </td>
    </tr>
  `).join('');
}

function applyTransactionFilters() {
  const search = document.getElementById('txSearchInput')?.value || '';
  const type = document.getElementById('txTypeFilter')?.value || 'all';
  const category = document.getElementById('txCategoryFilter')?.value || 'all';
  const method = document.getElementById('txMethodFilter')?.value || 'all';
  const sortBy = document.getElementById('txSortFilter')?.value || 'newest';

  const params = new URLSearchParams({ search, type, category, payment_method: method, sort_by: sortBy });
  apiRequest(`/api/transactions?${params.toString()}`).then(data => {
    state.transactions = data;
    renderTransactions(data);
  });
}

async function deleteTransaction(txnId) {
  if (!confirm('Are you sure you want to delete this transaction?')) return;
  try {
    await apiRequest(`/api/transactions/${txnId}`, 'DELETE');
    showToast('Transaction deleted successfully.', 'success');
    loadTransactionsView();
  } catch (e) {
    showToast(e.message, 'error');
  }
}

async function viewTransactionDetails(txnId) {
  try {
    const t = await apiRequest(`/api/transactions/${txnId}`);
    alert(`Transaction Details:\n\nID: ${t.id}\nType: ${t.type}\nAmount: ₹${t.amount}\nCategory: ${t.category}\nDescription: ${t.description}\nDate: ${t.date}\nPayment Method: ${t.payment_method}`);
  } catch (e) {
    showToast(e.message, 'error');
  }
}

async function loadBudgetsView() {
  try {
    const data = await apiRequest('/api/budgets');
    state.budgets = data;
    renderBudgets(data);
  } catch (e) {
    console.error(e);
  }
}

function renderBudgets(budgets) {
  const container = document.getElementById('budgetsGrid');
  if (!container) return;

  container.innerHTML = budgets.map(b => `
    <div class="card-panel">
      <div class="card-panel-header">
        <h2 class="panel-title">${b.category}</h2>
        <span class="type-pill ${b.status === 'Exceeded' ? 'expense' : 'income'}">${b.status}</span>
      </div>
      <div style="font-family:var(--font-display); font-size:1.6rem; font-weight:800; margin-bottom:0.5rem;">${formatCurrency(b.spent)} / <small style="font-size:1rem; color:#64748b;">${formatCurrency(b.budget_amount)}</small></div>
      <div style="height:10px; background:#e2e8f0; border-radius:5px; overflow:hidden; margin-bottom:0.85rem;">
        <div style="height:100%; width:${Math.min(100, b.percentage)}%; background-color:${b.percentage > 100 ? '#e11d48' : (b.percentage >= 85 ? '#d97706' : '#059669')}; border-radius:5px; transition: width 0.5s ease;"></div>
      </div>
      <div style="display:flex; justify-content:space-between; font-size:0.875rem; color:#475569;">
        <span>Remaining: <strong>${formatCurrency(b.remaining)}</strong></span>
        <button onclick="deleteBudget('${b.id}')" style="background:none; border:none; color:#e11d48; font-weight:600; cursor:pointer;">Delete</button>
      </div>
    </div>
  `).join('');
}

async function deleteBudget(budgetId) {
  if (!confirm('Delete budget?')) return;
  try {
    await apiRequest(`/api/budgets/${budgetId}`, 'DELETE');
    showToast('Budget deleted.', 'success');
    loadBudgetsView();
  } catch (e) {
    showToast(e.message, 'error');
  }
}

async function loadGoalsView() {
  try {
    const data = await apiRequest('/api/goals');
    state.goals = data;
    renderGoals(data);
  } catch (e) {
    console.error(e);
  }
}

function renderGoals(goals) {
  const container = document.getElementById('goalsGrid');
  if (!container) return;

  container.innerHTML = goals.map(g => `
    <div class="card-panel">
      <div class="card-panel-header">
        <h2 class="panel-title">${g.name}</h2>
        <span style="font-size:0.8rem; background:#f1f5f9; padding:0.25rem 0.6rem; border-radius:6px; font-weight:600;">Target: ${formatDate(g.target_date)}</span>
      </div>
      <div style="font-family:var(--font-display); font-size:1.6rem; font-weight:800; color:#059669; margin-bottom:0.5rem;">${formatCurrency(g.saved_amount)} / <small style="font-size:1rem; color:#64748b;">${formatCurrency(g.target_amount)}</small></div>
      <div style="height:12px; background:#e2e8f0; border-radius:6px; overflow:hidden; margin-bottom:0.85rem;">
        <div style="height:100%; width:${g.percentage}%; background:linear-gradient(90deg, #059669, #10b981); border-radius:6px; transition: width 0.5s ease;"></div>
      </div>
      <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.875rem;">
        <span style="font-weight:700;">${g.percentage}% Achieved</span>
        <div>
          <button onclick="contributeGoal('${g.id}')" style="background:#059669; color:#fff; border:none; padding:0.35rem 0.75rem; border-radius:6px; font-weight:700; cursor:pointer;">+ Add Contribution</button>
          <button onclick="deleteGoal('${g.id}')" style="background:none; border:none; color:#e11d48; font-weight:600; cursor:pointer; margin-left:0.3rem;">Delete</button>
        </div>
      </div>
    </div>
  `).join('');
}

async function contributeGoal(goalId) {
  const amtStr = prompt('Enter contribution amount (₹):');
  if (!amtStr) return;
  const amt = parseFloat(amtStr);
  if (isNaN(amt) || amt <= 0) return alert('Invalid amount');
  try {
    await apiRequest(`/api/goals/${goalId}/contribute`, 'POST', { amount: amt });
    showToast('Contribution added!', 'success');
    loadGoalsView();
  } catch (e) {
    showToast(e.message, 'error');
  }
}

async function deleteGoal(goalId) {
  if (!confirm('Delete goal?')) return;
  try {
    await apiRequest(`/api/goals/${goalId}`, 'DELETE');
    showToast('Goal deleted.', 'success');
    loadGoalsView();
  } catch (e) {
    showToast(e.message, 'error');
  }
}

async function loadAnalyticsView() {
  try {
    const data = await apiRequest('/api/analytics');
    renderAnalytics(data);
  } catch (e) {
    console.error(e);
  }
}

function renderAnalytics(data) {
  const container = document.getElementById('analyticsContent');
  if (!container) return;

  const totalExp = data.total_expenses || 1;

  // Render Category Spending Pictorial Bar Chart
  const categoryBarsHtml = data.category_breakdown.map(c => `
    <div class="analytics-bar-row">
      <div class="bar-row-label">
        <span>${c.category}</span>
        <span>${formatCurrency(c.amount)} (${c.percentage}%)</span>
      </div>
      <div class="bar-row-track">
        <div class="bar-row-fill" style="width: ${c.percentage}%;"></div>
      </div>
    </div>
  `).join('');

  // Render Payment Method Volume Bars
  const pmMax = Math.max(...data.payment_methods.map(p => p.amount), 1);
  const pmBarsHtml = data.payment_methods.map(p => {
    const pct = Math.round((p.amount / pmMax) * 100);
    return `
      <div class="analytics-bar-row">
        <div class="bar-row-label">
          <span>💳 ${p.method}</span>
          <span>${formatCurrency(p.amount)}</span>
        </div>
        <div class="bar-row-track">
          <div class="bar-row-fill" style="width: ${pct}%; background: linear-gradient(90deg, #0d9488, #14b8a6);"></div>
        </div>
      </div>
    `;
  }).join('');

  container.innerHTML = `
    <div class="metrics-snapshot-grid">
      <div class="metric-card">
        <div class="metric-card-lbl">Net Balance</div>
        <div class="metric-card-val">${formatCurrency(data.balance)}</div>
      </div>
      <div class="metric-card">
        <div class="metric-card-lbl">Total Income</div>
        <div class="metric-card-val emerald">${formatCurrency(data.total_income)}</div>
      </div>
      <div class="metric-card">
        <div class="metric-card-lbl">Total Expenses</div>
        <div class="metric-card-val red">${formatCurrency(data.total_expenses)}</div>
      </div>
      <div class="metric-card">
        <div class="metric-card-lbl">Savings Rate</div>
        <div class="metric-card-val gold">${data.savings_rate}%</div>
      </div>
    </div>

    <!-- Category Expense Pictorial Bar Chart -->
    <div class="analytics-chart-card">
      <div class="card-panel-header">
        <h2 class="panel-title">📊 Category Spending Pictorial Analysis</h2>
        <span style="font-size:0.85rem; color:#64748b; font-weight:600;">Proportional Outflow Breakdown</span>
      </div>
      <div class="analytics-bar-chart">
        ${categoryBarsHtml || '<p>No expense data available for pictorial representation.</p>'}
      </div>
    </div>

    <!-- Payment Method Distribution Visual Chart -->
    <div class="analytics-chart-card">
      <div class="card-panel-header">
        <h2 class="panel-title">💳 Payment Method Volume Analysis</h2>
        <span style="font-size:0.85rem; color:#64748b; font-weight:600;">Channel Usage Comparison</span>
      </div>
      <div class="analytics-bar-chart">
        ${pmBarsHtml}
      </div>
    </div>
  `;
}

async function loadReportsView() {
  try {
    const data = await apiRequest('/api/reports');
    renderReports(data);
  } catch (e) {
    console.error(e);
  }
}

function renderReports(data) {
  const container = document.getElementById('reportsContent');
  if (!container) return;

  container.innerHTML = `
    <div class="card-panel">
      <div class="card-panel-header">
        <div>
          <h2 class="panel-title">${data.title}</h2>
          <span style="font-size:0.85rem; color:#64748b;">Generated on ${data.date_generated}</span>
        </div>
        <button onclick="window.print()" class="quick-act-btn" style="padding:0.5rem 1rem; font-size:0.85rem;">🖨️ Print Executive Report</button>
      </div>

      <div class="metrics-snapshot-grid" style="margin:1.75rem 0;">
        <div class="metric-card"><div class="metric-card-lbl">Income</div><div class="metric-card-val emerald">${formatCurrency(data.total_income)}</div></div>
        <div class="metric-card"><div class="metric-card-lbl">Expenses</div><div class="metric-card-val red">${formatCurrency(data.total_expenses)}</div></div>
        <div class="metric-card"><div class="metric-card-lbl">Net Savings</div><div class="metric-card-val">${formatCurrency(data.net_savings)}</div></div>
        <div class="metric-card"><div class="metric-card-lbl">Savings Rate</div><div class="metric-card-val gold">${data.savings_rate}%</div></div>
      </div>

      <h3 style="font-family:var(--font-display); font-size:1.15rem; margin-bottom:1rem;">Category Breakdown Summary</h3>
      <table class="data-table">
        <thead><tr><th>Category</th><th>Amount Spent</th><th>% Contribution</th></tr></thead>
        <tbody>
          ${data.category_breakdown.map(c => `<tr><td><strong>${c.category}</strong></td><td>${formatCurrency(c.amount)}</td><td>${c.percentage}%</td></tr>`).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function openSlidePanel(title, htmlContent) {
  const overlay = document.getElementById('slideOverlay');
  const panel = document.getElementById('slidePanel');
  const titleEl = document.getElementById('slidePanelTitle');
  const bodyEl = document.getElementById('slidePanelBody');

  if (titleEl) titleEl.innerText = title;
  if (bodyEl) bodyEl.innerHTML = htmlContent;

  overlay.classList.add('active');
  panel.classList.add('active');
}

function closeSlidePanel() {
  document.getElementById('slideOverlay')?.classList.remove('active');
  document.getElementById('slidePanel')?.classList.remove('active');
}

function openTransactionPanel(type = 'Expense') {
  const html = `
    <form id="txnForm" onsubmit="handleTransactionSubmit(event)">
      <div class="form-group">
        <label class="form-label">Transaction Type</label>
        <select id="tType" class="form-control" onchange="updateCategoriesByType(this.value)">
          <option value="Expense" ${type === 'Expense' ? 'selected' : ''}>Expense</option>
          <option value="Income" ${type === 'Income' ? 'selected' : ''}>Income</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Amount (₹)</label>
        <input type="number" step="0.01" id="tAmount" class="form-control" required placeholder="0.00" min="0.01">
      </div>
      <div class="form-group">
        <label class="form-label">Category</label>
        <select id="tCategory" class="form-control" required>
          ${getCategoryOptions(type)}
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Description</label>
        <input type="text" id="tDesc" class="form-control" required placeholder="e.g. Grocery shopping">
      </div>
      <div class="form-group">
        <label class="form-label">Date</label>
        <input type="date" id="tDate" class="form-control" required value="${new Date().toISOString().split('T')[0]}">
      </div>
      <div class="form-group">
        <label class="form-label">Payment Method</label>
        <select id="tMethod" class="form-control">
          <option value="UPI">UPI</option>
          <option value="Card">Card</option>
          <option value="Bank Transfer">Bank Transfer</option>
          <option value="Cash">Cash</option>
          <option value="Other">Other</option>
        </select>
      </div>
      <button type="submit" class="quick-act-btn" style="width:100%; margin-top:1.25rem;">Save Transaction</button>
    </form>
  `;
  openSlidePanel(`Add New ${type}`, html);
}

function getCategoryOptions(type) {
  if (type === 'Income') {
    return `<option value="Salary">Salary</option><option value="Freelance">Freelance</option><option value="Business">Business</option><option value="Interest">Interest</option><option value="Other">Other</option>`;
  }
  return `<option value="Food">Food</option><option value="Transport">Transport</option><option value="Shopping">Shopping</option><option value="Bills">Bills</option><option value="Entertainment">Entertainment</option><option value="Education">Education</option><option value="Health">Health</option><option value="Rent">Rent</option><option value="Other">Other</option>`;
}

function updateCategoriesByType(type) {
  const catEl = document.getElementById('tCategory');
  if (catEl) catEl.innerHTML = getCategoryOptions(type);
}

async function handleTransactionSubmit(e) {
  e.preventDefault();
  const payload = {
    type: document.getElementById('tType').value,
    amount: parseFloat(document.getElementById('tAmount').value),
    category: document.getElementById('tCategory').value,
    description: document.getElementById('tDesc').value,
    date: document.getElementById('tDate').value,
    payment_method: document.getElementById('tMethod').value
  };

  try {
    await apiRequest('/api/transactions', 'POST', payload);
    showToast('Transaction created successfully!', 'success');
    closeSlidePanel();
    if (state.currentView === 'dashboard') loadDashboardView();
    else if (state.currentView === 'transactions') loadTransactionsView();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function openQuickActionModal() {
  document.getElementById('quickActionModal')?.classList.add('active');
}

function closeQuickActionModal() {
  document.getElementById('quickActionModal')?.classList.remove('active');
}

function toggleNotificationDrawer() {
  document.getElementById('notifDrawer')?.classList.toggle('active');
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.nav-item-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      navigateTo(link.dataset.view);
    });
  });

  navigateTo('dashboard');
});
