// frappe.ready(function(){
//     getItems(null, false, true);
//     initializeFilters();
//     initializePagination();
//  })
//  let catFilters = []
//  var itemCount = 0
//  var pageCount = $('.pagination')[0].getAttribute('data-item_count') | 0
//  function initializeFilters(){
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
//  };
//  // Pagination
//  function initializePagination(){
//     $('.paginate').on('click', function(e){
//         e.preventDefault()
//         let pageNo = $(e.target)[0].parentElement.firstChild.innerText
//         if($(e.target)[0].getAttribute('value') == 3){
//             setforwardPages(pageNo)
//             getItems(pageNo)
//         }else{
//             togglePage($(e.target.parentElement))
//             getItems(pageNo)
//         }
//     });
//     $('.next-forward').on('click', function(e){
//         e.preventDefault()
//         if($('.current-page')[0].nextElementSibling.classList.contains('paginate')){
//                 getItems($('.current-page')[0].nextElementSibling.innerText)
//                 if($('.current-page')[0].nextElementSibling.firstChild.getAttribute('value') == 3){
//                     setforwardPages($('.current-page')[0].nextElementSibling.innerText)
//                 }else{
//                     togglePage($('.current-page')[0].nextElementSibling)
//                 }
//         }
//     });
//     $('.next-backward').on('click', function(e){
//         e.preventDefault()
//         if($('.current-page')[0].previousElementSibling.classList.contains('paginate')){
//             getItems($('.current-page')[0].previousElementSibling.innerText)
//             togglePage($('.current-page')[0].previousElementSibling)
//         }else{
//             if(parseInt(parseInt($('.current-page')[0].firstChild.innerText)-2) > 0){
//                 getItems(parseInt($('.current-page')[0].firstChild.innerText)-1)
//                 setbackwardPages(parseInt($('.current-page')[0].firstChild.innerText)-2, true)
//             }
//         }
//     });
//  };
//  function togglePage(element){
//     let currentPage = $(element)[0].firstChild.getAttribute('value')
//     let pageNo = $(element)[0].firstChild.innerText
//     $('.paginate').removeClass('active')
//     $('.paginate').removeClass('current-page')
//     $(element).addClass('active')
//     $(element).addClass('current-page')
//  };
//  function setforwardPages(pageNo){
//     // Inital design for 3 page no.s. Should use 'for loop' for greater values!
//     let newPageNo = ""
//     if(pageCount - pageNo >= 2){
//         newPageNo = `<li class="page-item paginate active current-page"><a class="page-link" id="" value="1" href="">${pageNo}</a></li>
//             <li class="page-item paginate"><a class="page-link" id="" value="2" href="#">${parseInt(pageNo)+1}</a></li>
//             <li class="page-item paginate"><a class="page-link" id="" value="3" href="#">${parseInt(pageNo)+2}</a></li>
//             `
//     }else if(pageCount - pageNo == 1){
//         newPageNo = `<li class="page-item paginate active current-page"><a class="page-link" id="" value="1" href="">${pageNo}</a></li>
//         <li class="page-item paginate"><a class="page-link" id="" value="2" href="#">${parseInt(pageNo)+1}</a></li>`
//     }else{
//         newPageNo = `<li class="page-item paginate active current-page"><a class="page-link" id="" value="1" href="">${pageNo}</a></li>`
//     }
//     setPaginator(newPageNo)
//  };
//  function setbackwardPages(pageNo){
//     newPageNo = `<li class="page-item paginate"><a class="page-link" id="" value="1" href="">${pageNo}</a></li>
//         <li class="page-item paginate active current-page"><a class="page-link" id="" value="2" href="#">${parseInt(pageNo)+1}</a></li>
//         <li class="page-item paginate"><a class="page-link" id="" value="3" href="#">${parseInt(pageNo)+2}</a></li>
//         `
//     setPaginator(newPageNo)
//  };
//  function setPaginator(newPageNo){
//     $('.pagination').html("")
//     let data = $(`<li class="page-item">
//             <a class="page-link next-backward" href="#" aria-label="Previous">
//             <span aria-hidden="true">&laquo;</span>
//             </a>
//         </li>
//         ${newPageNo}
//         <li class="page-item">
//             <a class="page-link next-forward" href="#" aria-label="Next">
//             <span aria-hidden="true">&raquo;</span>
//             </a>
//         </li>`).appendTo($('.pagination'))
//     initializePagination()
//  };
//  // Get Items and render
//  function getItems(pageNo, renderData=true, updatePageData=false){
//     frappe.xcall("leftword.web_api.items.makeup_pagination", {
//         filters:{
//             product_category: catFilters
//         },
//         page:pageNo
//     }).then(data=>{
//         if(updatePageData){
//             itemCount = data.item_count
//             pageCount = data.page_count
//         }
//         if(data.items && renderData){
//             renderItems(data.items)
//             if(!pageNo){
//                 setforwardPages(1)
//             }
//         }
//     })
//  };
//  function renderItems(items){
//     let data = ""
//     hideInr = ""
//     hideUsd = ""
//     if($('.transaction-currency')[0].value == "INR"){
//         hideUsd = "display:none;"
//     }else{
//         hideInr = "display:none;"
//     }
//     if(items){
//         items.forEach(item=>{
//             data += (`
//             <div class="col-xl-3 col-md-6">
//                 <div class="list-item">
//                     <a href="/product?id=${item.item_code}" class="card">
//                         <div class="item-img">
//                         <img src="${item.custom_website_image}" class="img-fluid">
//                         </div>
//                     </a>
//                     <div class="item-text">
//                         <label>${__(item.web_item_name)}</label>
//                         <!-- <h3>Zmats Kempe</h3> -->
//                         <p>
//                             <span class="item-price currency_inr" style="${hideInr}">
//                                 INR ${item.price_list_rate_inr.toFixed(1)}
//                             </span>
//                             <span class="item-price currency_usd" style="${hideUsd}">
//                                 USD ${item.price_list_rate_usd.toFixed(1)}
//                             </span>
//                         </p>
//                     </div>
//                 </div>
//             </div>
//             `)
//         })
//     }
//     $('.product_list').html(data)
//  };





frappe.ready(function() {
    
    const urlParams = new URLSearchParams(window.location.search);
    const filterArgs = urlParams.get('filter_args');
   
    if (filterArgs) {
        catFilters = decodeURIComponent(filterArgs).split(',');
    }
   
    
    updateFilterTags();
 
 
    getItems(null, false, true);
    initializeFilters();
    initializePagination();
    initializeSortAndPaginationOptions();
 
 

$('#clear-filters').on('click', function (e) {
    e.preventDefault();
    
    
    $('#sortSelector').val("Select an option"); 
    $('#itemCountSelector').val("10"); 
    
    
    $('.category_filter').prop('checked', false);
    catFilters = []; 
    
    
    sortOption = ""; 
    itemCount = 10; 
    
    
    getItems(1, true, true); 
});
 
 // Add to Cart functionality
 $('.product_list, .owl-carousel').on('click', '.add-to-cart-btn', function (e) {
    e.preventDefault();

    if (frappe.session.user === "Guest") {
        $('#lwsignIn').modal('show');
        return;
    }

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
        callback: function (response) {
            if (response.message) {
                const totalQty = response.message[1];
                $('#cart-count').text(totalQty); // Update cart count dynamically

                // Update button state to "In Cart"
                $(`.add-to-cart-btn[data-item-code="${itemCode}"]`)
                    .text("In Cart")
                    .removeClass('add-to-cart-btn')
                    .addClass('in-cart');

                // Update cart ID in cookies
                document.cookie = `cart_id=${response.message[0]}`;

                // Show success message
                showSuccessMessage('Item added to cart successfully!');

                // Hide success message after 1.5 seconds
                setTimeout(() => {
                    successMessage.style.display = "none";
                }, 1500);
            } 
        },
        error: function (err) {
            console.error('Error adding to cart:', err);
        }
    });
});



 $('#sortSelector').on('change', function() {
    let order_key = null;
 
 
    // Check the selected sorting option
    if ($(this).val() == "alphabetical") {
        order_key = ["web_item_name", "ASC"];  
    }
    else if ($(this).val() == "rate_asc") {
        order_key = ["price_list_rate", "ASC"];  
    }
    else if ($(this).val() == "rate_desc") {
        order_key = ["price_list_rate", "DESC"];  
    }
 
 
   
    getItems($('.current-page')[0].firstChild.innerText, true, false, order_key);
 });
 
 
 
 
 
 $('.page-select').on('click', function(e) {
    e.preventDefault();
    let order_key = null;
 
 
    
    if ($('.order-select')[0].value == "book_name_asc") {
        order_key = ["web_item_name", "ASC"];
    }
    else if ($('.order-select')[0].value == "book_name_desc") {
        order_key = ["web_item_name", "DESC"];
    }
    else if ($('.order-select')[0].value == "rate_asc") {
        order_key = ["price_list_rate", "ASC"];
    }
    else if ($('.order-select')[0].value == "rate_desc") {
        order_key = ["price_list_rate", "DESC"];
    }
 
 
    
    getItems(null, true, true, order_key);
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
    
    if ($('#cart-button').hasClass('add-to-cart')) {
        if (!$('#cart-button').hasClass('allow-guest-cart') && frappe.session.user === "Guest") {
            window.location.href = '/leftword_login';
            return;
        }
      
        const item_code = $('#cart-button').data('item-code');
        const count = parseInt($('#item-count').text().trim());
        $('#cart-button').prop('disabled', true); 
        $('#cart-button').text("Adding To Cart...");

        const cartCurrency = sessionStorage.getItem('selectedCurrency') || 'INR';
        
        frappe.call({
            method: 'leftwordlatest.web_api.cart.make_cart',
            args: {
                item_code: item_code,
                qty: count,
                currency: cartCurrency
            },
            callback: function(r) {
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
 });
 let catFilters = [];
 var itemCount = 20; 
 var pageCount = $('.pagination')[0].getAttribute('data-item_count') | 0;
 var sortOption = ''; 

 

function initializeFilters() {
    
    $('.category_filter').on('change', function(e) {
        const value = e.target.value;
        if (e.target.checked) {
            
            if (!catFilters.includes(value)) {
                catFilters.push(value);
            }
        } else {
            
            catFilters = catFilters.filter(filter => filter !== value);
        }
        updateFilterTags(); 
        getItems(1, true, true);  
    });

    
    $('.card-footer a').on('click', function(e) {
        e.preventDefault();
        
        $('.category_filter').prop('checked', false);
        catFilters = []; 
        updateFilterTags(); 
        getItems(1, true, true);  
    });
}


function updateFilterTags() {
    const filterTagContainer = $('.filter-tag ul');
    filterTagContainer.empty(); 

    catFilters.forEach(filter => {
        const tag = $(`
            <li>
                <div class="alert alert-primary alert-dismissible fade show" role="alert">
                    ${filter}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            </li>
        `);

        
        tag.find('.btn-close').on('click', function() {
            catFilters = catFilters.filter(f => f !== filter);
            $(`.category_filter[value="${filter}"]`).prop('checked', false);
            updateFilterTags(); 
            getItems(1, true, true); 
        });

        filterTagContainer.append(tag);
    });
}

 
 function initializeSortAndPaginationOptions() {
    $('#sortSelector').on('change', function() {
        sortOption = $(this).val(); 
        getItems(null, true, true); 
    });
    
    $('#itemCountSelector').on('change', function() {
        itemCount = parseInt($(this).val());  
        getItems(null, true, true);         
    });
 }
 // Pagination
 function initializePagination() {
    $('.paginate').on('click', function(e) {
        e.preventDefault();
        let pageNo = $(e.target)[0].parentElement.firstChild.innerText;
        if ($(e.target)[0].getAttribute('value') == 3) {
            setforwardPages(pageNo);
            getItems(pageNo);
        } else {
            togglePage($(e.target.parentElement));
            getItems(pageNo);
        }
    });
    $('.next-forward').on('click', function(e) {
        e.preventDefault();
        if ($('.current-page')[0].nextElementSibling.classList.contains('paginate')) {
            getItems($('.current-page')[0].nextElementSibling.innerText);
            if ($('.current-page')[0].nextElementSibling.firstChild.getAttribute('value') == 3) {
                setforwardPages($('.current-page')[0].nextElementSibling.innerText);
            } else {
                togglePage($('.current-page')[0].nextElementSibling);
            }
        }
    });
    $('.next-backward').on('click', function(e) {
        e.preventDefault();
        if ($('.current-page')[0].previousElementSibling.classList.contains('paginate')) {
            getItems($('.current-page')[0].previousElementSibling.innerText);
            togglePage($('.current-page')[0].previousElementSibling);
        } else {
            if (parseInt(parseInt($('.current-page')[0].firstChild.innerText) - 2) > 0) {
                getItems(parseInt($('.current-page')[0].firstChild.innerText) - 1);
                setbackwardPages(parseInt($('.current-page')[0].firstChild.innerText) - 2, true);
            }
        }
    });
 }
 function togglePage(element) {
    let currentPage = $(element)[0].firstChild.getAttribute('value');
    let pageNo = $(element)[0].firstChild.innerText;
    $('.paginate').removeClass('active');
    $('.paginate').removeClass('current-page');
    $(element).addClass('active');
    $(element).addClass('current-page');
 }
 function setforwardPages(pageNo) {
    let newPageNo = "";
    if (pageCount - pageNo >= 2) {
        newPageNo = `<li class="page-item paginate active current-page"><a class="page-link" id="" value="1" href="">${pageNo}</a></li>
            <li class="page-item paginate"><a class="page-link" id="" value="2" href="#">${parseInt(pageNo) + 1}</a></li>
            <li class="page-item paginate"><a class="page-link" id="" value="3" href="#">${parseInt(pageNo) + 2}</a></li>
            `;
    } else if (pageCount - pageNo == 1) {
        newPageNo = `<li class="page-item paginate active current-page"><a class="page-link" id="" value="1" href="">${pageNo}</a></li>
        <li class="page-item paginate"><a class="page-link" id="" value="2" href="#">${parseInt(pageNo) + 1}</a></li>`;
    } else {
        newPageNo = `<li class="page-item paginate active current-page"><a class="page-link" id="" value="1" href="">${pageNo}</a></li>`;
    }
    setPaginator(newPageNo);
 }
 function setbackwardPages(pageNo) {
    let newPageNo = `<li class="page-item paginate"><a class="page-link" id="" value="1" href="">${pageNo}</a></li>
        <li class="page-item paginate active current-page"><a class="page-link" id="" value="2" href="#">${parseInt(pageNo) + 1}</a></li>
        <li class="page-item paginate"><a class="page-link" id="" value="3" href="#">${parseInt(pageNo) + 2}</a></li>
        `;
    setPaginator(newPageNo);
 }
 function setPaginator(newPageNo) {
    $('.pagination').html("");
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
        </li>`).appendTo($('.pagination'));
    initializePagination();
 }
 //  // Get Items and render
 //  function getItems(pageNo, renderData = true, updatePageData = false) {
 //     frappe.xcall("leftword.web_api.items.makeup_pagination", {
 //         filters: {
 //             product_category: catFilters
 //         },
 //         page: pageNo,
 //         sort: sortOption, // Send the sort option to the backend if necessary
 //         item_count: itemCount // Send the item count to the backend
 //     }).then(data => {
 //         if (updatePageData) {
 //             itemCount = data.item_count;
 //             pageCount = data.page_count;
 //         }
 //         if (data.items && renderData) {
 //             // Sort items alphabetically if the sort option is set to 'alphabetical'
 //             if (sortOption === 'alphabetical') {
 //                 data.items.sort((a, b) => a.web_item_name.localeCompare(b.web_item_name));
 //             }
 //             renderItems(data.items);
 //             if (!pageNo) {
 //                 setforwardPages(1);
 //             }
 //         }
 //     });
 //  }
 // Fetch Items Function
 function getItems(pageNo = 1, renderData = true, updatePageData = false, sortKey = null) {
    let productsPerPage = $('#itemCountSelector').val();  
 
 
    frappe.xcall("leftwordlatest.web_api.items.makeup_pagination", {
        filters: {
            product_category: catFilters
        },
        page: pageNo,
        sort_by: JSON.stringify(sortKey || sortOption), 
        products_per_page: productsPerPage,  
    }).then(data => {
        if (updatePageData) {
            itemCount = data.item_count;
            pageCount = data.page_count;
        }
        if (data.items && renderData) {
            renderItems(data.items, itemCount, data.ppp, pageNo);
            if (!pageNo) {
                setforwardPages(1);
            }
        }
    });
 }
 
 
 function renderItems(items) {
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
            
            let imageUrl = item.custom_website_image || item.website_image || '/src/img/blankImg.png';
          
            data += (`
            <div class="col mb-4">
                <div class="card card-item">
                    <a href="/productdetailspage?id=${item.item_code}" class="card-item-img">
                        <img src="${imageUrl}" class="img-fluid" alt="${item.web_item_name}"
                             onerror="this.onerror=null; this.src='/src/img/blankImg.png';">
                    </a>
                    <div class="card-content">
                        <div class="itemDetails">
                            <h6 class="text-limit2">${__(item.web_item_name)}</h6>
                            <p>${item.publisher || ''}</p>
                        </div>
                        <div class="cart-hover-sec">
                            <div class="price-amount">
                                <div class="price-amount currency_inr" style="${hideInr}">
                                    <span>INR</span>${item.price_list_rate_inr.toFixed(1)}
                                </div>
                                <div class="price-amount currency_usd" style="${hideUsd}">
                                    <span>USD</span>${item.price_list_rate_usd.toFixed(1)}
                                </div>
                            </div>
                            <div class="add-cart-btn">
                                <a href="#" class="btn-primary btn-style btn-icon-left add-to-cart-btn" data-item-code="${item.item_code}" data-qty="1">ADD TO CART</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            `);
        });
    }
    $('.product_list').html(data);
 }
 
 