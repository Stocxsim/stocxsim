

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