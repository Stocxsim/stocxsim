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

// Holding UI
function getHoldingQty() {
     const raw = stockPageEl?.dataset.holdingQty;
     const parsed = Number.parseInt(raw ?? "0", 10);
     return Number.isFinite(parsed) ? parsed : 0;
}

function syncHoldingUI() {
     const holdingQtyEl = document.getElementById("holdingQty");
     if (!holdingQtyEl) return;

     const holdingQty = getHoldingQty();
     holdingQtyEl.innerText = String(holdingQty);

     // UX: prevent selling more than holding
     if (qtyInput) {
          if (transactionType === "sell") {
               qtyInput.max = String(holdingQty);
               const currentQty = Number.parseInt(qtyInput.value || "0", 10) || 0;
               if (holdingQty > 0 && currentQty > holdingQty) {
                    qtyInput.value = String(holdingQty);
               }
          } else {
               qtyInput.removeAttribute("max");
          }
     }
}

// listeners to update the "Approx req" as type
qtyInput.addEventListener("input", updateApproxReq);
priceInput.addEventListener("input", updateApproxReq);



// =========================
// SOCKET EVENTS
// =========================
socket.on("connect", () => {
     console.log("✅ Socket connected:", socket.id);
});

socket.on("disconnect", () => {
     console.log("❌ Socket disconnected");
});

let EMA_20 = Number.parseFloat(stockPageEl?.dataset.ema20);
if (!Number.isFinite(EMA_20)) EMA_20 = null;

let STOCK_RSI = Number.parseFloat(stockPageEl?.dataset.rsi);
if (!Number.isFinite(STOCK_RSI)) STOCK_RSI = null;

const rsiGaugeEl = document.getElementById("rsiGauge");
const ema20GaugeEl = document.getElementById("ema20Gauge");
const rsiLoadingEl = document.getElementById("loading-rsi");
const ema20LoadingEl = document.getElementById("loading-ema20");

function setIndicatorLoading(kind, isLoading) {
     const gaugeEl = kind === "rsi" ? rsiGaugeEl : ema20GaugeEl;
     const loadingEl = kind === "rsi" ? rsiLoadingEl : ema20LoadingEl;

     if (!gaugeEl || !loadingEl) return;

     if (isLoading) {
          loadingEl.classList.remove("hidden");
          gaugeEl.classList.add("indicator-dim");
     } else {
          loadingEl.classList.add("hidden");
          gaugeEl.classList.remove("indicator-dim");
     }
}

function applyIndicators(indicators) {
     const rsi = Number(indicators?.rsi);
     const ema20 = Number(indicators?.ema_20);

     if (Number.isFinite(rsi)) {
          STOCK_RSI = rsi;
          const gaugeValue = (rsi - 50) * 2;
          setGauge(gaugeValue);
          setIndicatorLoading("rsi", false);
     }

     if (Number.isFinite(ema20) && ema20 > 0) {
          EMA_20 = ema20;
          // If we already have an LTP, update EMA gauge immediately.
          if (window.lastLTP) {
               setEmaGauge(window.lastLTP, EMA_20);
          } else {
               updateEmaLabel(0);
          }
          setIndicatorLoading("ema20", false);
     }
}

async function pollIndicatorsUntilReady() {
     if (!STOCK_TOKEN) return;

     // Show spinner if any indicator is missing.
     setIndicatorLoading("rsi", STOCK_RSI === null);
     setIndicatorLoading("ema20", EMA_20 === null);

     if (STOCK_RSI !== null && EMA_20 !== null) return;

     const start = Date.now();
     const timeoutMs = 60_000;

     const timer = setInterval(async () => {
          try {
               if ((Date.now() - start) > timeoutMs) {
                    clearInterval(timer);
                    return;
               }

               const res = await fetch(`/stocks/${STOCK_TOKEN}/indicators`, { cache: "no-store" });
               if (!res.ok) return;
               const data = await res.json();

               if (data?.status === "ok") {
                    applyIndicators(data);
                    if (STOCK_RSI !== null && EMA_20 !== null) {
                         clearInterval(timer);
                    }
               }
          } catch (_) {
               // ignore
          }
     }, 1000);
}

socket.on("live_prices", (data) => {

     if (!data.stocks || !data.stocks[STOCK_TOKEN]) {
          return;
     }

     const stock = data.stocks[STOCK_TOKEN];
     if (stock && stock.ltp) {
          updateStockUI(stock);
          if (EMA_20 !== null) {
               setEmaGauge(stock.ltp, EMA_20);
          }
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

     const ltp = Number(stock?.ltp);
     if (!Number.isFinite(ltp)) return;
     window.lastLTP = ltp;

     const change = Number(stock?.change);
     const percentChange = Number(stock?.percent_change ?? stock?.percentChange ?? stock?.percent);
     const changeOk = Number.isFinite(change);
     const percentOk = Number.isFinite(percentChange);

     const isUp = changeOk ? change >= 0 : true;
     const sign = isUp ? "+" : "";

     // 🔹 Price
     priceEl.innerText = "₹" + ltp.toFixed(2);

     // 🔹 Change line
     if (changeOk && percentOk) {
          changeEl.innerText = `${sign}${change.toFixed(2)} (${percentChange.toFixed(2)}%)`;
          changeEl.className = "price-change " + (isUp ? "up" : "down");
     } else {
          changeEl.innerText = "--";
     }

     // 🔹 Exchange row
     exchangeId.innerHTML = `
                    <span class="fw-semibold">₹${ltp.toFixed(2)}</span>
                    ${percentOk ? `<span class="mx-1 text-muted">•</span>
                    <span class="${isUp ? 'up' : 'down'}">(${sign}${percentChange.toFixed(2)}%)</span>` : ""}
                `;
     if (!priceInput.value) {
          priceInput.value = ltp.toFixed(2);
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

     syncHoldingUI();

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

     syncHoldingUI();

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

     try {
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
          approxReqEl.classList.add("text-down");
     } else {
          approxReqEl.classList.remove("text-down");
     }
}

// NOTE: STOCK_RSI is now a mutable variable set from dataset / polling.
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
// Initialize RSI gauge if RSI is already available; otherwise show spinner.
if (STOCK_RSI !== null) {
     const gaugeValue = (STOCK_RSI - 50) * 2; // Convert 0-100 to -100 to +100
     setGauge(gaugeValue);
     setIndicatorLoading("rsi", false);
} else {
     setGauge(0);
     setIndicatorLoading("rsi", true);
}

// =========================
// EMA GAUGE
// =========================
function setEmaGauge(price, ema20) {
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

     // Sync holding qty immediately from server-rendered dataset
     syncHoldingUI();

     fetch("/login/get-balance")
          .then(res => res.json())
          .then(data => {
               if (data.balance !== undefined) {
                    balanceEl.innerText = `Balance: ₹${data.balance.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
               }
               updateApproxReq(); // Run once balance is loaded
          });


     if (!STOCK_TOKEN) return;

     // Indicators are computed asynchronously on server; keep UI responsive.
     pollIndicatorsUntilReady();

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

// =========================
// INDICATOR INFO MODAL
// =========================
(function () {
     const INDICATOR_INFO = {
          rsi: {
               title: "RSI Information",
               body: `
                    <h4>What is RSI?</h4>
                    <p>The <strong>Relative Strength Index (RSI)</strong> is a momentum oscillator that measures the speed and magnitude of recent price changes on a scale of 0 to 100. It helps traders identify whether a stock is potentially overbought or oversold.</p>

                    <h4>How to Read RSI</h4>
                    <p><span class="signal-tag overbought">Overbought (70+)</span> &mdash; When RSI crosses above 70, the stock may be overvalued. This suggests buying pressure has pushed the price too high and a pullback or reversal could follow.</p>
                    <p><span class="signal-tag oversold">Oversold (30&minus;)</span> &mdash; When RSI drops below 30, the stock may be undervalued. This indicates heavy selling pressure and a potential bounce or recovery ahead.</p>
                    <p><span class="signal-tag strong">STRONG</span> &mdash; A "Strong" reading means RSI is between 55&ndash;65, indicating healthy upward momentum without being overbought. The stock has consistent buying interest and the trend is favourable.</p>

                    <h4>Key Takeaway</h4>
                    <p>RSI works best when combined with other indicators. A single overbought or oversold reading does not guarantee a reversal &mdash; always consider the broader market context.</p>
               `
          },
          ema20: {
               title: "EMA 20 Information",
               body: `
                    <h4>What is EMA 20?</h4>
                    <p>The <strong>Exponential Moving Average (EMA 20)</strong> is a trend-following indicator that calculates the average closing price of the last 20 periods, giving more weight to recent prices. This makes it more responsive to new price data compared to a simple moving average.</p>

                    <h4>Short-Term Trend Usage</h4>
                    <p>EMA 20 is widely used to gauge the <strong>short-term trend direction</strong>. When the current price is above EMA 20, the short-term trend is considered bullish. When below, it signals bearish momentum.</p>

                    <h4>How to Read Signals</h4>
                    <p><span class="signal-tag buy">BUY Signal</span> &mdash; A "Buy" signal appears when the stock price crosses above the EMA 20 line, suggesting the start of an upward trend. The further the price is above EMA 20, the stronger the bullish momentum.</p>
                    <p>Conversely, when price falls below EMA 20, it may indicate weakening momentum and a potential sell opportunity.</p>

                    <h4>Key Takeaway</h4>
                    <p>EMA 20 is most effective in trending markets. In sideways or choppy markets, it can generate frequent false signals. Combine it with other indicators like RSI for confirmation.</p>
               `
          },
          mtf: {
               title: "What is MTF (Margin Trading Facility)?",
               body: `
                    <h4>How MTF Works</h4>
                    <p>MTF allows you to buy stocks with <strong>leverage</strong>. With 4x MTF, you can purchase shares worth <strong>4 times</strong> your available capital.</p>
                    <ul class="modal-list">
                         <li>You pay only <strong>25%</strong> of the total order value upfront</li>
                         <li>The remaining <strong>75%</strong> is funded by the broker</li>
                         <li>Interest charges may apply on the borrowed amount</li>
                         <li>Higher risk due to amplified exposure</li>
                    </ul>

                    <h4>Example</h4>
                    <div class="example-box">
                         <p class="example-header">If you have <strong>&#8377;10,000</strong> capital</p>
                         <div class="example-row">
                              <span>You can buy shares worth</span>
                              <strong>&#8377;40,000</strong>
                         </div>
                         <div class="example-divider"></div>
                         <div class="example-row">
                              <span>You pay (25%)</span>
                              <strong>&#8377;10,000</strong>
                         </div>
                         <div class="example-row">
                              <span>Broker funds (75%)</span>
                              <strong>&#8377;30,000</strong>
                         </div>

                         <div class="example-divider"></div>
                         <p class="example-subheader up">If stock rises 10%</p>
                         <div class="example-row">
                              <span>Total value becomes</span>
                              <strong>&#8377;44,000</strong>
                         </div>
                         <div class="example-row">
                              <span>Profit</span>
                              <strong class="up">+&#8377;4,000</strong>
                         </div>
                         <div class="example-row">
                              <span>Your return on &#8377;10,000</span>
                              <strong class="up">+40%</strong>
                         </div>

                         <div class="example-divider"></div>
                         <p class="example-subheader down">If stock falls 10%</p>
                         <div class="example-row">
                              <span>Total value becomes</span>
                              <strong>&#8377;36,000</strong>
                         </div>
                         <div class="example-row">
                              <span>Loss</span>
                              <strong class="down">&minus;&#8377;4,000</strong>
                         </div>
                         <div class="example-row">
                              <span>Your loss on &#8377;10,000</span>
                              <strong class="down">&minus;40%</strong>
                         </div>
                    </div>

                    <div class="warning-badge">
                         <i class="bi bi-exclamation-triangle-fill"></i>
                         Leverage increases both profit and loss.
                    </div>
               `
          }
     };

     const overlay = document.getElementById("indicatorModal");
     const titleEl = document.getElementById("modalTitle");
     const bodyEl = document.getElementById("modalBody");
     const closeBtn = document.getElementById("modalCloseBtn");

     if (!overlay) return;

     function openModal(indicator) {
          const info = INDICATOR_INFO[indicator];
          if (!info) return;
          titleEl.textContent = info.title;
          bodyEl.innerHTML = info.body;
          overlay.classList.add("active");
          document.body.classList.add("indicator-modal-open");
     }

     function closeModal() {
          overlay.classList.remove("active");
          document.body.classList.remove("indicator-modal-open");
     }

     document.querySelectorAll(".info-btn[data-indicator]").forEach(function (btn) {
          btn.addEventListener("click", function () {
               openModal(this.dataset.indicator);
          });
     });

     closeBtn.addEventListener("click", closeModal);

     overlay.addEventListener("click", function (e) {
          if (e.target === overlay) closeModal();
     });

     document.addEventListener("keydown", function (e) {
          if (e.key === "Escape") closeModal();
     });
})();