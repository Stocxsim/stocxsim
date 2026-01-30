const stockPageEl = document.getElementById("stockPage");
const STOCK_TOKEN = stockPageEl?.dataset?.stockToken ? String(stockPageEl.dataset.stockToken) : "";
const STOCK_NAME = stockPageEl?.dataset?.stockName ? String(stockPageEl.dataset.stockName) : "";
let HOLDING_QTY = Number(stockPageEl?.dataset?.holdingQty ?? 0);
const HOLDING_AVG = Number(stockPageEl?.dataset?.holdingAvg ?? 0);

const socket = io();

socket.on("connect", () => {
     console.log("✅ Socket connected:", socket.id);
});

socket.on("disconnect", () => {
     console.log("❌ Socket disconnected");
});

let EMA_20 = parseFloat(stockPageEl?.dataset?.ema20 ?? "0");

// show holding qty in UI
const holdingQtyEl = document.getElementById("holdingQty");
if (holdingQtyEl) holdingQtyEl.textContent = String(HOLDING_QTY || 0);

socket.on("live_prices", (data) => {

     if (!data.stocks || !data.stocks[STOCK_TOKEN]) {
          console.warn("Stock not in feed yet:", STOCK_TOKEN);
          return;
     }

     const stock = data.stocks[STOCK_TOKEN];

     // console.log("LIVE STOCK:", stock);
     // console.log("LTP:", stock.ltp);
     // console.log("EMA:", EMA_20);

     updateStockUI(stock);
     setEmaGauge(stock.ltp, EMA_20);

     // 2️⃣ INDEX PAGE (future / optional)
     // Example:
     // updateIndexUI("26009", data.index["26009"]);
});

function updateStockUI(stock) {
     const priceEl = document.getElementById("currentPrice");
     const changeEl = document.getElementById("priceChange");
     const exchangeId = document.getElementById("exchange-id");

     if (!priceEl || !changeEl || !exchangeId) return;

     const change = Number(stock.change ?? stock.netChange ?? 0);
     const pct = Number(stock.percent_change ?? stock.percent ?? stock.percentChange ?? 0);
     const isUp = change >= 0;
     const sign = isUp ? "+" : "";
     const ltp = Number(stock.ltp ?? 0);
     window.lastLTP = ltp;


     // 🔹 Price
     priceEl.innerText = "₹" + ltp.toFixed(2);

     // 🔹 Change line
     changeEl.innerText = `${sign}${change.toFixed(2)} (${pct.toFixed(2)}%)`;
     changeEl.className =
          "price-change " + (isUp ? "text-success" : "text-danger");

     // 🔹 Exchange row
     exchangeId.innerHTML = `
                    <span class="fw-semibold">
                    ₹${ltp.toFixed(2)}
                    </span>
                    <span class="mx-1 text-muted">•</span>
                    <span class="${isUp ? 'text-success' : 'text-danger'}">
                    (${sign}${pct.toFixed(2)}%)
                    </span>
                `;
     if (orderType === "limit") {
          priceInput.value = ltp.toFixed(2);
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
const qtyInputEl = document.getElementById("qty");

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

     if (qtyInputEl) qtyInputEl.removeAttribute("max");
});

// =========================
// SELL TAB
// =========================
sellTab.addEventListener("click", () => {
     if (!HOLDING_QTY || HOLDING_QTY <= 0) {
          alert("❌ You have 0 shares to sell");
          return;
     }
     transactionType = "sell";

     sellTab.classList.add("active", "sell-active");
     buyTab.classList.remove("active");

     submitBtn.innerText = "Sell";
     submitBtn.classList.remove("buy-btn");
     submitBtn.classList.add("sell-btn");

     if (qtyInputEl) qtyInputEl.setAttribute("max", String(HOLDING_QTY));
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

     if (currentTransactionType === "sell") {
          if (!HOLDING_QTY || HOLDING_QTY <= 0) {
               alert("❌ You have 0 shares to sell");
               return;
          }
          if (Number(qtyValue) > HOLDING_QTY) {
               alert(`❌ You can sell max ${HOLDING_QTY} shares`);
               return;
          }
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

                    // optimistic local update for SELL so UI stays consistent
                    if (currentTransactionType === "sell") {
                         HOLDING_QTY = Math.max(0, HOLDING_QTY - Number(qtyValue));
                         if (holdingQtyEl) holdingQtyEl.textContent = String(HOLDING_QTY);
                         if (qtyInputEl) qtyInputEl.setAttribute("max", String(HOLDING_QTY));
                    }

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

priceToggle.addEventListener("click", () => {
     if (orderType === "limit") {
          // 👉 LIMIT → MARKET
          orderType = "market";
          orderTypeText.innerText = "Market";

          const ltp = Number(window.lastLTP ?? 0);
          priceInput.value = ltp ? ltp.toFixed(2) : "";
          priceInput.disabled = true;
     } else {
          // 👉 MARKET → LIMIT
          orderType = "limit";
          orderTypeText.innerText = "Limit";

          priceInput.disabled = false;

          // current price muki do
          const ltp = Number(window.lastLTP ?? 0);
          priceInput.value = ltp ? ltp.toFixed(2) : "";
     }
});

let STOCK_RSI = parseFloat(stockPageEl?.dataset?.rsi ?? "50");

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

// =========================
// INDICATORS (ASYNC LOAD)
// =========================
let _indicatorPollTries = 0;
function pollIndicators() {
     if (!STOCK_TOKEN) return;
     if (_indicatorPollTries >= 8) return; // ~8 tries (quick)
     _indicatorPollTries += 1;

     fetch(`/stocks/${STOCK_TOKEN}/indicators`)
          .then(r => r.json())
          .then(data => {
               if (!data || data.status !== "ok") {
                    setTimeout(pollIndicators, 600);
                    return;
               }

               const rsi = Number(data.rsi);
               const ema20 = Number(data.ema_20);

               if (!Number.isNaN(rsi)) {
                    STOCK_RSI = rsi;
                    const gv = (rsi - 50) * 2;
                    setGauge(gv);
               }

               if (!Number.isNaN(ema20)) {
                    EMA_20 = ema20;
                    const ltp = Number(window.lastLTP ?? 0);
                    if (ltp) setEmaGauge(ltp, EMA_20);
               }
          })
          .catch(() => {
               setTimeout(pollIndicators, 800);
          });
}

// Start polling after initial paint
setTimeout(pollIndicators, 200);





// console.log("EMA 20:", EMA_20, "Price:", PRICE);


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



function emaToGaugeValue(price, ema20) {
     let pct = ((price - ema20) / ema20) * 100; // % distance

     // Clamp between -2% to +2%
     pct = Math.max(-2, Math.min(2, pct));

     // Map -2% → -100, 0 → 0, +2% → +100
     return (pct / 2) * 100;
}
