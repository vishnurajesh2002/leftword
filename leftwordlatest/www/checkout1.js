$(document).ready(function() {

    if ($('#place-order').hasClass('order-placed')) { 
        $('#place-order').text("Check Out");
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
       if (!$("#phone-no").val()) { 
            alert("Please Enter Phone Number !");
            return;
        }
        
        if (!$("#email-id").val()) { 
            alert("Please Enter Email ID !");
            return;
        } 
        if (!$("#street-address").val()) { 
            alert("Please Enter Street Address !");
            return;
        }
        if (!$("#town").val()) { 
            alert("Please Enter Town/City !");
            return;
        }
        if (!$("#stateInput").val()) { 
            alert("Please Enter State !");
            return;
        } 
        if (!$("#zip-code").val()) { 
            alert("Please Enter Zip Code !");
            return;
        }else{
            $("#zip-code").prop('disabled', true); 

        }
 

        // customer Billing section

        // if( $('#checkbox1').hasClass('billing-address')){
        //     console.log("billing address")
        //     frappe.xcall('leftword.web_api.address.add_billing_address',  {
        //         "email": $('#email-id').val(),
        //         "street": $("#billing-street-address").val(),
        //         "city": $("#billing-town").val(),
        //         "country": $("#billing-country").val(),
        //         "phone": $("#phone-no").val(),
        //         "zip_code": $("#billing-zip-code").val(),
        //         "state": $("billing-stateInput").val(),
        //         "first_name": $('#first-name').val(),
        //         "last_name": $('#last-name').val(),

        // }).then(function(){
        //     $('#checkbox1').removeClass('billing-address');
        //     $("input[type='text']").prop('disabled', true);

        // });
            
        // }
      
        $('#place-order').text("Placing Order...");
        frappe.call(
            {
            method: 'leftwordlatest.web_api.checkout.create_order',
            callback(r) {
                $('#place-order').removeClass('cart-items');
                $('#place-order').addClass('order-placed');
                $('#place-order').text("Check Out");
                $(".order-placed").removeAttr("id");
                $(".order-placed").attr('id', 'checkout'); 

                $('.btn-group.item-count').remove();

            }
                
            });

        if ($("#zip-code").val() && $("#stateInput").val() && $("#town").val() && 
            $("#street-address").val() && $("#email-id").val() && $("#phone-no").val() && $("#town").val()) {

                frappe.xcall('leftwordlatest.web_api.address.add_shipping_address',  {
                    "email": $('#email-id').val(),
                    "street": $("#street-address").val(),
                    "city": $("#town").val(),
                    "country": $("#country").val(),
                    "phone": $("#phone-no").val(),
                    "zip_code": $("#zip-code").val(),
                    "state": $("#stateInput").val(),
                    "first_name": $('#first-name').val(),
                    "last_name": $('#last-name').val(),

                }).then(function() {
                    $("input[type='text']").prop('readonly', true);

                });
        }

       
        if ($('#checkout').hasClass('order-placed')) { 
            $('#checkout').text("Check Out");
            frappe.xcall('leftwordlatest.web_api.checkout.create_invoice', {}).then(function() {
                
                $('#checkout').removeClass('order-placed');
                $('#checkout').text("Place Order");
                window.location.href = '/start_payment'; 
            });
            $(".checkout").removeAttr("id");
            $(".checkout").attr('id', 'place-order');
        }


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
