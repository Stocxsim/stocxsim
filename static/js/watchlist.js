const socket = io();
socket.on("connect", () => {
  console.log("✅ Socket connected:", socket.id);
});

// Page load
fetch("/watchlist/api")
  .then(res => res.json())
  .then(stocks => {
    buildTable(stocks);

    // Apply last known prices
    Object.keys(latestPrices).forEach(token => {
      updateWatchlistRow(token, latestPrices[token]);
    });
  });

// Live socket update
let latestPrices = {};

socket.on("live_prices", data => {
  latestPrices = data.stocks;
  Object.keys(data.stocks).forEach(token => {
    updateWatchlistRow(token, data.stocks[token]);
  });
});

function updateWatchlistRow(token, info) {
  const row = document.getElementById("token-" + token);
  if (!row) return;

  const priceEl = row.querySelector(".wl-price");
  const changeEl = row.querySelector(".wl-change-pill");
  const trendEl = row.querySelector(".wl-trend-pill");

  if (!priceEl || !changeEl || !trendEl) return;

  if (
    info.ltp === undefined ||
    info.change === undefined ||
    info.percent_change === undefined
  ) {
    return;
  }

  const ltp = Number(info.ltp);
  const change = Number(info.change);
  const percent = Number(info.percent_change);

  const isUp = change >= 0;

  // price update
  priceEl.innerText = "₹" + ltp.toFixed(2);

  // change pill
  changeEl.innerText =
    `${isUp ? "+" : ""}${change.toFixed(2)} (${percent.toFixed(2)}%)`;
  changeEl.classList.remove("up", "down", "neutral");
  changeEl.classList.add(isUp ? "up" : "down");

  // trend pill
  trendEl.innerText = isUp ? "↗" : "↘";
  trendEl.classList.remove("up", "down", "neutral");
  trendEl.classList.add(isUp ? "up" : "down");
}

function buildTable(stocks) {
  const container = document.getElementById("watchlistBody");
  container.innerHTML = "";

  // Update count badge
  const countBadge = document.getElementById("watchlist-count");
  if (countBadge) countBadge.textContent = stocks ? stocks.length : 0;

  if (!stocks || stocks.length === 0) {
    container.innerHTML = `
      <div class="watchlist-empty">
        <div class="empty-icon"><i class="bi bi-eye"></i></div>
        <div class="empty-title">Your watchlist is empty</div>
        <div class="empty-subtitle">Search for stocks and add them to your watchlist to track them here!</div>
      </div>`;
    return;
  }

  stocks.forEach(stock => {
    const initial = stock.name ? stock.name[0].toUpperCase() : "?";

    const row = document.createElement("div");
    row.className = "watchlist-row";
    row.id = "token-" + stock.token;

    // Click to navigate
    row.addEventListener("click", () => {
      window.location.href = `/stocks/${stock.token}`;
    });

    row.innerHTML = `
      <div class="wl-company-cell">
        <div class="wl-avatar">${initial}</div>
        <div class="wl-stock-name">${stock.name}</div>
      </div>
      <div class="wl-trend">
        <span class="wl-trend-pill neutral">--</span>
      </div>
      <div class="wl-price">--</div>
      <div class="wl-change-cell">
        <span class="wl-change-pill neutral">--</span>
      </div>
    `;

    container.appendChild(row);
  });
}
