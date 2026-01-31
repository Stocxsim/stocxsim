document.addEventListener("DOMContentLoaded", () => {
     fetchOrders();
});

function fetchOrders() {
     fetch("/order/history", {
          method: "POST",
          headers: {
               "Content-Type": "application/json"
          },
          body: JSON.stringify({
               filter_params: {}
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
        <strong style="color:#44475b">${order.symbol}</strong><br>
        <small>
          ${order.transaction_type} · ${order.order_type} · ${order.product}
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
          <span class="order-arrow ${order.transaction_type === "BUY" ? "text-success" : "text-danger"
               }">
          &#8250;
          </span>
     </div>
    `;

          container.appendChild(item);
     });
}