// Select tab functionality
function selectTab(element) {
     const allTabs = document.querySelectorAll('.tab-item');
     allTabs.forEach(tab => {
          tab.classList.remove('active');
     });

     element.classList.add('active');
}

// Profile dropdown toggle
function toggleProfile() {
     document.getElementById("profileDropdown").classList.toggle("show");
}

// stock search
const input = document.getElementById("searchInput");
const resultsBox = document.getElementById("searchResults");

if (input) {
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

               if (stocks.length === 0) {
                    resultsBox.innerHTML =
                         `<div class="search-item disabled">No stocks found</div>`;
                    resultsBox.style.display = "block";
                    return;
               }

               stocks.forEach(stock => {
                    const div = document.createElement("div");
                    div.className = "search-item";
                    div.textContent = `${stock.name}`;

                    div.onclick = () => {
                         resultsBox.style.display = "none";
                         input.value = "";
                         window.location.href = `/stocks/${stock.token}`;
                    };

                    resultsBox.appendChild(div);
               });

               resultsBox.style.display = "block";

          } catch (err) {
               console.error("Search error:", err);
               resultsBox.style.display = "none";
          }
     });
}


// holding auto load
let holdingsData = {};
document.addEventListener("DOMContentLoaded", () => {
     setHoldingsLoading(true);
     loadUserHoldings();
     setupLiveSocket();
});

function setHoldingsLoading(isLoading, message = "Loading holdings…") {
     const container = document.getElementById("holding-body");
     if (!container) return;

     if (isLoading) {
          container.innerHTML = `<div class="holding-loading">${message}</div>`;
     }
}

function setupLiveSocket() {
     if (typeof io === 'undefined') {
          console.log("Socket.IO not loaded");
          return;
     }

     const socket = io();

     socket.on("connect", () => {
          console.log("✅ Holdings socket connected");
     });

     socket.on("live_prices", (data) => {
          if (data && data.stocks) {
               updateHoldingPrices(data.stocks);
          }
     });

     socket.on("disconnect", () => {
          console.log("❌ Holdings socket disconnected");
     });
}

function updateHoldingPrices(liveStocks) {
     const holdingRows = document.querySelectorAll(".holding-row");

     let totalInvested = 0;
     let totalCurrent = 0;
     let oneDayPnl = 0;
     let prevDayValue = 0;
     
     holdingRows.forEach(row => {
          const token = row.dataset.token;
          if (!token || !holdingsData[token]) return;

          const h = holdingsData[token];
          const buyPrice = Number(h.avg_buy_price ?? 0);
          const quantity = Number(h.quantity ?? 0);

          // Check if live price exists
          if (liveStocks[token] && liveStocks[token].ltp != null) {
               const newPrice = Number(liveStocks[token].ltp);
               const change = Number(liveStocks[token].change);
               const pct = Number(liveStocks[token].percent_change ?? liveStocks[token].percent);

               if (!Number.isNaN(newPrice)) h.market_price = newPrice;
               if (!Number.isNaN(change)) h.one_day_change = change;
               if (!Number.isNaN(pct)) h.one_day_percent = pct;
               
               // Update market price in the row only
               const priceEl = row.querySelector(".holding-price");
               if (priceEl && !Number.isNaN(newPrice)) priceEl.textContent = `₹${newPrice.toFixed(2)}`;

               // Update 1D display
               const mpSubEl = row.querySelector(".holding-mp-sub");
               if (mpSubEl) {
                    const localChange = Number(h.one_day_change ?? 0);
                    const localPct = Number(h.one_day_percent ?? 0);
                    const mpColor = localChange >= 0 ? "#04b488" : "#ff4d4f";
                    mpSubEl.style.color = mpColor;
                    mpSubEl.textContent = `${localChange >= 0 ? "+" : ""}${localChange.toFixed(2)} (${Math.abs(localPct).toFixed(2)}%)`;
               }
          }

          // Recalculate row values (even if ltp missing, use existing market_price)
          let marketPrice = Number(h.market_price ?? buyPrice ?? 0);
          if ((!marketPrice || marketPrice <= 0) && buyPrice > 0) marketPrice = buyPrice;

          const investedValue = buyPrice * quantity;
          const currentValue = marketPrice * quantity;
          const profitLoss = currentValue - investedValue;
          const returnPercent = investedValue === 0 ? 0 : (profitLoss / investedValue) * 100;
          const color = returnPercent >= 0 ? "#04b488" : "#ff4d4f";

          // Portfolio 1D (use baseline prev_close if present, else use websocket change if present)
          const prevClose = Number(h.prev_close ?? 0);
          if (prevClose > 0) {
               prevDayValue += prevClose * quantity;
               oneDayPnl += (marketPrice - prevClose) * quantity;
          } else if (h.one_day_change != null) {
               oneDayPnl += Number(h.one_day_change ?? 0) * quantity;
          }

          const plEl = row.querySelector(".holding-pl");
          if (plEl) {
               plEl.style.color = color;
               plEl.textContent = `${profitLoss >= 0 ? "+" : ""}₹${profitLoss.toFixed(2)}`;
          }

          const plPctEl = row.querySelector(".holding-pl-pct");
          if (plPctEl) {
               plPctEl.style.color = color;
               plPctEl.textContent = `${returnPercent >= 0 ? "+" : ""}${returnPercent.toFixed(2)}%`;
          }

          const currentEl = row.querySelector(".holding-current");
          if (currentEl) currentEl.textContent = `₹${currentValue.toFixed(2)}`;

          const investedEl = row.querySelector(".holding-invested");
          if (investedEl) investedEl.textContent = `₹${investedValue.toFixed(2)}`;

          totalInvested += investedValue;
          totalCurrent += currentValue;
     });

     // Update summary totals
     updateHoldingsSummary(totalInvested, totalCurrent, oneDayPnl, prevDayValue);
}

function updateHoldingsSummary(totalInvested, totalCurrent, oneDayPnl = 0, prevDayValue = 0) {
     const totalProfit = totalCurrent - totalInvested;
     const totalReturnPercent = totalInvested === 0 ? 0 : (totalProfit / totalInvested) * 100;

     const oneDayPercent = prevDayValue === 0 ? 0 : (oneDayPnl / prevDayValue) * 100;

     const investedEl = document.getElementById("total-invested");
     if (investedEl) investedEl.innerText = `₹${Number(totalInvested).toFixed(2)}`;

     const currentEl = document.getElementById("total-current");
     if (currentEl) currentEl.innerText = `₹${Number(totalCurrent).toFixed(2)}`;

     const returnsEl = document.getElementById("total-returns");
     if (returnsEl) {
          returnsEl.innerText = `${totalProfit >= 0 ? "+" : ""}₹${totalProfit.toFixed(2)} (${totalReturnPercent.toFixed(2)}%)`;
          returnsEl.style.color = totalProfit >= 0 ? "#04b488" : "#ff4d4f";
     }

     const oneDayEl = document.getElementById("one-day-returns");
     if (oneDayEl) {
          oneDayEl.innerText = `${oneDayPnl >= 0 ? "+" : ""}₹${oneDayPnl.toFixed(2)} (${oneDayPercent.toFixed(2)}%)`;
          oneDayEl.style.color = oneDayPnl >= 0 ? "#04b488" : "#ff4d4f";
     }

      // --- Dashboard sidebar elements ---
    const dashboardInvested = document.getElementById("dashboard-invested");
    const dashboardCurrent = document.getElementById("dashboard-current");
    const dashboardTotal = document.getElementById("dashboard-total");
    const dashboard1D = document.getElementById("dashboard-1d");

    if (dashboardInvested) dashboardInvested.innerText = `₹${Number(totalInvested).toFixed(2)}`;
    if (dashboardCurrent) dashboardCurrent.innerText = `₹${Number(totalCurrent).toFixed(2)}`;
    if (dashboardTotal) {
        dashboardTotal.innerText = `${totalProfit >= 0 ? "+" : ""}₹${totalProfit.toFixed(2)} (${totalReturnPercent.toFixed(2)}%)`;
        dashboardTotal.style.color = totalProfit >= 0 ? "#04b488" : "#ff4d4f";
    }
    if (dashboard1D) {
        dashboard1D.innerText = `${oneDayPnl >= 0 ? "+" : ""}₹${oneDayPnl.toFixed(2)} (${oneDayPercent.toFixed(2)}%)`;
        dashboard1D.style.color = oneDayPnl >= 0 ? "#04b488" : "#ff4d4f";
    }
}

function loadUserHoldings() {
     setHoldingsLoading(true);
     fetch("/holding/order", {
          method: "POST",
          headers: {
               "Content-Type": "application/json"
          }
     })
          .then(res => res.json())
          .then(data => {
               if (!data.holdings || Object.keys(data.holdings).length === 0) {
                    if (retry < 1) {
                         setHoldingsLoading(true, "Unable to load holdings");
                         setTimeout(() => loadUserHoldings(retry + 1), 300);
            }
            return;
          }

               holdingsData = data.holdings;
               // ✅ Holdings page
        if (document.getElementById("holding-body")) {
            renderHoldings(data.holdings);
        } 
        // ✅ Dashboard page only
        else {
            let totalInvested = 0;
            let totalCurrent = 0;

            Object.values(data.holdings).forEach(h => {
                const buy = Number(h.avg_buy_price ?? 0);
                const qty = Number(h.quantity ?? 0);
                const price = Number(h.market_price ?? buy ?? 0);

                totalInvested += buy * qty;
                totalCurrent += price * qty;
            });

            updateHoldingsSummary(totalInvested, totalCurrent);
        }
    })
          .catch(err => {
               console.error("Holdings error:", err);
               setHoldingsLoading(true, "Unable to load holdings");
          });
}

function renderHoldings(holdings) {
     const container = document.getElementById("holding-body");
     container.innerHTML = "";
     let totalInvested = 0;
     let totalCurrent = 0;

     const tokens = Object.keys(holdings);

     if (tokens.length === 0) {
          container.innerHTML =
               `<div class="holding-row">No holdings</div>`;

          console.log("No holdings to display");
          return;
     }

     console.log("holdings to display");

     const rows = [];

     tokens.forEach(token => {
          const h = holdings[token];

          const buy_price = Number(h.avg_buy_price ?? 0);
          let market_price = Number(h.market_price ?? buy_price ?? 0);
          if ((!market_price || market_price <= 0) && buy_price > 0) market_price = buy_price;
          const qnt = Number(h.quantity ?? 0);

          const prev_close = Number(h.prev_close ?? 0);
          const oneDayChange = prev_close > 0 ? (market_price - prev_close) : 0;
          const oneDayPct = prev_close > 0 ? (oneDayChange / prev_close) * 100 : 0;

          const current_value = market_price * qnt;
          const invested_value = buy_price * qnt;
          const profit_loss = current_value - invested_value;
          const return_percent = invested_value === 0 ? 0 : (profit_loss / invested_value) * 100;

          totalInvested += invested_value;
          totalCurrent += current_value;

          const name = (h.stock_symbol || h.stock_name || token);
          const color = return_percent >= 0 ? "#04b488" : "#ff4d4f";
          const mpColor = oneDayChange >= 0 ? "#04b488" : "#ff4d4f";

          rows.push(
               ` <div class="holding-row" data-token="${token}" role="button" tabindex="0" onclick="window.location.href='/stocks/${token}'">
               <div>
                    <strong>${name}</strong>
                    <p>${qnt} shares · Avg. ₹${buy_price.toFixed(2)}</p>
               </div>
               <div>
                    <span class="holding-price">₹${market_price.toFixed(2)}</span>
                    <p class="holding-mp-sub" style="color:${mpColor};">${oneDayChange >= 0 ? "+" : ""}${oneDayChange.toFixed(2)} (${Math.abs(oneDayPct).toFixed(2)}%)</p>
               </div>
               <div style="color:${color};">
                    <span class="holding-pl">${profit_loss >= 0 ? '+' : ''}₹${profit_loss.toFixed(2)}</span>
                    <p class="holding-pl-pct">${return_percent >= 0 ? '+' : ''}${return_percent.toFixed(2)}%</p>
               </div>
               <div>
                    <span class="holding-current">₹${current_value.toFixed(2)}</span>
                    <p class="holding-invested">₹${invested_value.toFixed(2)}</p>
               </div>
          </div> `
          );
     });

     container.innerHTML = rows.join("");

     updateHoldingsSummary(totalInvested, totalCurrent);
}