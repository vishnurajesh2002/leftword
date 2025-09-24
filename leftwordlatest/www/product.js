frappe.ready(() => {
  if($('.lw-wishlist').attr('data-item-code') && frappe.session.user != "Guest"){
    frappe.xcall('leftwordlatest.web_api.wishlist.get_wishlist', {
      "item_code": $('.lw-wishlist').attr('data-item-code')
    }).then(data=>{
      if(data.length){
        $('.lw-wishlist').addClass('in-wl')
      }
      $('.lw-product-action').removeClass('hide-element')
    })
  }else{
    $('.lw-product-action').removeClass('hide-element')
  }
  $('#btn-add').on('click', function(e){
    if(parseInt($('.stock-data')[0].attributes.getNamedItem("data-stock-value").value) > parseInt($('#item-count')[0].firstChild.data)){
      $('#item-count')[0].firstChild.data = parseInt($('#item-count')[0].firstChild.data) + 1
    }
  })
  $('#btn-min').on('click', function(e){
    if(parseInt($('#item-count')[0].firstChild.data) > 1){
      $('#item-count')[0].firstChild.data = parseInt($('#item-count')[0].firstChild.data) - 1
    }
  })

  $('.lw-wishlist').on('click', function(e){
    e.preventDefault()
    if(e.target.classList.contains("in-wl")){
      $('.lw-wishlist').removeClass('in-wl')
      frappe.xcall('leftwordlatest.web_api.wishlist.remove_wishlist', {
        "item_code":$('.lw-wishlist').attr('data-item-code')
      })
    }else{
      $('.lw-wishlist').addClass('in-wl')
      frappe.xcall('leftwordlatest.web_api.wishlist.make_wishlist', {
        "item_code":$('.lw-wishlist').attr('data-item-code')
      })
    }
  });

  
  $('#cart-button').on('click', (e) => {
    if ($('#cart-button').hasClass('add-to-cart')) {   
      if(!$('#cart-button').hasClass('allow-guest-cart') &&  frappe.session.user == "Guest") {
        window.location.href = '/leftword_login';
        return;
      }     
        const item_code = $('#cart-button').data('item-code');
        const count = parseInt($('#item-count').text().trim());
        const currency = sessionStorage.getItem('selectedCurrency') || 'INR'; // Get the selected currency
        $('#cart-button').text("Adding To Cart...");
        frappe.call({
            method: 'leftwordlatest.web_api.cart.make_cart',
            args: {
                item_code: item_code,
                qty: count,
                currency: currency
            },
            callback(r){
              $('#cart-count').text(r.message[1])
              if(r.message){
                document.cookie = `cart_id=${r.message[0]}`
                // document.cookie = r.message[0]
              

              }
              $('#cart-button').prop('disabled', false);
              $('#cart-button').text("Go to Cart");
            }
        })
        $('#cart-button').removeClass('add-to-cart');
        $('#cart-button').addClass('in-cart');
        
    }
    else if($('#cart-button').hasClass('in-cart')){
      window.location.href = '/shopping_cart';

    }
  

  });


// new cart function
 





 
});
