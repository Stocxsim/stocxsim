const socket = io();

// socket event handlers
socket.on("connect", () => {
     console.log("✅ Socket connected, id =", socket.id);
});

socket.on("disconnect", () => {
     console.log("❌ Socket disconnected");
});

socket.on("live_prices", function (data) {

     // Merge stock prices into the global object
     if (data.stocks) {
          Object.assign(latestPrices, data.stocks);
     }
     // Merge index prices as well
     if (data.index) {
          Object.assign(latestPrices, data.index);
     }

     // INDEX UPDATE
     if (data.index) {
          for (const token in data.index) updateUI(token, data.index[token]);
     }
     if (data.stocks) {
          for (const token in data.stocks) updateUI(token, data.stocks[token]);
     }
});

// update UI for a stock/index
function updateUI(token, info) {
     const el = document.getElementById(token);
     if (!el) return;

     const priceEl = el.querySelector(".price");
     const changeEl = el.querySelector(".change");

     if (priceEl) priceEl.innerText = info.ltp.toFixed(2);

     if (changeEl) {
          const sign = info.change >= 0 ? "+" : "";
          changeEl.innerText =
               `${sign}${info.change.toFixed(2)} (${info.percent_change.toFixed(2)}%)`;

          changeEl.classList.remove("up", "down");
          changeEl.classList.add(info.change >= 0 ? "up" : "down");
     }
}


let latestPrices = {};
const row = document.getElementById("stocksRow");

// fetch watchlist stocks from backend
fetch("/watchlist/api")
     .then(res => res.json())
     .then(stocks => {
          buildDashboardWatchlist(stocks);

          // apply prices if socket already came
          const tokens = stocks.map(s => s.token);
          if (tokens.length > 0) {
               console.log("Subscribing to tokens:", tokens);
               socket.emit("subscribe_watchlist", { tokens: tokens });
          }
     });

// build watchlist UI
function buildDashboardWatchlist(stocks) {
     if (!row) return;
     row.innerHTML = "";

     stocks.forEach(stock => {
          if (stock.category === 'INDEX') {
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
               <div class="stock_change change ${cached ? (cached.change >= 0 ? 'up' : 'down') : ''}">
                    ${cached ? `${cached.change >= 0 ? '+' : ''}${cached.change.toFixed(2)} (${cached.percent_change.toFixed(2)}%)` : "--"}
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