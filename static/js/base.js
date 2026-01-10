document.addEventListener("DOMContentLoaded", () => {

  // Tabs
  window.selectTab = function (element) {
    document.querySelectorAll('.tab-item')
      .forEach(tab => tab.classList.remove('active'));
    element.classList.add('active');
  };

  // Profile dropdown
  window.toggleProfile = function () {
    const dropdown = document.getElementById("profileDropdown");
    if (dropdown) dropdown.classList.toggle("show");
  };

  // Search
  const input = document.getElementById("searchInput");
  const resultsBox = document.getElementById("searchResults");

  if (!input || !resultsBox) return;

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

      if (!stocks.length) {
        resultsBox.innerHTML =
          `<div class="search-item disabled">No stocks found</div>`;
        resultsBox.style.display = "block";
        return;
      }

      stocks.forEach(stock => {
        const div = document.createElement("div");
        div.className = "search-item";
        div.textContent = stock.name;
        div.onclick = () =>
          window.location.href = `/stocks/${stock.token}`;
        resultsBox.appendChild(div);
      });

      resultsBox.style.display = "block";
    } catch (e) {
      console.error(e);
    }
  });
});