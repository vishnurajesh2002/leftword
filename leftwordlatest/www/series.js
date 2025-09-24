frappe.ready(function(){
    getItems(null, false, true);
    // initializeFilters();
    initializePagination();

    $('.order-select').on('click', function(e){
        e.preventDefault()
        if ($('.order-select')[0].value == "book_name"){
            order_key = ["web_item_name", "ASC"]
            getItems($('.current-page')[0].firstChild.innerText, true, false, order_key)
        }
        else if ($('.order-select')[0].value == "rate_asc"){
            order_key = ["price_list_rate", "ASC"]
            getItems($('.current-page')[0].firstChild.innerText, true, false, order_key)
        }
        else if ($('.order-select')[0].value == "rate_desc"){
            order_key = ["price_list_rate", "DESC"]
            getItems($('.current-page')[0].firstChild.innerText, true, false, order_key)
        }
        else {  
            getItems($('.current-page')[0].firstChild.innerText, true, false)
        }
    });

    $('.page-select').on('click', function(e) {
        e.preventDefault()
        if ($('.order-select')[0].value == "book_name"){
            order_key = ["web_item_name", "ASC"]
            getItems($('.current-page')[0].firstChild.innerText, true, false, order_key)

        }
        else if ($('.order-select')[0].value == "rate_asc"){
            order_key = ["price_list_rate", "ASC"]
            getItems($('.current-page')[0].firstChild.innerText, true, false, order_key)

        }
        else if ($('.order-select')[0].value == "rate_desc"){
            order_key = ["price_list_rate", "DESC"]
            getItems($('.current-page')[0].firstChild.innerText, true, false, order_key)

        }
        else {  
            order_key = null
        }

        getItems($('.current-page')[0].firstChild.innerText, true, false, order_key)
    });

});


let catFilters = []
var itemCount = 0
var pageCount = $('.pagination')[0].getAttribute('data-item_count') | 0

// function initializeFilters(){
//     $('.category_filter').on('click', function(e){
//         if(e.target.checked){
//             catFilters.push(e.target.value)
//             getItems(null, true, true)
//         }
//         else if(!e.target.checked){
//             catFilters.pop(e.target.value)
//             getItems(null, true, true)
//         }
//     });
// };

// Pagination
function initializePagination(){
    $('.paginate').on('click', function(e){
        e.preventDefault()
        let pageNo = $(e.target)[0].parentElement.firstChild.innerText
        if($(e.target)[0].getAttribute('value') == 3){
            setforwardPages(pageNo)
            sortingConditionCheck(pageNo);
        }else{
            togglePage($(e.target.parentElement))
            sortingConditionCheck(pageNo);
        }
    });
    
    $('.next-forward').on('click', function (e) {
        e.preventDefault()
        if ($('.current-page')[0].nextElementSibling.classList.contains('paginate')) {
            let pageNo = $('.current-page')[0].nextElementSibling.innerText
            sortingConditionCheck(pageNo);
            if ($('.current-page')[0].nextElementSibling.firstChild.getAttribute('value') == 3) {
                setforwardPages($('.current-page')[0].nextElementSibling.innerText)
            } else {
                togglePage($('.current-page')[0].nextElementSibling)
            }
        }
    });
    
    $('.next-backward').on('click', function(e){
        e.preventDefault()
        if($('.current-page')[0].previousElementSibling.classList.contains('paginate')){
            let pageNo = $('.current-page')[0].previousElementSibling.innerText
            sortingConditionCheck(pageNo);
            togglePage($('.current-page')[0].previousElementSibling)
        }else{
            if (parseInt(parseInt($('.current-page')[0].firstChild.innerText) -2) > 0) {
                let pageNo = parseInt($('.current-page')[0].firstChild.innerText) - 1 
                sortingConditionCheck(pageNo);
                setbackwardPages(parseInt($('.current-page')[0].firstChild.innerText) -2, true)
            }
        }
    });
};

function togglePage(element){
    let currentPage = $(element)[0].firstChild.getAttribute('value')
    let pageNo = $(element)[0].firstChild.innerText
    $('.paginate').removeClass('active')
    $('.paginate').removeClass('current-page')
    $(element).addClass('active')
    $(element).addClass('current-page')
};

function setforwardPages(pageNo){
    // Inital design for 3 page no.s. Should use 'for loop' for greater values!
    let newPageNo = ""
    if(pageCount - pageNo >= 2){
        newPageNo = `<li class="page-item paginate active current-page"><a class="page-link" id="" value="1" href="">${pageNo}</a></li>
            <li class="page-item paginate"><a class="page-link" id="" value="2" href="#">${parseInt(pageNo)+1}</a></li>
            <li class="page-item paginate"><a class="page-link" id="" value="3" href="#">${parseInt(pageNo)+2}</a></li>
            `
    }else if(pageCount - pageNo == 1){
        newPageNo = `<li class="page-item paginate active current-page"><a class="page-link" id="" value="1" href="">${pageNo}</a></li>
        <li class="page-item paginate"><a class="page-link" id="" value="2" href="#">${parseInt(pageNo)+1}</a></li>`
    }else{
        newPageNo = `<li class="page-item paginate active current-page"><a class="page-link" id="" value="1" href="">${pageNo}</a></li>`
    }
    setPaginator(newPageNo)
};

function setbackwardPages(pageNo){
    newPageNo = `<li class="page-item paginate"><a class="page-link" id="" value="1" href="">${pageNo}</a></li>
        <li class="page-item paginate active current-page"><a class="page-link" id="" value="2" href="#">${parseInt(pageNo)+1}</a></li>
        <li class="page-item paginate"><a class="page-link" id="" value="3" href="#">${parseInt(pageNo)+2}</a></li>
        `
    setPaginator(newPageNo)  
};

function setPaginator(newPageNo){
    $('.pagination').html("")
    let data = $(`<li class="page-item">
            <a class="page-link next-backward" href="#" aria-label="Previous">
            <span aria-hidden="true">&laquo;</span>
            </a>
        </li>
        ${newPageNo}
        <li class="page-item">
            <a class="page-link next-forward" href="#" aria-label="Next">
            <span aria-hidden="true">&raquo;</span>
            </a>
        </li>`).appendTo($('.pagination'))
    initializePagination()
};

// Get Items and render
function getItems(pageNo, renderData=true, updatePageData=false, sort_key){

    product_per_page = $('.page-select')[0].value
    const urlArgs = new URLSearchParams(window.location.search);
    let selectedSeries = urlArgs.get('series');
    let filterArgs = null;
    if (urlArgs.get("filter_args")) {
        filterArgs = urlArgs.get("filter_args").split(",");
    }
    let filters = {};
    if (filterArgs) {
        filters = {
            item_code: filterArgs,
            product_category: catFilters
        }
    }
    else {
        filters = {
            product_category: catFilters
        }
    }
    frappe.xcall("leftwordlatest.web_api.itemquery.makeup_pagination", {
        // filters:{
        //     product_category: catFilters
        // },
        // if (selectedSeries) {
        //     filters["custom_series"] = selectedSeries;
        // },
        filters: filters,
        page:pageNo,
        sort_by: sort_key,
        search_key:selectedSeries,
        products_per_page: product_per_page
    }).then(data=>{
        if(updatePageData){
            itemCount = data.item_count
            pageCount = data.page_count
        }
        if(data.items && renderData){
            renderItems(data.items, itemCount, data.ppp, pageNo)
            if(!pageNo){
                setforwardPages(1)
            }
        }    
    })
};

function renderItems(items, item_count, ppp, page_no) {
    let data = "";
    let hideInr = "";
    let hideUsd = "";

    if ($('.transaction-currency')[0].value == "INR") {
        hideUsd = "display:none;";
    } else {
        hideInr = "display:none;";
    }

    if (items) {
        items.forEach(item => {
            const isGuest = frappe.session.user === "Guest";
            const addToCartButton = isGuest
                ? `<a href="#" class="btn-primary btn-style btn-icon-left add-to-cart-btn allow-guest-cart" 
                      data-bs-toggle="modal" data-bs-target="#lwsignIn">
                      Add to Cart
                   </a>`
                : `<button class="btn-primary btn-style btn-icon-left add-to-cart-btn" 
                      data-item-code="${item.item_code}" data-qty="1">
                      Add to Cart
                   </button>`;
                   let priceInr = item.price_list_rate_inr > 0
               ? `<span>INR</span>${item.price_list_rate_inr}`
               : `<span style="color: red;">Not Available In INR</span>`;


           // USD Price Display
           let priceUsd = item.price_list_rate_usd > 0
               ? `<span>USD</span>${item.price_list_rate_usd}`
               : `<span style="color: red;">Not Available In USD</span>`;


                   data += `
                   <div class="col mb-4">
                       <div class="itembooks card card-item">
                           <!-- Product Image -->
                           <a href="/productdetailspage?id=${item.item_code}" class="card-item-img">
                               <img 
                                   src="${item.custom_website_image 
                                       || item.website_image 
                                       || item.custom_image1 
                                       || item.custom_image2 
                                       || item.custom_image3 
                                       || '/src/img/blankImg.png'}" 
                                   class="">
                           </a>
               
                           <!-- Card Content -->
                           <div class="card-content">
                               <!-- Product Details -->
                               <div class="itemDetails">
                                   <a href="/productdetailspage?id=${item.item_code}">
                                       <h6 class="text-limit2">
                                           ${item.web_item_name}${item.custom_series ? ` - ${item.custom_series}` : ''}
                                       </h6>
                                   </a>
                                   <p>${item.brand || ''}</p>
                               </div>
               
                               <!-- Hover Section -->
                               <div class="cart-hover-sec">

                                   <!-- Price Details -->


                               <div class="price-amount currency_inr" style="${hideInr}">${priceInr}</div>


                               <div class="price-amount currency_usd" style="${hideUsd}">${priceUsd}</div>



                                   
                                   <!-- Add to Cart Button -->
                                   <div class="add-cart-btn">
                                       ${frappe.session.user === "Guest" ? 
                                           `<a href="#" 
                                               class="btn-primary btn-style btn-icon-left add-to-cart-btn allow-guest-cart" 
                                               data-bs-toggle="modal" data-bs-target="#lwsignIn">
                                               ADD TO CART
                                           </a>` 
                                           : 
                                           `<a href="#" 
                                               class="btn-primary btn-style btn-icon-left add-to-cart-btn" 
                                               data-item-code="${item.item_code}" data-qty="1">
                                               ADD TO CART
                                           </a>`}
                                   </div>
                               </div>
                           </div>
                       </div>
                   </div>
               `;
               
        })

        if(page_no) {
            pn = page_no
        }
        else{
            pn = 1;
        }
        let start = ((parseInt(ppp) * parseInt(pn)) - ppp) + 1;
        let end = (start + ppp) - 1;
        if (end > item_count) {
            end = item_count;
        }

        new_showing_count = (`
        <p>Showing ${start} - ${end} of <span class="bold">${item_count} result</span></p>
            `)
    }

    $('.product_list').html(data);
    $('.showing_count').html(new_showing_count);
};


// function renderDropdown(items) {
//     let options = `<option selected="">Select an option</option>`;
//     if (items) {
//         items.forEach(item => {
//             if (item.custom_series){
//                 options += `<option value="${item.custom_series}">${item.custom_series}</option>`;
//             }
//         });
//     }
//     $('.form-select.arrows').html(options);  // Assuming this class is unique to the dropdown
// };

// function initializeFilters() {
    
//     $('.form-select.arrows').on('change', function () {
//         let selectedSeries = $(this).val();
//         console.log("Selected Series:", selectedSeries);
//         getItems(null, true, true, selectedSeries); 
//     });

    
//     $('.category_filter').on('click', function(e) {
//         if(e.target.checked){
//             catFilters.push(e.target.value);
//         } else {
//             catFilters.pop(e.target.value);
//         }
//         getItems(null, true, true); 
//     });
// };


function sortingConditionCheck(pageNo){
    if ($('.order-select')[0].value == "book_name"){
        order_key = ["web_item_name", "ASC"]
        getItems(pageNo, true, false, order_key)
    }
    else if ($('.order-select')[0].value == "rate_asc"){
        order_key = ["price_list_rate", "ASC"]
        getItems(pageNo, true, false, order_key)
    }
    else if ($('.order-select')[0].value == "rate_desc"){
        order_key = ["price_list_rate", "DESC"]
        getItems(pageNo, true, false, order_key)
    }
    else if ($('.order-select')[0].value == "Select an option"){
        getItems(pageNo, true, false)
    }
    else {
        getItems(pageNo)
    }
}

$('.product_list').on('click', '.add-to-cart-btn', function(e) {
    e.preventDefault(); // Prevent the default anchor behavior
    const itemCode = $(this).data('item-code'); // Get item code from the data attribute
    const qty = $(this).data('qty'); // Get quantity from the data attribute
    const currency = sessionStorage.getItem('selectedCurrency') || 'INR';
    // Call the make_cart function in the backend
    frappe.call({
        method: 'leftwordlatest.web_api.cart.make_cart',
        args: {
            item_code: itemCode,
            qty: qty,
            currency: currency
        },
        callback: function(response) {
            if (response.message) {
                const cartId = response.message[0]; // Get the cart ID if needed
                const totalQty = response.message[1]; // Get the total quantity
                const netTotal = response.message[2]; // Get the total net amount

                // Update cart count display, etc.
                $('#cart-count').text(totalQty); // Update cart count on the page
                
                // Change the button text and style
                const $cartButton = $('#cart-button');
                $cartButton.text("Go to Cart");
                $cartButton.removeClass('add-to-cart').addClass('in-cart');
                
                // Store the cart ID in a cookie
                document.cookie = `cart_id=${cartId}`;
                showSuccessMessage('Item added to cart successfully!');
            }
        },
        error: function(err) {
            console.error('#', err);
        }
    });
});
function showSuccessMessage(message) {

    // Create a div for the message

    const messageDiv = $('<div class="success-message"></div>').text(message);

    

    // Append the message to the body or a specific container

    $('body').append(messageDiv);


    // Optionally, you can style the message

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


    // Remove the message after a few seconds

    setTimeout(() => {

        messageDiv.fadeOut(300, () => {

            messageDiv.remove();

        });

    }, 3000);

}
$('#cart-button').on('click', function(e) {
    // Check if the button is in 'add-to-cart' state
    if ($('#cart-button').hasClass('add-to-cart')) {
        if (!$('#cart-button').hasClass('allow-guest-cart') && frappe.session.user === "Guest") {
            window.location.href = '/leftword_login';
            return;
        }
        
        const item_code = $('#cart-button').data('item-code');
        const count = parseInt($('#item-count').text().trim());
        const cartCurrency = sessionStorage.getItem('selectedCurrency') || 'INR';
        $('#cart-button').text("Adding To Cart...");
        
        // Call the backend to add to cart
        frappe.call({
            method: 'leftwordlatest.web_api.cart.make_cart',
            args: {
                item_code: item_code,
                qty: count,
                currency: cartCurrency
            },
            callback: function(r) {
                $('#cart-count').text(r.message[1]); // Update cart count on the page
                if (r.message) {
                    document.cookie = `cart_id=${r.message[0]}`;
                }
                $('#cart-button').prop('disabled', false);
                $('#cart-button').text("Go to Cart");
            }
        });
        
        // Update button state
        $('#cart-button').removeClass('add-to-cart');
        $('#cart-button').addClass('in-cart');
    } else if ($('#cart-button').hasClass('in-cart')) {
        // Redirect to shopping cart page
        window.location.href = '/shopping_cart';
    }
});





