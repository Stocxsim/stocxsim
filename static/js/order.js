document.addEventListener("DOMContentLoaded", () => {
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

          fetchOrders();
     });
}


function fetchOrders() {
     const filterParams = getFilterParams();
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
          });
}

function buildOrdersList(orders) {
     const container = document.querySelector(".orders-list");
     container.innerHTML = "";

     if (!orders || orders.length === 0) {
          container.innerHTML = `
      <div class="text-center text-muted mt-5">
        No orders found
      </div>
    `;
          return;
     }

     let lastDate = ""; // Track the date change

     orders.forEach(order => {

          // Insert date header if the date has changed
          if (order.date !== lastDate) {
               lastDate = order.date;
               const dateHeader = document.createElement("div");
               dateHeader.className = "mt-4 mb-2 fw-bold text-muted small border-bottom";
               dateHeader.innerHTML = lastDate;
               container.appendChild(dateHeader);
          }


          const item = document.createElement("div");
          item.className =
               "order-item d-flex justify-content-between align-items-center mb-3";

          item.innerHTML = `
      <div class="col order-info">
        <strong class="text-heading">${order.symbol}</strong><br>
        <small>
          ${order.transaction_type} · ${order.order_type} 
        </small>
      </div>

      <div class="col text-center">
        ${order.quantity}<br>
        <small>Qty</small>
      </div>

      <div class="col text-center">
        ₹${Number(order.price).toFixed(2)}<br>
        <small>price</small>
      </div>

      <div class="col text-center ms-1">
          ${order.time}
          <span class="order-arrow ${order.transaction_type === "BUY" ? "up" : "down"
               }">
          &#8250;
          </span>
     </div>
    `;

          container.appendChild(item);
     });
}
const fromDate = document.getElementById("fromDate");
const toDate = document.getElementById("toDate");

fromDate.addEventListener("change", function () {
     const selectedFromDate = this.value;

     // toDate ma minimum date set karo
     toDate.min = selectedFromDate;

     // jo already select karel toDate fromDate karta nani hoy to clear kari do
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

     return params;
}


// Search Filter functionality
const searchInput = document.getElementById('orderSearchInput');
const resultsBox = document.getElementById('orderSearchResults');
let debounceTimer;

searchInput.addEventListener("input", function () {
     const query = this.value.trim();

     // 1. Clear previous timer and results if input is short
     clearTimeout(debounceTimer);
     if (query.length == 0) {
          resultsBox.style.display = "none";
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
                    resultsBox.innerHTML = '<div class="p-3 text-center text-muted small">No matching orders found</div>';
               } else {
                    orders.forEach(order => {
                         const div = document.createElement("div");
                         div.className = "p-2 border-bottom order-item-hover";
                         div.style.cursor = "pointer";

                         // Map 'type' from your Python: row[1]
                         const typeClass = order.type === 'BUY' ? 'text-success' : 'text-danger';

                         div.innerHTML = `
                              <div class="d-flex justify-content-between align-items-start">
                                   <div>
                                        <div class="fw-bold mb-0">${order.symbol}</div>
                                        <div class="text-muted small" style="font-size: 0.7rem;">${order.full_name}</div> <div class="text-muted extra-small" style="font-size: 0.75rem;">Qty: ${order.qty} | Price: ₹${order.price}</div>
                                   </div>
                                   <div class="text-end">
                                        <div class="small ${typeClass} fw-bold">${order.type}</div>
                                        <div class="text-muted extra-small" style="font-size: 0.7rem;">${order.date}</div>
                                   </div>
                              </div>
                              `;
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