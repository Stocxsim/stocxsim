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
    if (dropdown) dropdown.classList.toggle("show");
  };

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
        div.textContent = stock.name;
        div.onclick = () =>
          window.location.href = `/stocks/${stock.token}`;
        resultsBox.appendChild(div);
      });

      resultsBox.style.display = "block";
    } catch (e) {
      console.error(e);
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

  /* ===============================
     TICKER UI UPDATE
  =============================== */
  function updateTicker(token, info) {
    const el = document.getElementById(token);
    if (!el) return;

    const priceEl = el.querySelector(".price");
    const changeEl = el.querySelector(".change");

    if (!priceEl || !changeEl) return;

    // Price
    priceEl.innerText = info.ltp.toFixed(2);

    // Change
    const sign = info.change >= 0 ? "+" : "";
    changeEl.innerText = `${sign}${info.change.toFixed(2)}`;

    changeEl.classList.remove("up", "down");
    changeEl.classList.add(info.change >= 0 ? "up" : "down");
  }
});