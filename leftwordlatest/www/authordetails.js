$(document).ready(function() {
    
    $('.row').on('click', '.add-to-cart-btn', function(e) {
        e.preventDefault(); 
        $(this).prop('disabled', true);
        
        const itemCode = $(this).data('item-code'); 
        const qty = $(this).data('qty');

        const currency = sessionStorage.getItem('selectedCurrency') || 'INR';
        
        frappe.call({
            method: 'leftwordlatest.web_api.cart.make_cart',
            args: {
                item_code: itemCode,
                qty: qty,
                currency: currency
            },
            callback: function(response) {
                if (response.message) {
                    const totalQty = response.message[1]; 
                    $('#cart-count').text(totalQty); 

                    
                    $(`.add-to-cart-btn[data-item-code="${itemCode}"]`)
                        .text("In Cart")
                        .removeClass('add-to-cart-btn') 
                        .addClass('in-cart');
                    
                   
                    document.cookie = `cart_id=${response.message[0]}`;
                } 
            },
            error: function(err) {
                console.error('Error adding to cart:', err);
            }
        });
    });
});
