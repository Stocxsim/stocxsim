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

const formatCurrency = (val) => `₹${Number(val || 0).toFixed(2)}`;

// holding auto load
let holdingsData = {};
document.addEventListener("DOMContentLoaded", () => {
     setHoldingsLoading(true);
     loadUserHoldings();
     setupHoldingRowNavigation();
     setupLiveSocket();
});

function setupHoldingRowNavigation() {
     const container = document.getElementById("holding-body");
     if (!container) return;

     // Use event delegation so re-rendered rows keep working.
     container.addEventListener("click", (e) => {
          const row = e.target?.closest?.(".holding-row");
          if (!row) return;

          const stockToken = row.dataset.stockToken;
          if (!stockToken) return;
          window.location.href = `/stocks/${encodeURIComponent(stockToken)}`;
     });

     container.addEventListener("keydown", (e) => {
          if (e.key !== "Enter" && e.key !== " ") return;
          const row = e.target?.closest?.(".holding-row");
          if (!row) return;
          const stockToken = row.dataset.stockToken;
          if (!stockToken) return;
          e.preventDefault();
          window.location.href = `/stocks/${encodeURIComponent(stockToken)}`;
     });
}

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
     let totalInvested = 0;
     let totalCurrent = 0;
     let oneDayPnl = 0;
     let prevDayValue = 0;
     
     // NOTE: holdingsData keys are holding IDs, not stock tokens.
     // Always use h.symbol_token to map to liveStocks.
     Object.keys(holdingsData).forEach(holdingId => {
          const h = holdingsData[holdingId];
          const stockToken = String(h?.symbol_token ?? "");
          
          // 🔥 CACHE USE: Direct element uthavo (No querySelector needed)
          const cachedEls = holdingDOMCache[holdingId]; 

          // 1. Jo Live Price aavi hoy to Data update karo
          if (stockToken && liveStocks[stockToken] && liveStocks[stockToken].ltp != null) {
               const newPrice = Number(liveStocks[stockToken].ltp);
               const change = Number(liveStocks[stockToken].change);
               const pct = Number(liveStocks[stockToken].percent_change ?? liveStocks[stockToken].percent);

               if (!Number.isNaN(newPrice)) h.market_price = newPrice;
               if (!Number.isNaN(change)) h.one_day_change = change;
               if (!Number.isNaN(pct)) h.one_day_percent = pct;

               // 2. UI UPDATE (FAST): Cache mathi direct text badlo
               if (cachedEls) {
                    if (cachedEls.priceEl) {
                         cachedEls.priceEl.textContent = formatCurrency(newPrice);
                    }

                    if (cachedEls.mpSubEl) {
                         cachedEls.mpSubEl.classList.remove("up", "down");
                         cachedEls.mpSubEl.classList.add(change >= 0 ? "up" : "down");
                         cachedEls.mpSubEl.textContent = `${change >= 0 ? "+" : ""}${change.toFixed(2)} (${Math.abs(pct).toFixed(2)}%)`;
                    }
               }
          }

          // 3. Calculation Logic (Junu logic same che)
          const buyPrice = Number(h.avg_buy_price ?? 0);
          const quantity = Number(h.quantity ?? 0);
          
          let marketPrice = Number(h.market_price ?? buyPrice);
          if (marketPrice <= 0) marketPrice = buyPrice; // Fallback

          const investedValue = buyPrice * quantity;
          const currentValue = marketPrice * quantity;
          const profitLoss = currentValue - investedValue;
          const returnPercent = investedValue === 0 ? 0 : (profitLoss / investedValue) * 100;

          // 4. P&L Colors & Text Update using Cache
          if (cachedEls) {
               const plClass = returnPercent >= 0 ? "up" : "down";

               if (cachedEls.plEl) {
                    cachedEls.plEl.classList.remove("up", "down");
                    cachedEls.plEl.classList.add(plClass);
                    cachedEls.plEl.textContent = `${profitLoss >= 0 ? "+" : ""}₹${profitLoss.toFixed(2)}`;
               }

               if (cachedEls.plPctEl) {
                    cachedEls.plPctEl.classList.remove("up", "down");
                    cachedEls.plPctEl.classList.add(plClass);
                    cachedEls.plPctEl.textContent = `${returnPercent >= 0 ? "+" : ""}${returnPercent.toFixed(2)}%`;
               }

               if (cachedEls.currentEl) {
                    cachedEls.currentEl.textContent = `₹${currentValue.toFixed(2)}`;
               }
          }

          // 5. Totals Calculation
          totalInvested += investedValue;
          totalCurrent += currentValue;

          const prevClose = Number(h.prev_close ?? 0);
          if (prevClose > 0) {
               prevDayValue += prevClose * quantity;
               oneDayPnl += (marketPrice - prevClose) * quantity;
          } else if (h.one_day_change != null) {
               oneDayPnl += Number(h.one_day_change) * quantity;
          }
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
          returnsEl.classList.remove("up", "down");
          returnsEl.classList.add(totalProfit >= 0 ? "up" : "down");
     }

     const oneDayEl = document.getElementById("one-day-returns");
     if (oneDayEl) {
          oneDayEl.innerText = `${oneDayPnl >= 0 ? "+" : ""}₹${oneDayPnl.toFixed(2)} (${oneDayPercent.toFixed(2)}%)`;
          oneDayEl.classList.remove("up", "down");
          oneDayEl.classList.add(oneDayPnl >= 0 ? "up" : "down");
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
        dashboardTotal.classList.remove("up", "down");
        dashboardTotal.classList.add(totalProfit >= 0 ? "up" : "down");
    }
    if (dashboard1D) {
        dashboard1D.innerText = `${oneDayPnl >= 0 ? "+" : ""}₹${oneDayPnl.toFixed(2)} (${oneDayPercent.toFixed(2)}%)`;
        dashboard1D.classList.remove("up", "down");
        dashboard1D.classList.add(oneDayPnl >= 0 ? "up" : "down");
    }
}

function loadUserHoldings(retry = 0) {
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
               // ✅ Dashboard page only (Aa part fix karyo che)
               else {
                    let totalInvested = 0;
                    let totalCurrent = 0;
                    // 🔥 1. Aa be nava variables add karya
                    let totalOneDayPnl = 0;
                    let totalPrevDayValue = 0;

                    Object.values(data.holdings).forEach(h => {
                         const buy = Number(h.avg_buy_price ?? 0);
                         const qty = Number(h.quantity ?? 0);
                         const price = Number(h.market_price ?? buy ?? 0);
                         // 🔥 2. Prev Close value lavya calculation mate
                         const prevClose = Number(h.prev_close ?? 0);

                         totalInvested += buy * qty;
                         totalCurrent += price * qty;

                         // 🔥 3. 1D Calculation Logic add karyu
                         if (prevClose > 0) {
                              totalPrevDayValue += prevClose * qty;
                              totalOneDayPnl += (price - prevClose) * qty;
                         }
                    });

                    // 🔥 4. Have summary ma chare (4) values pass kari
                    updateHoldingsSummary(totalInvested, totalCurrent, totalOneDayPnl, totalPrevDayValue);
               }
          })
          .catch(err => {
               console.error("Holdings error:", err);
               setHoldingsLoading(true, "Unable to load holdings");
          });
}
let holdingDOMCache = {}; 

function renderHoldings(holdings) {
     const container = document.getElementById("holding-body");
     container.innerHTML = "";
     
     let totalInvested = 0;
     let totalCurrent = 0;
     
     // 🔥 Aa 2 nava variables add karya initial calculation mate
     let totalOneDayPnl = 0;
     let totalPrevDayValue = 0;

     const holdingIds = Object.keys(holdings);

     if (holdingIds.length === 0) {
          container.innerHTML = `<div class="holding-row">No holdings</div>`;
          console.log("No holdings to display");
          return;
     }

     console.log("holdings to display");

     const rows = [];

     holdingIds.forEach(holdingId => {
          const h = holdings[holdingId];
          const stockToken = String(h?.symbol_token ?? "");

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

          // 🔥 AA LOGIC MISSING HATU - Total 1D P&L Calculation
          if (prev_close > 0) {
               totalPrevDayValue += prev_close * qnt;
               totalOneDayPnl += (market_price - prev_close) * qnt;
          }

          const name = (h.stock_short_name || h.stock_name || stockToken || holdingId);
          const plClass = return_percent >= 0 ? "up" : "down";
          const mpClass = oneDayChange >= 0 ? "up" : "down";

          rows.push(
               ` <div class="holding-row" data-holding-id="${holdingId}" data-stock-token="${stockToken}" role="button" tabindex="0">
               <div>
                    <strong>${name}</strong>
                    <p>${qnt} shares · Avg. ₹${buy_price.toFixed(2)}</p>
               </div>
               <div>
                    <span class="holding-price">₹${market_price.toFixed(2)}</span>
                    <p class="holding-mp-sub ${mpClass}">${oneDayChange >= 0 ? "+" : ""}${oneDayChange.toFixed(2)} (${Math.abs(oneDayPct).toFixed(2)}%)</p>
               </div>
               <div class="${plClass}">
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

     // --- Caching Logic (Same as before) ---
     holdingDOMCache = {}; 
     const allRows = container.querySelectorAll(".holding-row");
     allRows.forEach(row => {
          const holdingId = row.dataset.holdingId;
          if (holdingId) {
               holdingDOMCache[holdingId] = {
                    priceEl: row.querySelector(".holding-price"),      
                    mpSubEl: row.querySelector(".holding-mp-sub"),     
                    plEl: row.querySelector(".holding-pl"),            
                    plPctEl: row.querySelector(".holding-pl-pct"),     
                    currentEl: row.querySelector(".holding-current")   
               };
          }
     });

     // 🔥 HAVE AAPNE 4 ARGUMENTS PASS KARISHU
     // Pehla tame fakt (totalInvested, totalCurrent) pass karta hata, etle 1D 0 aavtu hatu.
     updateHoldingsSummary(totalInvested, totalCurrent, totalOneDayPnl, totalPrevDayValue);
}