// const STOCK_TOKEN = "{{ stock.stock_token }}";
const STOCK_TOKEN = document.body.dataset.stockToken;
const STOCK_NAME = "{{ stock.stock_name }}";
// Grab the watchlist as a JSON string from template
const watchlistTokens = '{{ watchlist_tokens | default([]) | tojson | safe }}';

// Example usage
const stockToken = document.body.dataset.stockToken;
let isWatchlisted = watchlistTokens.includes(stockToken);
console.log("Watchlist:", watchlistTokens, "Is watchlisted?", isWatchlisted);

const socket = io();

// =========================
// SOCKET EVENTS
// =========================
socket.on("connect", () => {
     console.log("✅ Socket connected:", socket.id);
});

socket.on("disconnect", () => {
     console.log("❌ Socket disconnected");
});

const EMA_20 = parseFloat("{{ stock.ema_20 if stock.ema_20 else 0 }}");

socket.on("live_prices", (data) => {

     if (!data.stocks || !data.stocks[STOCK_TOKEN]) {
          // const stockData = feed[id] || {};
          // if (!stockData.price) {
          //      console.debug(`Waiting for feed initialization for: ${id}`);
          //      return; // Don't log a full error/warning yet
          // }
          console.warn("Stock not in feed yet:", STOCK_TOKEN);
          return;
     }

     const stock = data.stocks[STOCK_TOKEN];

     // console.log("LIVE STOCK:", stock);
     // console.log("LTP:", stock.ltp);
     // console.log("EMA:", EMA_20);

     if (stock && stock.ltp) {
          updateStockUI(stock);
          setEmaGauge(stock.ltp, EMA_20);
     }

     // 2️⃣ INDEX PAGE (future / optional)
     // Example:
     // updateIndexUI("26009", data.index["26009"]);
});


// =========================
// UPDATE STOCK UI
// =========================
function updateStockUI(stock) {
     const priceEl = document.getElementById("currentPrice");
     const changeEl = document.getElementById("priceChange");
     const exchangeId = document.getElementById("exchange-id");

     if (!priceEl || !changeEl || !exchangeId) return;

     const isUp = stock.change >= 0;
     const sign = isUp ? "+" : "";
     window.lastLTP = stock.ltp;


     // 🔹 Price
     priceEl.innerText = "₹" + stock.ltp.toFixed(2);

     // 🔹 Change line
     changeEl.innerText = `${sign}${stock.change.toFixed(2)} (${stock.percent_change.toFixed(2)}%)`;
     changeEl.className =
          "price-change " + (isUp ? "text-success" : "text-danger");

     // 🔹 Exchange row
     exchangeId.innerHTML = `
                    <span class="fw-semibold">
                    ₹${stock.ltp.toFixed(2)}
                    </span>
                    <span class="mx-1 text-muted">•</span>
                    <span class="${isUp ? 'text-success' : 'text-danger'}">
                    (${sign}${stock.percent_change.toFixed(2)}%)
                    </span>
                `;
     if (orderType === "limit") {
          priceInput.value = stock.ltp.toFixed(2);
     }

}
// =========================
// GLOBAL STATE
// =========================
let transactionType = "buy";     // buy | sell
let orderType = "limit";         // limit | market

const buyTab = document.getElementById("buy-tab");
const sellTab = document.getElementById("sell-tab");
const submitBtn = document.getElementById("submitOrderBtn");

// =========================
// BUY TAB
// =========================
buyTab.addEventListener("click", () => {
     transactionType = "buy";

     buyTab.classList.add("active");
     sellTab.classList.remove("active", "sell-active");

     submitBtn.innerText = "Buy";
     submitBtn.classList.remove("sell-btn");
     submitBtn.classList.add("buy-btn");
});

// =========================
// SELL TAB
// =========================
sellTab.addEventListener("click", () => {
     transactionType = "sell";

     sellTab.classList.add("active", "sell-active");
     buyTab.classList.remove("active");

     submitBtn.innerText = "Sell";
     submitBtn.classList.remove("buy-btn");
     submitBtn.classList.add("sell-btn");
});

// =========================
// SUBMIT ORDER
// =========================
submitBtn.addEventListener("click", function () {

     // 🔐 Snapshot (race condition avoid)
     const currentTransactionType = transactionType;
     const currentOrderType = orderType;

     const qtyValue = document.getElementById("qty").value.trim();
     const priceValue = document.getElementById("price").value.trim();

     // =========================
     // VALIDATION
     // =========================
     if (!qtyValue || isNaN(qtyValue) || Number(qtyValue) <= 0) {
          alert("❌ Valid quantity aapo");
          return;
     }

     if (currentOrderType === "limit") {
          if (!priceValue || isNaN(priceValue) || Number(priceValue) <= 0) {
               alert("❌ Valid price aapo");
               return;
          }
     }

     const payload = {
          symbol_token: STOCK_TOKEN,
          quantity: Number(qtyValue),                 // number j jaay
          order_type: currentOrderType,
          price: currentOrderType === "market" ? "" : priceValue,
          transaction_type: currentTransactionType
     };

     fetch("/trade/order", {
          method: "POST",
          headers: {
               "Content-Type": "application/x-www-form-urlencoded"
          },
          body: new URLSearchParams(payload)
     })
          .then(res => res.json())
          .then(data => {
               console.log("ORDER RESPONSE:", data);

               if (data.error) {
                    alert("❌ " + data.error);
               } else {
                    alert("✅ " + data.message);

                    // optional reset
                    document.getElementById("qty").value = "";

               }
          })
          .catch(err => {
               console.error("Order error:", err);
               alert("⚠️ Something went wrong!");
          });
});
const priceInput = document.getElementById("price");
const orderTypeText = document.getElementById("orderTypeText");
const priceToggle = document.getElementById("priceTypeToggle");

// =========================
// PRICE TYPE TOGGLE
// =========================
priceToggle.addEventListener("click", () => {
     if (orderType === "limit") {
          // 👉 LIMIT → MARKET
          orderType = "market";
          orderTypeText.innerText = "Market";

          priceInput.value = window.lastLTP.toFixed(2);
          priceInput.disabled = true;
     } else {
          // 👉 MARKET → LIMIT
          orderType = "limit";
          orderTypeText.innerText = "Limit";

          priceInput.disabled = false;

          // current price muki do
          priceInput.value = window.lastLTP.toFixed(2);
     }
});


const STOCK_RSI = parseFloat("{{ stock.rsi if stock.rsi else 50 }}");

setGauge(STOCK_RSI)
/**
 * Sets the gauge to a specific value with smooth animation.
 * @param {number} value - Range from -100 to +100
 */
function setGauge(value) {
     // Clamp value to range [-100, 100]
     value = Math.max(-100, Math.min(100, value));

     // Convert linear value to rotation angle
     // -100 → -90°, 0 → 0°, +100 → +90°
     const angle = (value / 100) * 90;

     // Apply rotation to needle group
     const needleGroup = document.querySelector('.needle-group-rsi');
     needleGroup.style.transform = `rotate(${angle}deg)`;
     needleGroup.style.transformOrigin = '160px 160px';

     // Update label text and color based on value
     updateLabel(value);
}

/**
 * Updates the label text and color based on gauge value.
 * @param {number} value - Range from -100 to +100
 */
function updateLabel(value) {
     const label = document.getElementById('label-rsi');
     let text, colorClass;

     rsi = (value / 2) + 50

     if (rsi <= 30) {
          text = 'Over Sold';
          colorClass = 'color-strong-sell';
     } else if (rsi <= 45) {
          text = 'Weak But Improving';
          colorClass = 'color-sell';
     } else if (rsi <= 55) {
          text = 'Neutral';
          colorClass = 'color-neutral';
     } else if (rsi <= 65) {
          text = 'Strong';
          colorClass = 'color-buy';
     } else {
          text = 'Over Baught';
          colorClass = 'color-strong-buy';
     }

     label.textContent = text;
     label.className = `label-text ${colorClass}`;
}

// Initialize gauge with RSI data (RSI: 0-100, convert to -100 to +100 scale)
// RSI < 30 = Oversold (Sell), RSI > 70 = Overbought (Buy), RSI 30-70 = Neutral
const rsiValue = parseFloat(STOCK_RSI);
const gaugeValue = (rsiValue - 50) * 2; // Convert 0-100 to -100 to +100
setGauge(gaugeValue);





// console.log("EMA 20:", EMA_20, "Price:", PRICE);


// =========================
// EMA GAUGE
// =========================
function setEmaGauge(price, ema20) {
     console.log("EMA DEBUG → price:", price, "ema20:", ema20);

     if (!ema20 || ema20 <= 0) {
          updateEmaLabel(0);
          return;
     }

     const gaugeValue = emaToGaugeValue(price, ema20);

     // Clamp
     const value = Math.max(-100, Math.min(100, gaugeValue));
     const angle = (value / 100) * 90;

     const needleGroup = document.querySelector('.needle-group-ema20');
     needleGroup.style.transform = `rotate(${angle}deg)`;
     needleGroup.style.transformOrigin = '160px 160px';

     updateEmaLabel(value);
}

// =========================
// EMA LABEL UPDATE
// =========================
function updateEmaLabel(gaugeValue) {
     const label = document.getElementById('label-ema20');
     let text, colorClass;

     if (gaugeValue <= -60) {
          text = 'Strong Sell';
          colorClass = 'color-strong-sell';
     } else if (gaugeValue <= -20) {
          text = 'Sell';
          colorClass = 'color-sell';
     } else if (gaugeValue < 20) {
          text = 'Neutral';
          colorClass = 'color-neutral';
     } else if (gaugeValue < 60) {
          text = 'Buy';
          colorClass = 'color-buy';
     } else {
          text = 'Strong Buy';
          colorClass = 'color-strong-buy';
     }

     label.textContent = text;
     label.className = `label-text ${colorClass}`;
}


// =========================
// EMA TO GAUGE VALUE
// =========================
function emaToGaugeValue(price, ema20) {
     let pct = ((price - ema20) / ema20) * 100; // % distance

     // Clamp between -2% to +2%
     pct = Math.max(-2, Math.min(2, pct));

     // Map -2% → -100, 0 → 0, +2% → +100
     return (pct / 2) * 100;
}

// =========================
// DYNAMIC SUBSCRIPTION & UNLOAD
// =========================

document.addEventListener("DOMContentLoaded", () => {
     if (!STOCK_TOKEN) return;

     fetch(`/stocks/subscribe/${STOCK_TOKEN}`, {
          method: "POST"
     })
          .then(async res => {
               if (!res.ok) {
                    const errorData = await res.json();
                    throw new Error(errorData.error || 'Server Error');
               }
               return res.json();
          })
          .then(data => console.log("✅ Subscribed:", data.token))
          .catch(err => console.error("❌ Subscribe failed:", err.message));
});

window.addEventListener("beforeunload", () => {
     if (!STOCK_TOKEN) return;

     if (!isWatchlisted) {
          navigator.sendBeacon(`/stocks/unsubscribe/${STOCK_TOKEN}`);
          console.log("❌ Unsubscribed:", STOCK_TOKEN);
     } else {
          console.log("⏸ Stock in watchlist, keeping subscription:", STOCK_TOKEN);
     }
});


// =========================
// WATCHLIST BUTTON
// =========================

// =========================
// WATCHLIST BUTTON (FINAL)
// =========================
document.addEventListener("DOMContentLoaded", () => {
     const watchlistBtn = document.getElementById("watchlistBtn");
     const watchlistText = document.getElementById("watchlistText");
     const stockToken = document.body.dataset.stockToken;

     if (!watchlistBtn || !stockToken) return;

     // 1. Force sync with DB truth on page load
     fetch(`/watchlist/status/${stockToken}`)
          .then(res => res.json())
          .then(data => {
               isWatchlisted = data.watchlisted;
               updateWatchlistUI();
          })
          .catch(err => console.error("❌ Watchlist status sync failed:", err));

     // 2. Toggle logic
     watchlistBtn.addEventListener("click", () => {
          // Disable button briefly to prevent double-clicks
          watchlistBtn.style.pointerEvents = "none";

          fetch(`/watchlist/toggle/${stockToken}`, {
               method: "POST",
               headers: { "Content-Type": "application/json" }
          })
               .then(res => res.json())
               .then(data => {
                    isWatchlisted = data.watchlisted;
                    updateWatchlistUI();
               })
               .finally(() => {
                    watchlistBtn.style.pointerEvents = "auto";
               });
     });

     function updateWatchlistUI() {
          if (isWatchlisted) {
               watchlistBtn.classList.add("active");
               watchlistText.innerText = "Remove";
          } else {
               watchlistBtn.classList.remove("active");
               watchlistText.innerText = "Watchlist";
          }
     }
});