frappe.ready(() => {

        $('.logout').on("click", function(e){
            e.preventDefault()
            frappe.xcall("logout").then(data=>{
                window.location.href = '/leftword_home'
            })
        })
    $('.wishlist-cart').on('click', function() {

        var item_code = $(this).attr('data-item-code');
        var qty = 1;
        const currency = sessionStorage.getItem('selectedCurrency') || 'INR';
        frappe.call({
            method: 'leftwordlatest.web_api.cart.make_cart',
            args: {
                item_code: item_code,
                qty: qty,
                currency: currency
            },
            callback(r) {
                window.location.href = '/shopping_cart';
            }
        });
        frappe.xcall('leftwordlatest.web_api.wishlist.remove_wishlist', {
            "item_code": item_code
        });

    });

    $('.delete-wishlist').on('click', function() {
        frappe.xcall('leftwordlatest.web_api.wishlist.remove_wishlist', {
            "item_code":$('.wishlist-cart').attr('data-item-code')
        }).then(() => {

            location.reload();
        });
    });


});