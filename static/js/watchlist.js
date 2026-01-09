fetch("/stocks/watchlist")
  .then(res => res.json())
  .then(stocks => {
    const tbody = document.getElementById("watchlistBody");
    tbody.innerHTML = "";

    stocks.forEach(stock => {
      const isUp = stock.change >= 0;

      const row = document.createElement("tr");
      row.id = "token-" + stock.token;
      row.style.cursor = "pointer";

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
            <div class="logo">${stock.name ? stock.name[0].toUpperCase() : "?"}</div>
            <div>
              <div class="company-name">${stock.name}</div>
            </div>
          </div>
        </td>

        <td>
          <span class="trend ${isUp ? "up" : "down"}">
                ${isUp ? "↗" : "↘"}
          </span>
        </td>

        <td class="text-end">
          ${typeof stock.price === "number"
          ? "₹" + stock.price.toFixed(2)
          : "--"}
        </td>

        <td class="text-end ${isUp ? "text-success" : "text-danger"}">
          ${typeof stock.change === "number"
          ? `${isUp ? "+" : ""}${stock.change} (${stock.change_pct}%)`
          : "--"}
        </td>

        <td class="text-end">--</td>
        <td class="text-end perf">L ───●── H</td>
      `;

      tbody.appendChild(row);
    });
  });
