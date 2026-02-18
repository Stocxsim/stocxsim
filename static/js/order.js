document.addEventListener("DOMContentLoaded", () => {
     setOrdersLoading(true);
     fetchOrders();
});

document.querySelectorAll('.filters input').forEach(el => {
     el.addEventListener("change", () => {
          fetchOrders();
     });
});

const clearFiltersBtn = document.getElementById("clearFilters");
if (clearFiltersBtn) {
     clearFiltersBtn.addEventListener("click", (e) => {
          e.preventDefault();

          document.querySelectorAll('.filters input').forEach(el => {
               if (el.type === "checkbox") el.checked = false;
               else el.value = "";
          });

          if (searchInput) {
               delete searchInput.dataset.symbolToken;
               delete searchInput.dataset.symbol;
          }

          if (resultsBox) {
               resultsBox.style.display = "none";
               resultsBox.innerHTML = "";
          }

          fetchOrders();
     });
}


function setOrdersLoading(isLoading, message = "Loading orders…") {
     const container = document.getElementById("orders-body");
     if (!container) return;
     if (isLoading) {
          container.innerHTML = `<div class="orders-loading">
               <div class="loading-spinner"></div>
               <span>${message}</span>
          </div>`;
     }
}

function fetchOrders() {
     const filterParams = getFilterParams();
     setOrdersLoading(true);
     fetch("/order/history", {
          method: "POST",
          headers: {
               "Content-Type": "application/json"
          },
          body: JSON.stringify({
               filter_params: filterParams
          })
     })
          .then(res => res.json())
          .then(data => {
               buildOrdersList(data.orders);
          })
          .catch(err => {
               console.error("Orders fetch failed:", err);
               setOrdersLoading(false, "Unable to load orders");
          });
}

function buildOrdersList(orders) {
     const container = document.getElementById("orders-body");
     container.innerHTML = "";

     // Update count badge
     const countBadge = document.getElementById("orders-count");
     if (countBadge) countBadge.textContent = orders ? orders.length : 0;

     if (!orders || orders.length === 0) {
          container.innerHTML = `
               <div class="orders-empty">
                    <div class="empty-icon"><i class="bi bi-receipt"></i></div>
                    <div class="empty-title">No orders found</div>
                    <div class="empty-subtitle">Your executed orders will appear here. Try adjusting your filters or place a new order!</div>
               </div>`;
          return;
     }

     let lastDate = "";
     let cardIndex = 0;

     orders.forEach(order => {
          // Date separator
          if (order.date !== lastDate) {
               lastDate = order.date;
               const sep = document.createElement("div");
               sep.className = "order-date-separator";
               sep.innerHTML = `<span>${lastDate}</span>`;
               container.appendChild(sep);
          }

          const isBuy = order.transaction_type.toUpperCase() === "BUY";
          const accentClass = isBuy ? "accent-buy" : "accent-sell";
          const typeClass = isBuy ? "buy" : "sell";
          const initial = order.symbol ? order.symbol.charAt(0).toUpperCase() : "?";

          const card = document.createElement("div");
          card.className = `order-card ${accentClass}`;
          card.style.animationDelay = `${Math.min(cardIndex * 0.03, 0.3)}s`;
          cardIndex++;

          card.innerHTML = `
               <div class="order-stock-info">
                    <div class="order-avatar ${typeClass}">${initial}</div>
                    <div class="order-stock-details">
                         <div class="order-stock-name">${order.symbol}</div>
                         <div class="order-stock-meta">
                              <span class="order-type-badge ${typeClass}">
                                   <i class="bi ${isBuy ? 'bi-arrow-up-right' : 'bi-arrow-down-left'}"></i>
                                   ${order.transaction_type}
                              </span>
                              · ${order.order_type}
                         </div>
                    </div>
               </div>
               <div class="order-data-cell">
                    <div class="order-data-value">${order.quantity}</div>
                    <div class="order-data-label">Qty</div>
               </div>
               <div class="order-data-cell">
                    <div class="order-data-value">₹${Number(order.price).toFixed(2)}</div>
                    <div class="order-data-label">Price</div>
               </div>
               <div class="order-time-cell">
                    ${order.time}
               </div>
          `;

          container.appendChild(card);
     });
}

const fromDate = document.getElementById("fromDate");
const toDate = document.getElementById("toDate");

fromDate.addEventListener("change", function () {
     const selectedFromDate = this.value;

     toDate.min = selectedFromDate;
     if (toDate.value && toDate.value < selectedFromDate) {
          toDate.value = "";
     }
});

function getFilterParams() {
     const params = {};

     const dates = document.querySelectorAll('input[type="date"]');

     if (dates[0].value) {
          params.from_date = dates[0].value;
     }

     if (dates[1].value) {
          params.to_date = dates[1].value;
     }

     const transaction_type = [];
     if (document.getElementById("buyOrders").checked) transaction_type.push("buy");
     if (document.getElementById("sellOrders").checked) transaction_type.push("sell");

     if (transaction_type.length > 0) {
          params.transaction_type = transaction_type;
     }

     if (searchInput && searchInput.dataset && searchInput.dataset.symbolToken) {
          params.symbol_token = searchInput.dataset.symbolToken;
     }

     return params;
}


// Search Filter functionality
const searchInput = document.getElementById('orderSearchInput');
const resultsBox = document.getElementById('orderSearchResults');
let debounceTimer;

if (searchInput && resultsBox) {
searchInput.addEventListener("input", function () {
     const query = this.value.trim();

     // If user edits text after selection, drop the selected token
     if (this.dataset && this.dataset.symbolToken) {
          delete this.dataset.symbolToken;
          delete this.dataset.symbol;
     }

     // 1. Clear previous timer and results if input is short
     clearTimeout(debounceTimer);
     if (query.length == 0) {
          resultsBox.style.display = "none";
          resultsBox.innerHTML = "";
          return;
     }

     // 2. Wait 300ms after last keystroke to fetch
     debounceTimer = setTimeout(async function () {
          try {
               // Using singular /order as per your requirement
               const res = await fetch(`/order/search?q=${query}`);
               if (!res.ok) return;

               const orders = await res.json();
               resultsBox.innerHTML = "";

               if (orders.length === 0) {
                    resultsBox.innerHTML = '<div class="p-3 text-center text-muted small">No matching stocks found</div>';
               } else {
                    orders.forEach(order => {
                         const div = document.createElement("div");
                         div.className = "order-search-result-item";

                         // Map 'type' from your Python: row[1]
                         const typeClass = order.type === 'BUY' ? 'text-success' : 'text-danger';

                         const displayName = order.name || "";
                         const token = order.symbol_token;
                         const shortName = order.symbol;

                         div.innerHTML = `
                              <div class="d-flex justify-content-between align-items-start">
                                   <div>
                                        <div class="fw-bold mb-0">${shortName}</div>
                                        <div class="text-muted small" style="font-size: 0.75rem;">${displayName}</div>
                                   </div>
                                   <div class="text-end">
                                        <div class="small ${typeClass} fw-bold">${order.type}</div>
                                        <div class="text-muted extra-small" style="font-size: 0.75rem;">${order.date || ""}</div>
                                   </div>
                              </div>
                         `;

                         div.addEventListener("click", () => {
                              if (token) {
                                   searchInput.dataset.symbolToken = token;
                                   searchInput.dataset.symbol = shortName;
                              }

                              // Keep input readable but simple
                              searchInput.value = shortName;
                              resultsBox.style.display = "none";
                              resultsBox.innerHTML = "";
                              fetchOrders();
                         });
                         resultsBox.appendChild(div);
                    });
               }
               resultsBox.style.display = "block";
          } catch (e) {
               console.error("Order search failed", e);
          }
     }, 300);
});

// Close dropdown when clicking outside
document.addEventListener("click", (e) => {
     if (!searchInput.contains(e.target) && !resultsBox.contains(e.target)) {
          resultsBox.style.display = "none";
     }
});
}