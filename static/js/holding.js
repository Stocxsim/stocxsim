// Select tab functionality
function selectTab(element) {
     const allTabs = document.querySelectorAll('.tab-item');
     allTabs.forEach(tab => {
          tab.classList.remove('active');
     });

     element.classList.add('active');
}

// Profile dropdown toggle
function toggleProfile() {
     document.getElementById("profileDropdown").classList.toggle("show");
}

// // Stock search functionality
// const stocks = [
//      "Reliance Industries",
//      "Reliance Power",
//      "Reliance Infra",
//      "TCS",
//      "Infosys",
//      "HDFC Bank",
//      "ICICI Bank",
//      "Axis Bank",
//      "SBIN"
// ];

const input = document.getElementById("searchInput");
const resultsBox = document.getElementById("searchResults");

input.addEventListener("input", async function () {
     const query = this.value.trim();
     resultsBox.innerHTML = "";

     if (!query) {
          resultsBox.style.display = "none";
          return;
     }

     try {
          const res = await fetch(`/stocks/search?q=${query}`);
          const stocks = await res.json();

          if (stocks.length === 0) {
               resultsBox.innerHTML =
                    `<div class="search-item disabled">No stocks found</div>`;
               resultsBox.style.display = "block";
               return;
          }

          stocks.forEach(stock => {
               const div = document.createElement("div");
               div.className = "search-item";
               div.textContent = `${stock.name}`;

               div.onclick = () => {
                    resultsBox.style.display = "none";
                    input.value = "";
                    window.location.href = `/stocks/${stock.token}`;
               };

               resultsBox.appendChild(div);
          });

          resultsBox.style.display = "block";

     } catch (err) {
          console.error("Search error:", err);
          resultsBox.style.display = "none";
     }
});