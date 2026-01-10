// create socket ONLY ONCE
const socket = io();

socket.on("connect", () => {
     console.log("✅ Socket connected, id =", socket.id);
});

socket.on("disconnect", () => {
     console.log("❌ Socket disconnected");
});

socket.on("live_prices", function (data) {

     latestPrices = data.stocks;

     // INDEX UPDATE
     for (const token in data.index) {
          console.log("Live index:", data);
          updateUI(token, data.index[token]);
     }

     // STOCK UPDATE (future use)
     for (const token in data.stocks) {
          console.log("Live stocks:", data);
          updateUI(token, data.stocks[token]);
     }
});

function updateUI(token, info) {
     const el = document.getElementById(token);
     if (!el) return;

     const priceEl = el.querySelector(".price");
     const changeEl = el.querySelector(".change");

     priceEl.innerText = info.ltp.toFixed(2);

     const sign = info.change >= 0 ? "+" : "";
     changeEl.innerText =
          `${sign}${info.change.toFixed(2)} (${info.percent_change.toFixed(2)}%)`;

     changeEl.classList.remove("up", "down");
     changeEl.classList.add(info.change >= 0 ? "up" : "down");
}


let latestPrices = {};
const row = document.getElementById("stocksRow");

// fetch watchlist stocks from backend
fetch("/stocks/watchlist")
     .then(res => res.json())
     .then(stocks => {
          buildDashboardWatchlist(stocks);

          // apply prices if socket already came
          Object.keys(latestPrices).forEach(token => {
               updateUI(token, latestPrices[token]);
          });
     });

// build watchlist UI
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
          
          // click → stock detail
          wrapper.addEventListener("click", (e) => {
               e.stopPropagation(); // safety
               console.log("Clicked token:", stock.token);
               window.location.href = `/stocks/${stock.token}`;
          });
          
          row.appendChild(wrapper);
     });
}