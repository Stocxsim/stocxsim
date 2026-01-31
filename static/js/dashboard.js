
// --- Dashboard.js: Refactored for single source of truth, correct totals, and no race/overwrite ---

// Only run Socket.IO if on holdings page (detect by .holding-row or #holdingsTable)
const isHoldingsPage = document.querySelector('.holding-row') || document.getElementById('holdingsTable');

if (isHoldingsPage) {
     // create socket ONLY ONCE
     const socket = io();

     socket.on("connect", () => {
          console.log("✅ Socket connected, id =", socket.id);
     });

     socket.on("disconnect", () => {
          console.log("❌ Socket disconnected");
     });

     socket.on("live_prices", function (data) {
          // Only update holdings page, not dashboard
          updateHoldingsLivePrices(data.stocks);
     });
}

// --- Dashboard Watchlist ---
const row = document.getElementById("stocksRow");
if (row) {
     fetch("/stocks/watchlist")
          .then(res => res.json())
          .then(stocks => {
               buildDashboardWatchlist(stocks);
          });
}

function buildDashboardWatchlist(stocks) {
     row.innerHTML = "";
     stocks.forEach(stock => {
          const wrapper = document.createElement("div");
          wrapper.className = "watchlist-item";
          row.style.cursor = "pointer";
          wrapper.innerHTML = `
               <div class="stock_card p-3" id="${stock.token}">
                    <div class="stock_name mb-2">${stock.name}</div>
                    <div class="stock_price price">--</div>
                    <div class="stock_change change">--</div>
               </div>
          `;
          wrapper.addEventListener("click", (e) => {
               e.stopPropagation();
               window.location.href = `/stocks/${stock.token}`;
          });
          row.appendChild(wrapper);
     });
}

// --- Dashboard Sidebar Totals ---
// Always use API as source of truth, never recalc from DOM
const dashboardCurrent = document.getElementById('dashboard-current');
const dashboard1d = document.getElementById('dashboard-1d');
const dashboardTotal = document.getElementById('dashboard-total');
const dashboardInvested = document.getElementById('dashboard-invested');


if (dashboardCurrent && dashboard1d && dashboardTotal && dashboardInvested) {
     // Fetch holdings/order summary for dashboard sidebar
     fetch("/holding/order")
          .then(res => res.json())
          .then(data => {
               if (!data || !data.holdings) return;
               updateDashboardSidebarTotals(data.holdings);
})
          .catch(() => {
               // Do not overwrite with 0 on error
          });
}

function updateDashboardSidebarTotals(holdings) {
     // Calculate totals from holdings data (not DOM)
     let invested = 0, current = 0, totalReturn = 0, oneDayReturn = 0;
     holdings.forEach(h => {
          const qty = Number(h.quantity) || 0;
          const ltp = Number(h.market_price) || 0;
          const prev = (h.prev_close !== undefined && h.prev_close !== null) ? Number(h.prev_close) : (h.previous_close !== undefined ? Number(h.previous_close) : null);
          const avg = Number(h.avg_price) || 0;

          invested += qty * avg;
          current += qty * ltp;
          totalReturn += (ltp - avg) * qty;

          // 1D return: (market_price - prev_close) * quantity
          // Only add if prev_close is a valid number
          if (prev !== null && !isNaN(prev)) {
               oneDayReturn += (ltp - prev) * qty;
          } 
          if (!isNaN(oneDayReturn) && oneDayReturn !== 0) {
    dashboard1d.innerText = `${oneDayReturn >= 0 ? '+' : ''}${oneDayReturn.toFixed(2)}`;
} else {
    dashboard1d.innerText = '--';
}
   
          // If prev_close is missing, skip this holding (do not add 0 or NaN)
     });

     // Format values, never show NaN or 0 unless truly empty
     dashboardCurrent.innerText = current ? `₹${current.toLocaleString(undefined, {maximumFractionDigits:2})}` : '--';
     dashboardInvested.innerText = invested ? `₹${invested.toLocaleString(undefined, {maximumFractionDigits:2})}` : '--';
     dashboardTotal.innerText = totalReturn ? `${totalReturn >= 0 ? '+' : ''}${totalReturn.toLocaleString(undefined, {maximumFractionDigits:2})}` : '--';
     // 1D return: show '--' if no valid holdings, else show value
     if (typeof oneDayReturn === 'number' && !isNaN(oneDayReturn) && holdings.some(h => h.prev_close !== undefined && h.prev_close !== null && !isNaN(Number(h.prev_close)))) {
          dashboard1d.innerText = `${oneDayReturn >= 0 ? '+' : ''}${oneDayReturn.toLocaleString(undefined, {maximumFractionDigits:2})}`;
     } else {
          dashboard1d.innerText = '--';
     }
}

// --- Holdings Page: Live Price Update (if needed) ---
function updateHoldingsLivePrices(stocks) {
     // Only update DOM rows if present (holdings page)
     const rows = document.querySelectorAll('.holding-row');
     if (!rows.length) return;
     rows.forEach(row => {
          const token = row.getAttribute('data-token');
          if (!token || !stocks[token]) return;
          const priceCell = row.querySelector('.holding-price');
          if (priceCell) priceCell.innerText = stocks[token].ltp.toFixed(2);
          // ...extend as needed for other live fields...
     });
}