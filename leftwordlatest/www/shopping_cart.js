
$(document).ready(function() {
    if($('#cart-items-view').hasClass('empty-cart')){

        window.location.href = '/Checkout_cart_empty';        
    }

    $('.continue-shopping').on('click', function() {
        window.location.href = '/all_products';        

    });

    $('.checkout').on('click', function() {
        window.location.href = '/checkout';        

    });

    $('#checkout-link').click(function(e){
        e.preventDefault();
        window.location.href = $(this).attr('href');
    });
    
    $('.fa-trash').on('click', function() {
        var $button = $(this);
        if ($button.hasClass('disabled')) return;
        $button.addClass('disabled').prop('disabled', true);
    

        var itemCode = $(this).attr('data-item-code');
        var quotationName = $(this).attr('data-quotation-name');
        frappe.xcall('leftwordlatest.web_api.cart.delete_quotation', {
            "quotation_name": quotationName,
            "item_code": itemCode
        })
        .then(() => {
            $('#row-' + itemCode).remove();
            location.reload();

        })
        setTimeout(function() {
        $button.removeClass('disabled').prop('disabled', false);
    }, 1000);

    });

$('.plus-btn, .minus-btn').click(function() {
    var $button = $(this);
    if ($button.hasClass('disabled')) return;
    $button.addClass('disabled').prop('disabled', true);
    var itemCode = $(this).data('item-code'); 
    var countButton = $('#count-' + itemCode); 
    var qty = parseInt(countButton.text()); 
    const currency = sessionStorage.getItem('selectedCurrency') || 'INR';
    
    if ($(this).hasClass('plus-btn')) {
        qty++;
    } else {
        if (qty > 1) {
            qty--;
        }
    }

    countButton.text(qty);

    frappe.xcall('leftwordlatest.web_api.cart.make_cart', {
        "item_code": itemCode,
        "qty": qty,
        "currency": currency
    }).then(data=>{
        $('#cart-count').text(data[1])
        $('#total-amount').text(data[2])



    })
    setTimeout(function() {
        $button.removeClass('disabled').prop('disabled', false);
    }, 1000);

       
});

});
    













