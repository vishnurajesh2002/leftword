// $(document).ready(() => {
  // Fetch initial wishlist status for all items
  // $('.lw-wishlist').each(function () {
  //   const $wishlistButton = $(this);
  //   const itemCode = $wishlistButton.attr('data-item-code');

  //   if (itemCode && frappe.session.user != "Guest") {
  //     frappe.xcall('leftword.web_api.wishlist.get_wishlist', {}).then(data => {
  //       data.forEach(item => {
  //         if (item.item_code === itemCode) {
  //           $wishlistButton.addClass('in-wl');
  //         }
  //       });
  //       $('.lw-product-action').removeClass('hide-element');
  //     });
  //   } else {
  //     $('.lw-product-action').removeClass('hide-element');
  //   }
  // });

  // Click handler for wishlist button
  // $('.lw-wishlist').on('click', function (e) {
  //   e.preventDefault();
  //   const $clickedWishlist = $(this);
  //   const itemCode = $clickedWishlist.attr('data-item-code');

  //   if ($clickedWishlist.hasClass('in-wl')) {
  //     frappe.xcall('leftword.web_api.wishlist.remove_wishlist', {
  //       "item_code": itemCode
  //     }).then(() => {
  //       $clickedWishlist.removeClass('in-wl');
  //     });
  //   } else {
  //     frappe.xcall('leftword.web_api.wishlist.make_wishlist', {
  //       "item_code": itemCode
  //     }).then(() => {
  //       $clickedWishlist.addClass('in-wl');
  //     });
  //   }
  // });
// add to cart button
$(document).ready(function () {
  $('.product_list, .owl-carousel').on('click', '.add-to-cart-btn', function (e) {
    e.preventDefault();

    const $btn = $(this);

    if ($btn.hasClass('go-to-cart')) {
      window.location.href = '/shopping_cart';
      return;
    }

    if ($btn.data('in-progress')) return;

    const itemCode = $btn.data('item-code');
    const qty = $btn.data('qty') || 1;
    const currency = sessionStorage.getItem('selectedCurrency') || 'INR';

    if (!itemCode) {
      console.error('Missing item code');
      return;
    }

    $btn.data('in-progress', true).prop('disabled', true).text('Adding...');

    frappe.call({
      method: 'leftwordlatest.web_api.cart.make_cart',
      args: { item_code: itemCode, qty: qty, currency: currency },
      callback: function (response) {
        if (response.message) {
          const cartId = response.message[0];
          const totalQty = response.message[1];

          $('#cart-count').text(totalQty);

          $('#cart-button, #cart-button-usd')
            .text('Go to Cart')
            .removeClass('add-to-cart')
            .addClass('in-cart');

          $btn
            .text('Go to Cart')
            .addClass('go-to-cart')
            .prop('disabled', false)
            .data('in-progress', false);

          document.cookie = `cart_id=${cartId}`;

          showSuccessMessage('Item added to cart successfully!');
        }
      },
      error: function (err) {
        console.error('Cart error:', err);
        $btn.text('Add to Cart')
          .prop('disabled', false)
          .data('in-progress', false);
      }
    });
  });
});


  
function showSuccessMessage(message) {


  const messageDiv = $('<div class="success-message"></div>').text(message);


  $('body').append(messageDiv);

  messageDiv.css({

      'position': 'fixed',

      'top': '20px',

      'right': '20px',

      'background-color': '#28a745',

      'color': '#fff',

      'padding': '10px 20px',

      'border-radius': '5px',

      'z-index': '1000'

  });

  setTimeout(() => {

      messageDiv.fadeOut(300, () => {

          messageDiv.remove();

      });

  }, 3000);

}
  //add to Cart button click handler
  $('#cart-button-usd').on('click', (e) => {
    if ($('#cart-button-usd').hasClass('add-to-cart')) {
      if (!$('#cart-button-usd').hasClass('allow-guest-cart') && frappe.session.user == "Guest") {
        window.location.href = '/leftword_login';
        return;
      }
      const item_code = $('#cart-button-usd').data('item-code');
      const count = parseInt($('#item-count').text().trim());
      const cartCurrency = sessionStorage.getItem('selectedCurrency') || 'INR';
      $('#cart-button-usd').text("Adding To Cart...");
      frappe.call({
        method: 'leftwordlatest.web_api.cart.make_cart',
        args: {
          item_code: item_code,
          qty: count,
          currency: cartCurrency
        },
        callback(r) {
          $('#cart-count').text(r.message[1]);
          if (r.message) {
            document.cookie = `cart_id=${r.message[0]}`;
            showSuccessMessage('Item added to cart successfully!');
          }
          $('#cart-button-usd').prop('disabled', false);
          $('#cart-button-usd').text("Go to Cart");
        }
      });
      $('#cart-button-usd').removeClass('add-to-cart');
      $('#cart-button-usd').addClass('in-cart');
    } else if ($('#cart-button-usd').hasClass('in-cart')) {
      window.location.href = '/shopping_cart';
    }
  });
  $('#cart-button').on('click', (e) => {
    if ($('#cart-button').hasClass('add-to-cart')) {
      if (!$('#cart-button').hasClass('allow-guest-cart') && frappe.session.user == "Guest") {
        window.location.href = '/leftword_login';
        return;
      }
      const item_code = $('#cart-button').data('item-code');
      const count = parseInt($('#item-count').text().trim());
      const cartCurrencyTwo = sessionStorage.getItem('selectedCurrency') || 'INR';
      $('#cart-button').text("Adding To Cart...");
      frappe.call({
        method: 'leftwordlatest.web_api.cart.make_cart',
        args: {
          item_code: item_code,
          qty: count,
          currency: cartCurrencyTwo
        },
        callback(r) {
          $('#cart-count').text(r.message[1]);
          if (r.message) {
            document.cookie = `cart_id=${r.message[0]}`;
            showSuccessMessage('Item added to cart successfully!');
          }
          $('#cart-button').prop('disabled', false);
          $('#cart-button').text("Go to Cart");
        }
      });
      $('#cart-button').removeClass('add-to-cart');
      $('#cart-button').addClass('in-cart');
    } else if ($('#cart-button').hasClass('in-cart')) {
      window.location.href = '/shopping_cart';
    }
  });
  


  
// increment count
  $(document).ready(function() {
    let count = parseInt($('#item-count').text()) || 1;

$(document).on('click', '#btn-add', function(e) {
  
  let stockValue = $('.stock-data').attr('data-stock-value');
  
  if (stockValue) {
    if (parseInt(stockValue) > parseInt($('#item-count').text())) {
      let currentCount = parseInt($('#item-count').text());
      $('#item-count').text(currentCount + 1);
    }
  } else {
  }
});
});

// Decrement item count
$(document).ready(function() {
let count = parseInt($('#item-count').text()) || 1;

$(document).on('click', '#btn-min', function(e) {
  
  let stockValue = $('.stock-data').attr('data-stock-value');
  
  if (stockValue) {
    let currentCount = parseInt($('#item-count').text());
    if (currentCount > 1) {
      $('#item-count').text(currentCount - 1);
    } else {
    }
  } else {
  }
});
});


// url active button
$(document).ready(function() {
  const currentUrl = new URL(window.location.href);
  const variantFromUrl = currentUrl.searchParams.get('id'); 

  if (variantFromUrl) {
      $('.variant-button').each(function() {
          const buttonVariant = $(this).data('variant');
          
          if (buttonVariant === variantFromUrl) {
              $(this).addClass('active');
          } else {
              $(this).removeClass('active');
          }
      });
  }
  
  // variant button click
  $('.variant-button').on('click', function (e) {
      e.preventDefault();

      const variant = $(this).data('variant');
      currentUrl.searchParams.set('id', variant);
      history.pushState({}, '', currentUrl.toString());
      
      $('.variant-details').html('<div class="loading-spinner"></div>');
      $('.lw-productDetailsPrice').html('<div class="loading-spinner"></div>');

      // Refresh the page
    location.reload();

      frappe.xcall('leftwordlatest.web_api.items.item_query', { filters: { "item_code": variant } })
          .then(data => {

              let itemVariant = data[0];

              if (!itemVariant) {
                  $('.variant-details').html('');
                  $('.lw-productDetailsPrice').html('');
                  return;
              }

              let displayTitle = '';
              if (itemVariant.template_custom_title) {
                  displayTitle = itemVariant.template_custom_title;
              } else if (itemVariant.custom_title || itemVariant.custom_variant_name) {
                  displayTitle = itemVariant.custom_title || itemVariant.custom_variant_name;
              } else if (itemVariant.web_item_name) {
                  displayTitle = itemVariant.web_item_name;
              } else {
                  displayTitle = itemVariant.template_web_item_name;
              }

              $('h3').text(displayTitle);

              $('.variant-details')
                  .fadeOut(200, function () { 
                      $(this).html(`
                          <div class="lw-productDetailscatagItem">
                              <p>${itemVariant.custom_isbn || ''}</p>
                              <p>${itemVariant.brand || ''} ${itemVariant.custom_year || ''}</p>
                              <p>${itemVariant.custom_language ? 'Language ' + itemVariant.custom_language : ''}</p>
                              <p>${itemVariant.custom_no_of_pages ? itemVariant.custom_no_of_pages + ' Pages' : ''}</p>
                              <p>${itemVariant.custom_book_size ? itemVariant.custom_book_size + ' Inches' : ''}</p>
                          </div>
                      `);
                  }).fadeIn(200); 
              let hideInr = '';
              let hideUsd = '';
              if ($('.transaction-currency')[0].value === "INR") {
                  hideUsd = "display:none;";
              } else {
                  hideInr = "display:none;";
              }

              $('.lw-productDetailsPrice')
                  .fadeOut(200, function () { 
                      $(this).html(`
                          <div class="section left">
                              <p style="font-size: 15px;">Price
                                  <span class="item-price currency_inr" style="${hideInr}">INR ${itemVariant.price_list_rate_inr || ''}</span>
                                  <span class="item-price currency_usd" style="${hideUsd}">USD ${itemVariant.price_list_rate_usd || ''}</span>
                              </p>
                          </div>
                          <div class="section middle">
                              ${itemVariant.discount_amount_inr ? `
                              <p style="font-size: 13px;">Book Club Price
                                  <span class="item-price currency_inr" style="${hideInr}">INR ${itemVariant.discount_percentage_inr || ''}</span>
                                  <span class="item-price currency_usd" style="${hideUsd}">USD ${itemVariant.discount_percentage_usd || ''}</span>
                              </p>
                              ` : ''}
                          </div>
                          <div class="section right">
                              <p style="font-size: 14px;">
                                  <a href="/club_membership_plan" class="joinClub">Join Book Club</a>
                              </p>
                          </div>
                      `);
                  }).fadeIn(200); 
              $('#cart-button ,#cart-button-usd').data('item-code', variant);
          })
          .catch(error => {
              console.error("Error in API call:", error);
              $('.variant-details').html('<p>Error loading variant details. Please try again later.</p>');
              $('.lw-productDetailsPrice').html('');
          });
  });
});



// buy now
$(document).on('click', '.btn-primary.checkout', function (e) {
  e.preventDefault();

  const itemCode = $(this).data('item-code');
  const qty = parseInt($('#item-count').text().trim()); 
  const cartCurrencyThree = sessionStorage.getItem('selectedCurrency') || 'INR';

  if (!itemCode) {
    console.error('#');
    return;
  }

  if (!qty || qty < 1) {
    return;
  }

  frappe.call({
    method: 'leftwordlatest.web_api.cart.make_cart',
    args: {
      item_code: itemCode,
      qty: qty,
      currency: cartCurrencyThree
    },
    callback: function (response) {
      if (response.message) {
        const cartId = response.message[0];
        document.cookie = `cart_id=${cartId}`;

        
        window.location.href = '/checkout';
      } 
    },
    error: function (err) {
      console.error('#', err);
    },
  });
});

// slide show image clicking
document.addEventListener('DOMContentLoaded', function () {
  const thumbnails = document.querySelectorAll('.thumbnail-image');
  const mainImage = document.querySelector('.main-image');

  thumbnails.forEach(thumbnail => {
      thumbnail.addEventListener('click', function (event) {
          event.preventDefault(); 
          const newSrc = this.getAttribute('data-src'); 
          mainImage.setAttribute('src', newSrc); 
      });
  });
});
// document.addEventListener("DOMContentLoaded", function () {
//   const carousel = document.querySelector(".lw-details-carousel");
//   const images = carousel.querySelectorAll("img");
//   let loadedCount = 0;

//   images.forEach((img) => {
//       if (img.complete) {
//           loadedCount++;
//           if (loadedCount === images.length) {
//               carousel.classList.add("loaded");
//           }
//       } else {
//           img.addEventListener("load", () => {
//               loadedCount++;
//               if (loadedCount === images.length) {
//                   carousel.classList.add("loaded");
//               }
//           });
//       }
//   });
// });


function setMainImage(thumbnail) {
  const mainImage = document.getElementById("mainPreviewImage");
  mainImage.src = thumbnail.src;
}


// countdown of discount price.

function getEndOfDay(validDays) {
  const now = new Date();
  return new Date(
      now.getFullYear(),
      now.getMonth(),
      now.getDate() + (validDays - 1),
      23, 59, 59
  );
}

function startCountdownToEndOfDay(elementId, validDays) {
  const countdownEl = document.getElementById(elementId);
  const deadline = getEndOfDay(validDays);

  function updateCountdown() {
      const now = new Date();
      const diff = deadline - now;

      if (diff <= 0) {
          countdownEl.innerHTML = "Expired";
          return;
      }

      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);

      let output = "";
      if (days > 0) output += `${days}d `;
      output += `${hours}h ${minutes}m ${seconds}s`;

      countdownEl.innerHTML = output;
  }

  updateCountdown();
  setInterval(updateCountdown, 1000);
}

document.addEventListener("DOMContentLoaded", function () {
  const timers = [
      { elId: "discount-timer-inr", countdownId: "countdown-inr" },
      { elId: "discount-timer-usd", countdownId: "countdown-usd" },
      { elId: "bc-discount-timer-inr", countdownId: "bc-countdown-inr" },
      { elId: "bc-discount-timer-usd", countdownId: "bc-countdown-usd" }
  ];

  timers.forEach(({ elId, countdownId }) => {
      const el = document.getElementById(elId);
      if (el) {
          const validDays = parseInt(el.getAttribute("data-valid-days"));
          if (validDays > 0) {
              startCountdownToEndOfDay(countdownId, validDays);
          }
      }
  });
});