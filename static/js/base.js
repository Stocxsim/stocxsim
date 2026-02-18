document.addEventListener("DOMContentLoaded", () => {

  // Tabs
  window.selectTab = function (element) {
    document.querySelectorAll('.tab-item')
      .forEach(tab => tab.classList.remove('active'));
    element.classList.add('active');
  };

  // Profile dropdown
  window.toggleProfile = function () {
    const dropdown = document.getElementById("profileDropdown");
    const wrapper = document.querySelector(".profile-wrapper");
    if (dropdown) {
      dropdown.classList.toggle("show");
      if (wrapper) wrapper.classList.toggle("open", dropdown.classList.contains("show"));
    }
  };

  document.addEventListener("click", (e) => {
    const dropdown = document.getElementById("profileDropdown");
    const profileWrapper = document.querySelector(".profile-wrapper");

    if (!dropdown || !profileWrapper) return;

    // If click is outside the profile wrapper, close the dropdown
    if (!profileWrapper.contains(e.target)) {
      dropdown.classList.remove("show");
      profileWrapper.classList.remove("open");
    }
  });


  // Search
  const input = document.getElementById("searchInput");
  const resultsBox = document.getElementById("searchResults");

  if (!input || !resultsBox) return;

  input.addEventListener("input", async function () {
    const query = this.value.trim();
    resultsBox.innerHTML = "";

    if (!query) {
      resultsBox.style.display = "none";
      return;
    }

    try {
      const res = await fetch(`/stocks/search?q=${query}`);
      const stocks = await res.json();

      if (!stocks.length) {
        resultsBox.innerHTML =
          `<div class="search-item disabled">No stocks found</div>`;
        resultsBox.style.display = "block";
        return;
      }

      stocks.forEach(stock => {
        const div = document.createElement("div");
        div.className = "search-item";
        div.innerHTML = `
          <div class="search-item-info">
            <span class="search-item-symbol">${stock.symbol || stock.name}</span>
            <span class="search-item-name">${stock.name}</span>
          </div>
          ${stock.exchange ? `<span class="search-item-exchange">${stock.exchange}</span>` : ""}
        `;
        div.onclick = () =>
          window.location.href = `/stocks/${stock.token}`;
        resultsBox.appendChild(div);
      });

      resultsBox.style.display = "block";
    } catch (e) {
      console.error(e);
    }
  });

  // Close search when clicking outside
  document.addEventListener("click", (e) => {
    const searchBox = document.querySelector(".search-box");
    const resultsBox = document.getElementById("searchResults");

    if (!searchBox || !resultsBox) return;

    // If click is outside search box
    if (!searchBox.contains(e.target)) {
      resultsBox.style.display = "none";
    }
  });

  // Close search on Escape
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      const resultsBox = document.getElementById("searchResults");
      if (resultsBox) resultsBox.style.display = "none";
    }
  });


  // live market socket
  if (typeof io === 'undefined') {
    console.log("Socket.IO not loaded");
    return;
  }

  const socket = io();

  socket.on("connect", () => {
    console.log("✅ Market socket connected:", socket.id);
  });

  socket.on("disconnect", () => {
    console.log("❌ Market socket disconnected");
  });

  // Mapping of token to display name
  const tokenToName = {
    "26000": "NIFTY",
    "19000": "SENSEX",
    "26009": "BANKNIFTY",
    "26037": "FINNIFTY"
  };

  socket.on("live_prices", (data) => {

    if (!data || !data.index) return;

    for (const token in data.index) {
      const name = tokenToName[token];
      if (name) {
        updateTicker(name, data.index[token]);
      }
    }
  });

  // Fallback: if index live ticks are delayed (common right after startup),
  // fetch a one-time snapshot so SENSEX/NIFTY render without refresh.
  setTimeout(async () => {
    try {
      const sensexEl = document.getElementById("SENSEX");
      const priceEl = sensexEl?.querySelector?.(".price");
      if (!priceEl) return;

      const current = (priceEl.innerText || "").trim();
      if (current && current !== "--") return;

      const res = await fetch("/stocks/index/snapshot", { cache: "no-store" });
      const snap = await res.json();
      if (!snap || !snap.index) return;

      for (const token in snap.index) {
        const name = tokenToName[token];
        if (name) updateTicker(name, snap.index[token]);
      }
    } catch (e) {
      console.error("Index snapshot fallback failed", e);
    }
  }, 1500);

  /* ===============================
     TICKER UI UPDATE
  =============================== */
  function updateTicker(token, info) {
    const el = document.getElementById(token);
    if (!el) return;

    const priceEl = el.querySelector(".price");
    const changeEl = el.querySelector(".change");

    if (!priceEl || !changeEl) return;

    const ltp = Number(info?.ltp);
    const change = Number(info?.change);
    const percent = Number(info?.percent_change);
    if (!Number.isFinite(ltp)) return;

    // Price
    priceEl.innerText = ltp.toFixed(2);

    // Change (+ percent)
    const sign = Number.isFinite(change) && change >= 0 ? "+" : "";
    if (Number.isFinite(change) && Number.isFinite(percent)) {
      changeEl.innerText = `${sign}${change.toFixed(2)} (${percent.toFixed(2)}%)`;
    } else if (Number.isFinite(change)) {
      changeEl.innerText = `${sign}${change.toFixed(2)}`;
    } else {
      changeEl.innerText = "--";
    }

    // Remove old classes
    priceEl.classList.remove("up", "down");
    changeEl.classList.remove("up", "down");

    const cls = Number.isFinite(change) && change >= 0 ? "up" : "down";
    priceEl.classList.add(cls);
    changeEl.classList.add(cls);
  }
});


const logout = document.getElementById("logoutBtn");
if (logout) {
  logout.addEventListener("click", async () => {
    try {
      const res = await fetch('/login/logout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (res.ok) {
        window.location.href = '/';
      } else {
        console.error('Logout failed');
      }
    } catch (e) {
      console.error('Error during logout:', e);
    }
  });
} 


function goToProfile(e) {
  e.stopPropagation();
  window.location.href = "/profile";
}
function goToFunds() {
  window.location.href = "/profile/funds";
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

