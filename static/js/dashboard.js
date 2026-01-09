// create socket ONLY ONCE
const socket = io();

socket.on("connect", () => {
  console.log("✅ Socket connected, id =", socket.id);
});

socket.on("disconnect", () => {
  console.log("❌ Socket disconnected");
});

socket.on("live_prices", function (data) {
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


// // listen for price updates
// socket.on("price_update", data => {
//     const token = data.token;
//     const ltp = data.ltp;

//     // find ticker by token id
//     const ticker = document.getElementById(token);
//     if (!ticker) return;

//     // update price
//     const priceDiv = ticker.querySelector(".price");
//     if (priceDiv) {
//         priceDiv.innerText = "₹" + ltp.toFixed(2);
//     }
// });

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



// Dashboard Stocks Data and Rendering for Stock cards
const stocks = [
     {
          name: "Vodafone Idea",
          price: 10.76,
          change: -1.30,
          changePct: -10.78,
     },
     {
          name: "TATSILV",
          price: 21.85,
          change: -0.46,
          changePct: -2.06,
     },
     {
          name: "Orient Technologies",
          price: 453.05,
          change: 57.80,
          changePct: 14.62,
     },
     {
          name: "Hindustan Copper",
          price: 518.30,
          change: -15.05,
          changePct: -2.82,
     }
];

const row = document.getElementById("stocksRow");
let html = "";

stocks.forEach(s => {
     const isUp = s.change > 0;

     html += `
     <div class="col-lg-3 col-md-4 col-sm-6">
          <div class="stock_card p-3">

                    <div class="stock_name mb-3">${s.name}</div>

                    <div class="stock_price">₹${s.price}</div>

                    <div class="stock_change ${isUp ? 'up' : 'down'}">
                         ${isUp ? '+' : ''}${s.change} (${isUp ? '+' : ''}${s.changePct}%)
                    </div>
          </div>
     </div>
     `;
});

row.innerHTML = html;