const ITEMS_PER_PAGE = 20;

async function loadPublisherBooks(page = 1) {
  const brand = new URLSearchParams(window.location.search).get("brand");
  document.querySelector("h5").innerText = `Books by ${brand}`;

  const start = (page - 1) * ITEMS_PER_PAGE;

  const currencySelect = document.querySelector(".transaction-currency");
  const selectedCurrency = currencySelect?.value || "All";

  try {
    const res = await fetch(
      `/api/method/leftwordlatest.web_api.publisher.get_brand_variants_only?brand_name=${encodeURIComponent(
        brand
      )}&start=${start}&limit=${ITEMS_PER_PAGE}`
    );

    const json = await res.json();
    const books = json.message.items || [];
    const totalCount = json.message.total_count || 0;

    if (!books.length) {
      document.getElementById("empty").style.display = "block";
      return;
    }

    document.getElementById("empty").style.display = "none";

    const container = document.getElementById("publisher-books");
    let html = "";

    const currentUser = "{{ frappe.session.user }}";

    books.forEach((book) => {
      const inrPrice =
        book.price_list_rate_inr > 0
          ? `<div class="price-amount currency_inr"><span>INR</span> ${book.price_list_rate_inr}</div>`
          : `<div class="price-amount currency_inr"><span style="color: red;">Not Available In INR</span></div>`;

      const usdPrice =
        book.price_list_rate_usd > 0
          ? `<div class="price-amount currency_usd"><span>USD</span> ${book.price_list_rate_usd}</div>`
          : `<div class="price-amount currency_usd"><span style="color: red;">Not Available In USD</span></div>`;

      let priceHtml = "";
      if (selectedCurrency === "All") {
        priceHtml = `${inrPrice}${usdPrice}`;
      } else if (selectedCurrency === "INR") {
        priceHtml = inrPrice;
      } else if (selectedCurrency === "USD") {
        priceHtml = usdPrice;
      }

      html += `
        <div class="col mb-4">
          <div class="itembooks card card-item">
            <a href="/productdetailspage?id=${
              book.item_code
            }" class="card-item-img">
              <img src="${
                book.item_image ||
                book.custom_website_image ||
                book.website_image ||
                "/src/img/blankImg.png"
              }">
            </a>
            <div class="card-content">
              <div class="itemDetails">
                <a href="/productdetailspage?id=${book.item_code}">
                  <h6 class="text-limit2">${book.item_name}</h6>
                </a>
                <p>${book.custom_publisher || ""}</p>
              </div>
              <div class="cart-hover-sec">
                <div class="price-amount">
                ${priceHtml}
                </div>
                <div class="add-cart-btn">
                  ${
                    currentUser === "Guest"
                      ? `<a href="#" class="btn-primary btn-style btn-icon-left" data-bs-toggle="modal" data-bs-target="#lwsignIn">ADD TO CART</a>`
                      : `<a href="#" class="btn-primary btn-style btn-icon-left add-to-cart-btn" data-item-code="${book.item_code}" data-qty="1">ADD TO CART</a>`
                  }
                </div>
              </div>
            </div>
          </div>
        </div>`;
    });

    container.innerHTML = html;

    renderPagination(totalCount, page);
  } catch (err) {
    console.error(err);
    document.getElementById("empty").innerText = "Failed to load books.";
    document.getElementById("empty").style.display = "block";
  }
}

function renderPagination(totalCount, currentPage) {
  const totalPages = Math.ceil(totalCount / ITEMS_PER_PAGE);
  const paginationUl = document.getElementById("pagination-ul");
  paginationUl.innerHTML = "";

  if (totalPages <= 1) return;

  // Previous
  paginationUl.innerHTML += `
    <li class="page-item ${currentPage === 1 ? "disabled" : ""}">
      <a class="page-link" href="#" aria-label="Previous" data-page="${currentPage - 1}">
        <span aria-hidden="true">«</span>
      </a>
    </li>`;

  // Page numbers
  for (let i = 1; i <= totalPages; i++) {
    paginationUl.innerHTML += `
      <li class="page-item paginate ${
        i === currentPage ? "active current-page" : ""
      }">
        <a class="page-link" href="#" data-page="${i}">${i}</a>
      </li>`;
  }

  // Next
  paginationUl.innerHTML += `
    <li class="page-item ${currentPage === totalPages ? "disabled" : ""}">
      <a class="page-link next-forward" href="#" aria-label="Next" data-page="${
        currentPage + 1
      }">
        <span aria-hidden="true">»</span>
      </a>
    </li>`;

  // Attach click event
  document.querySelectorAll("#pagination-ul a").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const page = parseInt(e.currentTarget.getAttribute("data-page"));
      if (!isNaN(page) && page >= 1 && page <= totalPages) {
        loadPublisherBooks(page);
      }
    });
  });
}

loadPublisherBooks(1); // initial load

document.querySelectorAll(".transaction-currency").forEach((select) => {
  select.addEventListener("change", () => {
    loadPublisherBooks(1);
  });
});

$(document).ready(function () {
  $("#publisher-books").on("click", ".add-to-cart-btn", function (e) {
    e.preventDefault();
    const btn = $(this);
    btn.prop("disabled", true);

    const itemCode = btn.data("item-code");
    const qty = btn.data("qty");
    const currency = sessionStorage.getItem('selectedCurrency') || 'INR';
    frappe.call({
      method: "leftwordlatest.web_api.cart.make_cart",
      args: {
        item_code: itemCode,
        qty: qty,
        currency: currency
      },
      callback: function (response) {
        if (response.message) {
          const totalQty = response.message[1];
          $("#cart-count").text(totalQty);

          btn
            .text("In Cart")
            .removeClass("add-to-cart-btn")
            .addClass("in-cart");
          document.cookie = `cart_id=${response.message[0]}`;
        }
      },
      error: function (err) {
        console.error("Error adding to cart:", err);
      },
    });
  });
});
