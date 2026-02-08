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
