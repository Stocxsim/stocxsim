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
  let current = parseFloat(amountInput.value || 0);
  if (Number.isNaN(current)) current = 0;
  amountInput.value = current + Number(value || 0);
}

async function refreshBalance() {
  const stocksEl = document.getElementById('stocksBalance');
  const cashEl = document.getElementById('cashBalance');
  if (!stocksEl && !cashEl) return;

  try {
    const res = await fetch('/login/get-balance', { headers: { 'Accept': 'application/json' } });
    const data = await res.json();
    if (!res.ok) return;
    const formatted = formatINR(data.balance);
    if (stocksEl) stocksEl.textContent = formatted;
    if (cashEl) cashEl.textContent = formatted;
  } catch (e) {
    // non-fatal
  }
}

document.getElementById("actionBtn").addEventListener("click", async function () {
  const amountInput = document.getElementById("amountInput");
  const infoBox = document.getElementById("infoBox");
  let amount = parseFloat(amountInput.value || 0);

  if (!Number.isFinite(amount) || amount <= 0) {
    showOrderBanner(
      "error",
      "Invalid amount",
      "Please enter a valid amount greater than 0."
    );
    return;
  }

  const endpoint = currentTab === 'add' ? '/login/add_funds' : '/login/withdraw_funds';
  const verbLabel = currentTab === 'add' ? 'Add money' : 'Withdraw';
  if (infoBox) infoBox.textContent = `Processing ${verbLabel.toLowerCase()}…`;

  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ amount })
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const err = data && data.error ? String(data.error) : 'request_failed';
      if (err === 'insufficient_balance') {
        showOrderBanner('error', 'Insufficient balance', 'Not enough cash to withdraw this amount.');
      } else if (err === 'unauthorized') {
        showOrderBanner('error', 'Session expired', 'Please log in again.');
      } else {
        showOrderBanner('error', 'Failed', 'Please try again.');
      }
      if (infoBox) infoBox.textContent = currentTab === 'add' ? 'Enter amount to add' : 'Enter amount to withdraw';
      return;
    }

    if (currentTab === 'add') {
      showOrderBanner('success', 'Money Added', 'Amount added to your wallet successfully.');
    } else {
      showOrderBanner('success', 'Withdrawal Successful', 'Amount withdrawn from your wallet successfully.');
    }

    amountInput.value = 0;
    await refreshBalance();
    if (infoBox) infoBox.textContent = currentTab === 'add' ? 'Enter amount to add' : 'Enter amount to withdraw';
  } catch (e) {
    showOrderBanner('error', 'Network error', 'Could not reach server.');
    if (infoBox) infoBox.textContent = currentTab === 'add' ? 'Enter amount to add' : 'Enter amount to withdraw';
  }
});

// Keep balance fresh when page loads
document.addEventListener('DOMContentLoaded', refreshBalance);

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

// For Charges breakdown (Reverse Calculation)
// Reverse calculate charges for SELL display
function calculateDelayedCharges(amount) {
  const net = parseFloat(amount);

  // TAX and Charges (Rates as per current standards, can be updated if needed)
  const STT_RATE = 0.001;
  const STAMP_DUTY_RATE = 0.00015;
  const EXCHANGE_RATE = 0.0000322
  const SEBI_RATE = 0.000001;
  const IPFT_RATE = 0.000001;
  const GST_RATE = 0.18;
  const baseDP = 13.50;
  const fixedDP = 15.93; // after 18% GST on ₹13.5 + ₹2.5 = ₹15.93

  // Gross Price (Approx)
  const combinedRate = 0.001229356;
  // reverse calculate gross from net considering all charges and taxes
  const grossValue = (net + fixedDP) / (1 - combinedRate);

  // Individual Parts (Approx)
  const stt = grossValue * STT_RATE;
  const stampDuty = grossValue * STAMP_DUTY_RATE;
  const exchangeCharges = grossValue * EXCHANGE_RATE;
  const sebiCharges = grossValue * SEBI_RATE;
  const ipftCharges = grossValue * IPFT_RATE;

  // GST (18%) on (Exchange + SEBI + IPFT + 13.50 Base DP)
  const gst = GST_RATE * (exchangeCharges + sebiCharges + ipftCharges + baseDP);
  const totalCharges = stt + stampDuty + exchangeCharges + sebiCharges + ipftCharges + gst + baseDP;

  return {
    net: net,
    gross: grossValue.toFixed(2),
    stt: stt.toFixed(3),
    stamp: stampDuty.toFixed(3),
    exch: exchangeCharges.toFixed(3),
    sebi: sebiCharges.toFixed(3),
    ipft: ipftCharges.toFixed(3),
    gst: gst.toFixed(3),
    dp: "13.50", // The base fee shown in the list (Without GST of 18%)
    totalCharges: totalCharges.toFixed(3)
  };
}

// Breakdown for charges on SELL (indicator-modal style)
function showBreakdown(amount, type) {
  const data = calculateDelayedCharges(amount);

  document.getElementById('brk_exchange').innerText = `- ${formatINR(data.exch)}`;
  document.getElementById('brk_ipft').innerText = `- ${formatINR(data.ipft)}`;
  document.getElementById('brk_gst').innerText = `- ${formatINR(data.gst)}`;
  document.getElementById('brk_sebi').innerText = `- ${formatINR(data.sebi)}`;
  document.getElementById('brk_stt').innerText = `- ${formatINR(data.stt)}`;
  document.getElementById('brk_dp').innerText = `- ${formatINR(data.dp)}`;
  document.getElementById('brk_stamp').innerText = `- ${formatINR(data.stamp)}`;

  // Summary Section
  document.getElementById('brk_gross_summary').innerText = `₹${data.gross}`;
  document.getElementById('brk_total_charges').innerText = `- ₹${data.totalCharges}`;
  document.getElementById('breakdownNet').innerText = `₹${data.net}`;

  // Open the custom modal overlay
  const overlay = document.getElementById('breakdownOverlay');
  if (overlay) {
    overlay.classList.add('active');
    document.body.classList.add('indicator-modal-open');
  }
}

function closeBreakdownModal() {
  const overlay = document.getElementById('breakdownOverlay');
  if (!overlay) return;
  overlay.classList.remove('active');
  document.body.classList.remove('indicator-modal-open');
}

// Close button
document.getElementById('breakdownCloseBtn')?.addEventListener('click', closeBreakdownModal);

// Close on overlay background click
document.getElementById('breakdownOverlay')?.addEventListener('click', function (e) {
  if (e.target === this) closeBreakdownModal();
});

// Close on Escape key
document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') {
    const overlay = document.getElementById('breakdownOverlay');
    if (overlay && overlay.classList.contains('active')) {
      closeBreakdownModal();
    }
  }
});

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
      // const amount = `${meta.sign}${formatINR(tx.amount)}`;

      // ⚡ MODIFIED: Adds the (i) button specifically for SELL
      const amountVal = formatINR(tx.amount);
      let amountDisplay = `<span class="fw-bold text-heading">${meta.sign}${amountVal}</span>`;

      if (typeLabel.includes('SELL')) {
        amountDisplay += `
            <i class="bi bi-info-circle ms-2 text-muted" 
               onclick="event.stopPropagation(); showBreakdown('${tx.amount}', '${typeLabel}')" 
               style="cursor: pointer; font-size: 0.85rem;" 
               title="View Breakdown"></i>`;
      }

      return `
        <tr>
          <td class="text-muted small">${formatDateTime(tx.created_at)}</td>
          <td><span class="badge rounded-pill ${meta.badge} txn-badge">${typeLabel}</span></td>
          <td><span class="badge bg-light text-dark border">${asset}</span></td>
          <td class="text-end fw-bold text-heading">${amountDisplay}</td>
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

function showOrderBanner(type, message, detail = "") {
  const banner = document.getElementById("orderBanner");
  if (!banner) return;

  const icon =
    type === "success"
      ? '<i class="bi bi-check-lg"></i>'
      : '<i class="bi bi-x-lg"></i>';

  banner.className = `order-banner ${type}`;
  banner.innerHTML = `
    <div class="order-banner-icon">${icon}</div>
    <div>
      <div class="order-banner-title">${message}</div>
      ${detail ? `<div class="order-banner-detail">${detail}</div>` : ""}
    </div>
    <button class="order-banner-close">&times;</button>
  `;

  banner.classList.add("show");

  banner.querySelector(".order-banner-close").onclick = () => {
    banner.classList.remove("show");
  };

  clearTimeout(banner._timer);
  banner._timer = setTimeout(() => {
    banner.classList.remove("show");
  }, 3500);
}