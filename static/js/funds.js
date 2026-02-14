var currentTab = "add";

function switchTab(type) {
  const addTab = document.getElementById("addTab");
  const withdrawTab = document.getElementById("withdrawTab");
  const actionBtn = document.getElementById("actionBtn");
  const infoBox = document.getElementById("infoBox");
  const amountInput = document.getElementById("amountInput");

  if (type === "add") {
    addTab.classList.add("active");
    withdrawTab.classList.remove("active");

    actionBtn.innerText = "Add money";
    infoBox.innerText = "Enter amount to add";
    currentTab = "add";
  }
  else {
    withdrawTab.classList.add("active");
    addTab.classList.remove("active");

    actionBtn.innerText = "Withdraw";

    infoBox.innerText = "Enter amount to withdraw";
    amountInput.value = 0;
    currentTab = "withdraw";
  }
}

function addAmount(value) {
  const amountInput = document.getElementById("amountInput");
  let current = parseInt(amountInput.value || 0);
  amountInput.value = current + value;
}

document.getElementById("actionBtn").addEventListener("click", function() {
  const amountInput = document.getElementById("amountInput");
  let amount = parseInt(amountInput.value || 0);

  if (amount <= 0) {
    alert("Please enter a valid amount greater than 0.");
    return;
  }

  if (currentTab === "add") {
    window.location.href = `/login/add_funds?amount=${amount}`;
  } else {
    window.location.href = `/login/withdraw_funds?amount=${amount}`;
  }
});

function formatINR(value) {
  const number = Number(value || 0);
  try {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(number);
  } catch (e) {
    return `₹${number}`;
  }
}

function formatDateTime(value) {
  if (!value) return '-';
  const normalized = String(value).includes('T') ? String(value) : String(value).replace(' ', 'T');
  const dt = new Date(normalized);
  if (Number.isNaN(dt.getTime())) return String(value);
  return dt.toLocaleString('en-IN', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function txTypeMeta(type) {
  const t = String(type || '').toLowerCase();
  if (t.includes('add')) return { badge: 'text-bg-success', sign: '+' };
  if (t.includes('with')) return { badge: 'text-bg-warning', sign: '−' };
  if (t.includes('sell')) return { badge: 'text-bg-dark', sign: '+' };
  if (t.includes('buy')) return { badge: 'text-bg-primary', sign: '−' };
  return { badge: 'text-bg-secondary', sign: '' };
}

async function showTransaction() {
  const modalEl = document.getElementById('transactionsModal');
  const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
  modal.show();

  const tbody = document.getElementById('transactionBody');
  const loading = document.getElementById('transactionsLoading');
  const errorBox = document.getElementById('transactionsError');

  tbody.innerHTML = '';
  errorBox.classList.add('d-none');
  errorBox.innerText = '';
  loading.classList.remove('d-none');

  try {
    const response = await fetch('/transactions/', { headers: { 'Accept': 'application/json' } });
    const data = await response.json();
    if (!response.ok) throw new Error((data && data.error) ? data.error : 'Failed to load transactions');

    const list = (data && data.transactions) ? data.transactions : [];
    if (!list.length) {
      tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted py-4">No transactions yet</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(tx => {
      const asset = tx.symbol_name ? String(tx.symbol_name) : 'Wallet';
      const meta = txTypeMeta(tx.transaction_type);
      const typeLabel = String(tx.transaction_type || '—').toUpperCase();
      const amount = `${meta.sign}${formatINR(tx.amount)}`;

      return `
        <tr>
          <td class="text-muted small">${formatDateTime(tx.created_at)}</td>
          <td><span class="badge rounded-pill ${meta.badge} txn-badge">${typeLabel}</span></td>
          <td><span class="badge bg-light text-dark border">${asset}</span></td>
          <td class="text-end fw-bold text-heading">${amount}</td>
          <td class="text-center">
            <span class="badge rounded-pill bg-success-subtle text-success border border-success">Success</span>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    errorBox.innerText = err && err.message ? err.message : 'Something went wrong';
    errorBox.classList.remove('d-none');
    tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted py-4">Unable to load transactions</td></tr>`;
  } finally {
    loading.classList.add('d-none');
  }
}
