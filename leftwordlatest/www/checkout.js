$(document).ready(function() {

    if ($('#place-order').hasClass('order-placed')) { 
        $('#place-order').text("Placing Order....");
        $('.btn-group.item-count').remove();
    }
    // if ($('#place-order').hasClass('empty-cart')) { 
    //     console.log("loading");
    //     $('.empty-cart').prop('disabled', true);
    // }else{
    //     $('#place-order').prop('disabled', false);

    // }

    
    
    // $('#checkbox1').change(function() {
    //     if(this.checked) {
    //         $('#billing-address').removeClass('hide-element');
    //         $('#checkbox1').addClass('billing-address');

    //    }
            
    // }); 

    $("#place-order").click(function() {
        if ($(this).prop("disabled")) return;
        $('#place-order').text("Placing Order...").prop("disabled", true);
    
      
        var shippingAddress = $("input[type='checkbox'][data-address-type='shipping']:checked").val();
        var billingAddress = $("input[type='checkbox'][data-address-type='billing']:checked").val();

        if (!shippingAddress || !billingAddress) {
            alert("Please add both shipping and billing addresses.");
            $('#place-order').text("Place Order");
            return;
        }

        frappe.call({
            method: 'leftwordlatest.web_api.checkout.create_order',
            args: {
                shipping_address: shippingAddress,
                billing_address: billingAddress
            },
            callback: function(r) {
                var orderId = r.order;
    
                if (orderId) {
                    $('#place-order').removeClass('cart-items').addClass('order-placed').text("Placing Order....");
                    $(".order-placed").attr('id', 'checkout');
                    $('.btn-group.item-count').remove();
    
                    frappe.xcall('leftwordlatest.web_api.checkout.create_invoice', { order_id: orderId })
                        .then(function(response) {
       
                            if (response && response.order) {
                                var invoiceId = response.order;
                        
                                $('#checkout').removeClass('order-placed').text("Place Order");
                                window.location.href = '/start_payment?order=' + invoiceId;
                            } else {
                                console.error("Sales Invoice ID not received.");
                            }
                        })
                        .catch(function(error) {
                            console.error("Error creating invoice:", error);
                        });
    
                    $(".checkout").attr('id', 'place-order');
                } else {
                    console.error("Order ID not received.");
                    $('#place-order').text("Place Order");
                }
            }
        });
    });
    
    $('.btn-group.item-count').on('click', '.plus-btn, .minus-btn', function() {
        var $button = $(this);
        if ($button.hasClass('disabled')) return;
        $button.addClass('disabled').prop('disabled', true);
        var itemCode = $button.closest('.btn-group.item-count').find('#item-count').data('item-code');
        var countButton = $button.closest('.btn-group.item-count').find('#item-count');
        var qty = parseInt(countButton.text());

        if ($button.hasClass('plus-btn')) {
            qty++;
        } else {
            if (qty > 1) {
                qty--;
            }
        }

        countButton.text(qty);

        const currency = sessionStorage.getItem('selectedCurrency') || 'INR';
        frappe.xcall('leftwordlatest.web_api.cart.make_cart', {
            "item_code": itemCode,
            "qty": qty,
            "currency": currency
        }).then(data => {
        
            $('#cart-count').text(data[1]);
            $('#total-amount').text(data[2]);
   
        });

        setTimeout(function() {
            $button.removeClass('disabled').prop('disabled', false);
        }, 1000);
    });
});

