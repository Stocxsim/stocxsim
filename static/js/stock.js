// =========================
// Global variables
// =========================
const STOCK_TOKEN = document.body.dataset.stockToken;
const stockPageEl = document.getElementById("stockPage");
const socket = io();

let transactionType = "buy";
let isWatchlisted = false;
window.lastLTP = 0;

// UI Elements
const qtyInput = document.getElementById("qty");
const priceInput = document.getElementById("price");
const approxReqEl = document.querySelector(".info-row span:last-child");
const balanceEl = document.querySelector(".info-row span:first-child");
const buyTab = document.getElementById("buy-tab");
const sellTab = document.getElementById("sell-tab");
const submitBtn = document.getElementById("submitOrderBtn");

// listeners to update the "Approx req" as type
qtyInput.addEventListener("input", updateApproxReq);
priceInput.addEventListener("input", updateApproxReq);


// Example usage
const stockToken = document.body.dataset.stockToken;


// =========================
// SOCKET EVENTS
// =========================
socket.on("connect", () => {
     console.log("✅ Socket connected:", socket.id);
});

socket.on("disconnect", () => {
     console.log("❌ Socket disconnected");
});

const EMA_20 = parseFloat(stockPageEl?.dataset.ema20 || "0");

socket.on("live_prices", (data) => {

     if (!data.stocks || !data.stocks[STOCK_TOKEN]) {
          console.warn("Stock not in feed yet:", STOCK_TOKEN);
          return;
     }

     const stock = data.stocks[STOCK_TOKEN];
     if (stock && stock.ltp) {
          updateStockUI(stock);
          setEmaGauge(stock.ltp, EMA_20);
     }
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
     if (!priceInput.value) {
          priceInput.value = stock.ltp.toFixed(2);
     }
     updateApproxReq();
}


let orderType = "market"; // market | mtf

// =========================
// DELIVERY / MTF TOGGLE
// =========================
const orderTypeText = document.getElementById("orderTypeText");

function syncPriceUIForOrderType() {
     if (!priceInput) return;

     if (orderType === "mtf") {
          if (orderTypeText) orderTypeText.innerText = "MTF";
          priceInput.disabled = false;
          if (!priceInput.value && window.lastLTP) {
               priceInput.value = window.lastLTP.toFixed(2);
          }
     } else {
          if (orderTypeText) orderTypeText.innerText = "Market";
          priceInput.disabled = true;
          if (window.lastLTP) {
               priceInput.value = window.lastLTP.toFixed(2);
          }
     }
}

document.querySelectorAll(".order-type-chips .chip").forEach((chip) => {
     chip.addEventListener("click", () => {
          document
               .querySelectorAll(".order-type-chips .chip")
               .forEach((c) => c.classList.remove("active"));

          chip.classList.add("active");

          orderType = chip.dataset.type || "market";
          syncPriceUIForOrderType();
          updateApproxReq();
     });
});

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

     updateApproxReq();
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

     updateApproxReq();
});

// =========================
// SUBMIT ORDER
// =========================
submitBtn.addEventListener("click", async function () {

     const currentTransactionType = transactionType;
     const currentOrderType = orderType;

     const qtyValue = document.getElementById("qty").value.trim();
     const priceValue = document.getElementById("price").value.trim();

     // =========================
     // VALIDATION
     // =========================
     if (!qtyValue || isNaN(qtyValue) || Number(qtyValue) <= 0) {
          alert("❌ Give valid quantity");
          return;
     }

     if (currentOrderType === "mtf") {
          if (!priceValue || isNaN(priceValue) || Number(priceValue) <= 0) {
               alert("❌ Give valid price for MTF");
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
     // Calculate Total Value
     // const totalOrderValue = Number(qtyValue) * Number(priceValue);

     try {
          // const response = await fetch("/login/get-balance");
          // const balanceData = await response.json();
          // const currentBalance = balanceData.balance;


          // // Balance check for BUY orders
          // if (currentTransactionType === "buy") {
          //      if (totalOrderValue > currentBalance) {
          //           alert(`❌ Insufficient Balance!\nRequired: ₹${totalOrderValue.toFixed(2)}\nAvailable: ₹${currentBalance.toFixed(2)}`);
          //           return; // Stop the process
          //      }
          // }

          // place order

          const orderRes = await fetch("/trade/order", {
               method: "POST",
               headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
               },
               body: new URLSearchParams(payload)
          });

          const orderData = await orderRes.json();

          if (orderData.error) {
               alert("❌ " + orderData.error);
          } else {
               alert("✅ " + orderData.message);
               if (orderData.new_balance !== undefined) {
                    balanceEl.innerText = `Balance: ₹${orderData.new_balance.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
               }

               document.getElementById("qty").value = "1";

               updateApproxReq();
          }
     } catch (err) {
          console.error("Order error:", err);
          alert("⚠️ Connection error!");
     }

     // =========================
     // .then(res => res.json())
     // .then(data => {
     //      console.log("ORDER RESPONSE:", data);

     //      if (data.error) {
     //           alert("❌ " + data.error);
     //      } else {
     //           alert("✅ " + data.message);

     //           // optional reset
     //           document.getElementById("qty").value = "";

     //      }
     // })
     // .catch(err => {
     //      console.error("Order error:", err);
     //      alert("⚠️ Something went wrong!");
     // });
});



// =========================
// REAL-TIME COST CALCULATION
// =========================
function updateApproxReq() {
     const q = parseFloat(qtyInput.value) || 0;
     const p = parseFloat(priceInput.value) || 0;

     const total = q * p;

     // Backend behavior: MTF deducts 25% upfront
     let required = total;
     if (transactionType !== "buy") {
          required = 0;
     } else if (orderType === "mtf") {
          required = total * 0.25;
     }

     // Updates the "Approx req" text
     approxReqEl.innerHTML = `Approx req.: <b>₹${required.toLocaleString(undefined, { minimumFractionDigits: 2 })}</b>`;

     // Visual Cue: Turn text red if you can't afford it
     const balanceText = balanceEl.innerText.replace(/[^\d.]/g, "");
     const currentBal = parseFloat(balanceText) || 0;

     if (transactionType === "buy" && required > currentBal) {
          approxReqEl.style.color = "#e74c3c"; // Red
     } else {
          approxReqEl.style.color = ""; // Default
     }
}


// const orderTypeText = document.getElementById("orderTypeText");
// const priceToggle = document.getElementById("priceTypeToggle");

// // =========================
// // PRICE TYPE TOGGLE
// // =========================
// priceToggle.addEventListener("click", () => {
//      if (orderType === "limit") {
//           // 👉 LIMIT → MARKET
//           orderType = "market";
//           orderTypeText.innerText = "Market";

//           priceInput.value = window.lastLTP.toFixed(2);
//           priceInput.disabled = true;
//      } else {
//           // 👉 MARKET → LIMIT
//           orderType = "limit";
//           orderTypeText.innerText = "Limit";

//           priceInput.disabled = false;

//           // current price muki do
//           priceInput.value = window.lastLTP.toFixed(2);
//      }

//      updateApproxReq();
// });


const STOCK_RSI = parseFloat(stockPageEl?.dataset.rsi || "50");
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

     fetch("/login/get-balance")
          .then(res => res.json())
          .then(data => {
               if (data.balance !== undefined) {
                    balanceEl.innerText = `Balance: ₹${data.balance.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
               }
               updateApproxReq(); // Run once balance is loaded
          });


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

// =========================
// Back Button
// =========================

document.addEventListener("DOMContentLoaded", () => {
     const closeBtn = document.getElementById("closeStockBtn");

     if (!closeBtn) return;

     closeBtn.addEventListener("click", () => {
          /* document.referrer is the URL of the page that linked to this one.
              We check if it exists and if it belongs to your website.
           */
          if (document.referrer && document.referrer.includes(window.location.hostname)) {
               window.location.href = document.referrer;
          } else {
               // If they landed here from Google or a direct link, 
               // send them to a safe default.
               window.location.href = "/login/watchlist";
          }
     });
});