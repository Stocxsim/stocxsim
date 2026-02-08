const socket = io();
socket.on("connect", () => {
  console.log("✅ Socket connected:", socket.id);
});

// fetch("/stocks/watchlist")
//   .then(res => res.json())
//   .then(stocks => {
//     const tbody = document.getElementById("watchlistBody");
//     tbody.innerHTML = "";

//     stocks.forEach(stock => {
//       const isUp = stock.change >= 0;

//       const row = document.createElement("tr");
//       row.id = "token-" + stock.token;

//       row.innerHTML = `
//         <td>
//           <div class="company-cell">
//             <div class="logo">${stock.name ? stock.name[0].toUpperCase() : "?"}</div>
//             <div>
//               <div class="company-name">${stock.name}</div>
//             </div>
//           </div>
//         </td>

//         <td>
//           <span class="trend ${isUp ? "up" : "down"}">
//                 ${isUp ? "↗" : "↘"}
//           </span>
//         </td>

//         <td class="text-end">
//           ${typeof stock.price === "number"
//           ? "₹" + stock.price.toFixed(2)
//           : "--"}
//         </td>

//         <td class="text-end ${isUp ? "text-success" : "text-danger"}">
//           ${typeof stock.change === "number"
//           ? `${isUp ? "+" : ""}${stock.change} (${stock.change_pct}%)`
//           : "--"}
//         </td>

//         <td class="text-end">--</td>
//         <td class="text-end perf">L ───●── H</td>
//       `;

//       tbody.appendChild(row);
//     });
//   });
// Page load
fetch("/watchlist/api")
  .then(res => res.json())
  .then(stocks => {
    buildTable(stocks);

    // 👇 apply last known prices
    Object.keys(latestPrices).forEach(token => {
      updateWatchlistRow(token, latestPrices[token]);
    });
  });

// Live socket update
let latestPrices = {};

socket.on("live_prices", data => {
  console.log("Watchlist live prices:", data);
  latestPrices = data.stocks;
  Object.keys(data.stocks).forEach(token => {
    updateWatchlistRow(token, data.stocks[token]);
  });
});

function updateWatchlistRow(token, info) {
  const row = document.getElementById("token-" + token);
  if (!row) return; // aa token watchlist ma nathi

  const priceEl = row.querySelector(".price");
  const changeEl = row.querySelector(".change");
  const trendEl = row.querySelector(".trend");

  if (!priceEl || !changeEl || !trendEl) return;

  // safety
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

  // change + %
  changeEl.innerText =
    `${isUp ? "+" : ""}${change.toFixed(2)} (${percent.toFixed(2)}%)`;

  changeEl.classList.remove("up", "down");
  changeEl.classList.add(isUp ? "up" : "down");

  // TREND UI 
  trendEl.innerText = isUp ? "↗" : "↘";
  trendEl.classList.remove("up", "down");
  trendEl.classList.add(isUp ? "up" : "down");
}

function buildTable(stocks) {
  console.log("Building watchlist table:", stocks);
  const tbody = document.getElementById("watchlistBody");
  tbody.innerHTML = "";

  stocks.forEach(stock => {
    const isUp = stock.change >= 0;

    const row = document.createElement("tr");
    row.id = "token-" + stock.token;

    // 🔥 CLICK EVENT
    row.addEventListener("click", () => {
      const params = new URLSearchParams({
        token: stock.token,
        name: stock.name
      });

      window.location.href = `/stocks/${stock.token}`;
    });

    row.innerHTML = `
      <td>
        <div class="company-cell">
          <div class="logo">
            ${stock.name ? stock.name[0].toUpperCase() : "?"}
          </div>
          <div class="company-name">${stock.name}</div>
        </div>
      </td>

      <td>
        <span class="trend">--</span>
      </td>
      <td class="text-end price">--</td>
      <td class="text-end change">--</td>
      <td class="text-end">--</td>
    `;

    tbody.appendChild(row);
  });
}
