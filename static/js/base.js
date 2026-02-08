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


function goToOrders() {
  window.location.href = "/login/orders";
}


