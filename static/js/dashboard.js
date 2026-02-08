const socket = io();
// Dashboard live prices (Socket.IO event: "live_prices")
// Backend payload shape: { stocks: { [token]: {ltp, change, percent_change}}, index: {...} }

// Cache latest known prices so UI can render even if socket updates come
// before watchlist cards are inserted into the DOM.
let latestPrices = {};

// socket.on("live_prices", (data) => {
//      if (!data) return;

//      // INDEX UPDATE
//      if (data.index) {
//           for (const token in data.index) updateUI(token, data.index[token]);
//      }
//      if (data.stocks) {
//           for (const token in data.stocks) updateUI(token, data.stocks[token]);
//      }
// });

if (typeof io !== "undefined") {
  const socket = io();

  socket.on("connect", () => {
    // console.log("✅ Dashboard socket connected", socket.id);
  });

  socket.on("live_prices", (payload) => {
    if (!payload) return;

    if (payload.stocks && typeof payload.stocks === "object") {
      Object.assign(latestPrices, payload.stocks);
      for (const token in payload.stocks) {
        updateUI(token, payload.stocks[token]);
      }
    }

    if (payload.index && typeof payload.index === "object") {
      Object.assign(latestPrices, payload.index);
      for (const token in payload.index) {
        updateUI(token, payload.index[token]);
      }
    }
  });
} else {
  // Socket.IO not loaded; dashboard will still show watchlist names,
  // but prices will remain "--".
  // console.log("Socket.IO not loaded");
}

// update UI for a stock/index
function updateUI(token, info) {
  const el = document.getElementById(token);
  if (!el) return;

  if (!info || info.ltp === undefined || info.ltp === null) return;

  const priceEl = el.querySelector(".price");
  const changeEl = el.querySelector(".change");

  const ltp = Number(info.ltp);
  const change = Number(info.change);
  const percent = Number(info.percent_change);

  if (priceEl && !Number.isNaN(ltp)) priceEl.innerText = ltp.toFixed(2);

  if (changeEl) {
    if (Number.isNaN(change) || Number.isNaN(percent)) return;

    const sign = change >= 0 ? "+" : "";
    changeEl.innerText = `${sign}${change.toFixed(2)} (${percent.toFixed(2)}%)`;

    changeEl.classList.remove("up", "down");
    changeEl.classList.add(change >= 0 ? "up" : "down");
  }
}

// --- Dashboard Watchlist ---
const row = document.getElementById("stocksRow");

// fetch watchlist stocks from backend
fetch("/watchlist/api")
  .then((res) => res.json())
  .then((stocks) => {
    buildDashboardWatchlist(stocks);

    // apply prices if socket already came
    const tokens = stocks.map((s) => s.token);
    if (tokens.length > 0) {
      console.log("Subscribing to tokens:", tokens);
      socket.emit("subscribe_watchlist", { tokens: tokens });
    }
  });

// Object.keys(latestPrices).forEach(token => {
//      updateUI(token, latestPrices[token]);
// });
// });

function buildDashboardWatchlist(stocks) {
  if (!row) return;
  row.innerHTML = "";
  stocks.forEach((stock) => {
    if (stock.category === "INDEX") {
      return; // Skip this iteration
    }

    const cached = latestPrices[stock.token];

    const wrapper = document.createElement("div");
    wrapper.className = "watchlist-item";
    row.style.cursor = "pointer";

    wrapper.innerHTML = `
          <div class="stock_card p-3" id="${String(stock.token)}" style="cursor: pointer;">
               <div class="stock_name mb-2">${stock.name}</div>
               <div class="stock_price price">${cached ? cached.ltp.toFixed(2) : "--"}</div>
               <div class="stock_change change ${cached ? (cached.change >= 0 ? "up" : "down") : ""}">
                    ${cached ? `${cached.change >= 0 ? "+" : ""}${cached.change.toFixed(2)} (${cached.percent_change.toFixed(2)}%)` : "--"}
               </div>
          </div>
          `;

    // click → stock detail
    wrapper.addEventListener("click", (e) => {
      e.stopPropagation(); // safety
      window.location.href = `/stocks/${stock.token}`;
    });

    row.appendChild(wrapper);
  });
}

// --- Dashboard Sidebar Totals ---
// Always use API as source of truth, never recalc from DOM
const dashboardCurrent = document.getElementById("dashboard-current");
const dashboard1d = document.getElementById("dashboard-1d");
const dashboardTotal = document.getElementById("dashboard-total");
const dashboardInvested = document.getElementById("dashboard-invested");

if (dashboardCurrent && dashboard1d && dashboardTotal && dashboardInvested) {
  // Fetch holdings/order summary for dashboard sidebar
  fetch("/holding/order")
    .then((res) => res.json())
    .then((data) => {
      if (!data || !data.holdings) return;
      updateDashboardSidebarTotals(data.holdings);
    })
    .catch(() => {
      // Do not overwrite with 0 on error
    });
}

function updateDashboardSidebarTotals(holdings) {
  // Calculate totals from holdings data (not DOM)
  let invested = 0,
    current = 0,
    totalReturn = 0,
    oneDayReturn = 0;
  holdings.forEach((h) => {
    const qty = Number(h.quantity) || 0;
    const ltp = Number(h.market_price) || 0;
    const prev =
      h.prev_close !== undefined && h.prev_close !== null
        ? Number(h.prev_close)
        : h.previous_close !== undefined
          ? Number(h.previous_close)
          : null;
    const avg = Number(h.avg_price) || 0;

    invested += qty * avg;
    current += qty * ltp;
    totalReturn += (ltp - avg) * qty;

    // 1D return: (market_price - prev_close) * quantity
    // Only add if prev_close is a valid number
    if (prev !== null && !isNaN(prev)) {
      oneDayReturn += (ltp - prev) * qty;
    }
    // If prev_close is missing, skip this holding (do not add 0 or NaN)
  });

  // Format values, never show NaN or 0 unless truly empty
  dashboardCurrent.innerText = current
    ? `₹${current.toLocaleString(undefined, { maximumFractionDigits: 2 })}`
    : "--";
  dashboardInvested.innerText = invested
    ? `₹${invested.toLocaleString(undefined, { maximumFractionDigits: 2 })}`
    : "--";
  dashboardTotal.innerText = totalReturn
    ? `${totalReturn >= 0 ? "+" : ""}${totalReturn.toLocaleString(undefined, { maximumFractionDigits: 2 })}`
    : "--";
  // 1D return: show '--' if no valid holdings, else show value
  if (
    typeof oneDayReturn === "number" &&
    !isNaN(oneDayReturn) &&
    holdings.some(
      (h) =>
        h.prev_close !== undefined &&
        h.prev_close !== null &&
        !isNaN(Number(h.prev_close)),
    )
  ) {
    dashboard1d.innerText = `${oneDayReturn >= 0 ? "+" : ""}${oneDayReturn.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
  } else {
    dashboard1d.innerText = "--";
  }
}

// --- Holdings Page: Live Price Update (if needed) ---
function updateHoldingsLivePrices(stocks) {
  // Only update DOM rows if present (holdings page)
  const rows = document.querySelectorAll(".holding-row");
  if (!rows.length) return;
  rows.forEach((row) => {
    const token = row.getAttribute("data-token");
    if (!token || !stocks[token]) return;
    const priceCell = row.querySelector(".holding-price");
    if (priceCell) priceCell.innerText = stocks[token].ltp.toFixed(2);
    // ...extend as needed for other live fields...
  });
}

function loadChart(type) {
  let url = "";

  if (type === "weekly") {
    url = "/order/history/weekly-orders-chart";
  } else if (type === "win") {
    url = "/order/history/win-rate-chart";
  } else if (type === "pl") {
    url = "/order/history/profit-loss-chart";
  } else if (type === "top") {
    url = "/order/history/top-traded-chart";
  }

  const titleEl = document.getElementById("chartTitle");

  fetch(url)
    .then(async (res) => {
      if (!res.ok) {
        const text = await res.text();
        throw new Error(
          `Chart request failed (${res.status}): ${text.slice(0, 200)}`,
        );
      }
      return res.json();
    })
    .then((data) => {
      const imgEl = document.getElementById("chartImage");
      if (!imgEl) return;
      if (type === "win") {
        imgEl.style.maxWidth = "300px";
        imgEl.style.height = "300px"; // Fixed height creates a square crop
        imgEl.style.objectFit = "cover"; // Zooms in to fill the box
        imgEl.style.objectPosition = "center"; // Keeps the pie centered
        imgEl.style.margin = "0 auto";
        imgEl.style.display = "block";
      } else {
        // ✅ Reset styles for all other chart types
        imgEl.style.maxWidth = "100%";
        imgEl.style.height = "auto";
        imgEl.style.objectFit = "";
        imgEl.style.margin = "";
        imgEl.style.display = "";
      }
      imgEl.src = "data:image/png;base64," + data.chart;
    })
    .catch((err) => {
      console.error("Chart load failed:", err);
    });
}
document.addEventListener("DOMContentLoaded", function () {
  loadChart("weekly"); // default chart
});
