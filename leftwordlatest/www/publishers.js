fetch("/api/method/leftwordlatest.web_api.publisher.get_brands")
  .then((response) => response.json())
  .then((response) => {
    const data = response.message || [];
    const grouped = {};

    data.forEach((item) => {
      const letter = item.brand.charAt(0).toUpperCase();
      if (!grouped[letter]) grouped[letter] = [];
      grouped[letter].push(item);
    });

    // Render the HTML
    let html = "";
    Object.keys(grouped)
      .sort()
      .forEach((letter) => {
        html += `
            <div class="publisher-column">
                        <h2>${letter}</h2>
                        <ul>`;
        grouped[letter].forEach((pub) => {
          html += `<a href="/publisher_details?brand=${encodeURIComponent(pub.brand)}" 
                  class="publisher-link"><li class="publisher-item">${pub.brand}</li></a>`;
        });
        html += `</ul>
                    <u class="underline">
                        <a href="/brows_publisher?letter=${letter}" class="browse-link">Browse all ${letter}</a>
                    </u>
                </div>`;
      });
    document.getElementById("publisher-section").innerHTML = html;
  });

// publisher list page.

(function () {
  const API = "/api/method/leftwordlatest.web_api.publisher.get_brands";
  const LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

  const stripEl = document.getElementById("alphabet-section");
  const listEl = document.getElementById("publisher-list");
  const loaderEl = document.getElementById("loader");
  const emptyEl = document.getElementById("empty");

  const urlParams = new URLSearchParams(window.location.search);
  const initialLetter = (urlParams.get("letter") || "A").toUpperCase();

  function renderStrip(activeLetter) {
    stripEl.innerHTML = LETTERS.map(
      (ltr) =>
        `<a href="?letter=${ltr}" data-letter="${ltr}" class="${
          ltr === activeLetter ? "active" : ""
        }">${ltr}</a>`
    ).join("");
  }

  async function loadAndRender(letter) {
    stripEl
      .querySelectorAll("a")
      .forEach((a) =>
        a.classList.toggle("active", a.dataset.letter === letter)
      );
    listEl.innerHTML = "";
    emptyEl.style.display = "none";
    loaderEl.style.display = "block";

    try {
      const res = await fetch(
        `${API}?start_letter=${encodeURIComponent(letter)}`
      );
      const json = await res.json();
      const data = json.message || [];

      if (!data.length) {
        emptyEl.style.display = "block";
        return;
      }

      let html = "";
      data.forEach((pub) => {
        html += `<li><a href="/publisher_details?brand=${encodeURIComponent(
          pub.brand
        )}" class="publisher-link">${pub.brand}</a></li>`;
      });

      listEl.innerHTML = html;
    } catch (e) {
      console.error(e);
      emptyEl.textContent = "Failed to fetch publisher data";
      emptyEl.style.display = "block";
    } finally {
      loaderEl.style.display = "none";
    }
  }

  stripEl.addEventListener("click", (e) => {
    const a = e.target.closest("a[data-letter]");
    if (!a) return;
    e.preventDefault();

    const letter = a.dataset.letter;
    const newUrl = `${location.pathname}?letter=${letter}`;
    window.history.pushState({ letter }, "", newUrl);

    loadAndRender(letter);
  });

  window.addEventListener("popstate", (e) => {
    const letter =
      (e.state && e.state.letter) ||
      new URLSearchParams(window.location.search).get("letter") ||
      "A";

    renderStrip(letter);
    loadAndRender(letter);
  });

  renderStrip(initialLetter);
  loadAndRender(initialLetter);
})();
