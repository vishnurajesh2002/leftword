// let currentPage = 1;
// let itemsPerPage = 20;
// let authors = [];
// let sortOrder = 'default';

// function fetchAuthors() {
//    frappe.call({
//        method: "leftword.web_api.author.get_items_with_authors",
//        args: {},
//        callback: function(response) {
//            if (response.message) {
//                authors = response.message;
//                applySortAndRender();
//            } else {
//            }
//        },
//        error: function(error) {
//        }
//    });
// }

// function applySortAndRender() {
//    if (sortOrder === 'az') {
//        authors.sort((a, b) => a.author_name.localeCompare(b.author_name));
//    } else {
//        authors.sort((a, b) => b.items.length - a.items.length);
//    }
//    renderAuthors();
// }

// function renderAuthors() {
//    const authorSection = document.querySelector('.lw-author .row:last-child');
//    if (!authorSection) {
//        return;
//    }

//    authorSection.innerHTML = '';

//    const startIndex = (currentPage - 1) * itemsPerPage;
//    const endIndex = Math.min(startIndex + itemsPerPage, authors.length);

//    for (let i = startIndex; i < endIndex; i++) {
//        const author = authors[i];
//        const authorImage = author.author_image ? author.author_image : '/src/img/author-img1.png';

//        const authorCard = `
//            <div class="col mb-4">
//                <div class="card card-item">
//                    <a href="authordetail.html?author_name=${encodeURIComponent(author.author_name)}" class="card-item-img">
//                        <img src="${authorImage}" alt="${author.author_name}" class="">
//                    </a>
//                    <div class="card-content">
//                        <div class="authorCard-Details">
//                            <h6 class="text-limit2">${author.author_name}</h6>
//                            <p class="text-limit2">${author.author_description}</p>
//                        </div>
//                        <div class="authorCard-btn">
//                            <div class="add-cart-btn">
//                                <a href="authordetails?author_name=${encodeURIComponent(author.author_name)}" class="btn btn-primary btn100">View More</a>
//                                <a href="authordetails?author_name=${encodeURIComponent(author.author_name)}" class="btn btn-secondary btn-icon btn-icon-left btn-icon-book">${author.items.length}</a>
//                            </div>
//                        </div>
//                    </div>
//                </div>
//            </div>`;
//        authorSection.innerHTML += authorCard;
//    }

//    updatePaginationInfo();
// }

// function updatePaginationInfo() {
//    const totalResults = authors.length;
//    const showingStart = (currentPage - 1) * itemsPerPage + 1;
//    const showingEnd = Math.min(currentPage * itemsPerPage, totalResults);

//    const paginationText = document.querySelector('.filter-bar p');
//    if (paginationText) {
//        paginationText.innerHTML = `Showing ${showingStart} - ${showingEnd} of <span class="bold">${totalResults} result</span>`;
//    }
// }

// document.addEventListener("DOMContentLoaded", function() {
//    fetchAuthors();

//    const sortDropdown = document.querySelector('.filter-bar select[aria-label="Default select example"]');
//    if (sortDropdown) {
//        sortDropdown.addEventListener('change', function(e) {
//            const selectedOption = e.target.value;
//            if (selectedOption === "1") {
//                sortOrder = 'az';
//            } else {
//                sortOrder = 'default';
//            }
//            applySortAndRender();
//        });
//    } else {
//    }

//    const showDropdown = document.querySelector('.filter-bar select[aria-label="Show items per page"]');
//    if (showDropdown) {
//        showDropdown.addEventListener('change', function(e) {
//            itemsPerPage = parseInt(e.target.value) || 20;
//            currentPage = 1;
//            renderAuthors();
//        });
//    } else {
//    }

   
   
// });

frappe.ready(function () {
    getAuthors(null, false, true);
    initializePagination();

    $('.order-select').on('click', function(e){
        e.preventDefault()
        if ($('.order-select')[0].value == "1"){
            order_key = ["custom_name", "ASC"]
            getAuthors($('.current-page')[0].firstChild.innerText, true, false, order_key)
        }
        else if ($('.order-select')[0].value == "2"){
            order_key = ["custom_name", "DESC"]
            getAuthors($('.current-page')[0].firstChild.innerText, true, false, order_key)
        }
        else {
            getAuthors($('.current-page')[0].firstChild.innerText, true, false)
        }
    });

    $('.page-select').on('click', function(e) {
        e.preventDefault()
        if ($('.order-select')[0].value == "1"){
            order_key = ["custom_name", "ASC"]
        }
        else if ($('.order-select')[0].value == "2"){
            order_key = ["custom_name", "DESC"]
        }
        else {  
            order_key = null
        }

        getAuthors(null, true, true, order_key)
    });

    $('.product_list, .owl-carousel').on('click', '.add-to-cart-btn', function(e) {
        e.preventDefault(); 
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
                        .removeClass('add-to-cart')
                        .addClass('in-cart');
 
                        showSuccessMessage('Item added to cart successfully!');

                    document.cookie = `cart_id=${response.message[0]}`;
                }  
            },
            error: function(err) {
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
       
        if ($('#cart-button').hasClass('add-to-cart')) {
            if (!$('#cart-button').hasClass('allow-guest-cart') && frappe.session.user === "Guest") {
                window.location.href = '/leftword_login';
                return;
            }
 
            const item_code = $('#cart-button').data('item-code');
            const count = parseInt($('#item-count').text().trim());
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

let catFilters = []
var authorCount = 0
var pageCount = $('.pagination')[0].getAttribute('data-author_count') | 0

function initializePagination() {
    $('.paginate').on('click', function (e) {
        e.preventDefault()
        let pageNo = $(e.target)[0].parentElement.firstChild.innerText
        if ($(e.target)[0].getAttribute('value') == 3) {
            setforwardPages(pageNo)
            sortingConditionCheck(pageNo);
        } else {
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

    $('.next-backward').on('click', function (e) {
        e.preventDefault()
        if ($('.current-page')[0].previousElementSibling.classList.contains('paginate')) {
            let pageNo = $('.current-page')[0].previousElementSibling.innerText
            sortingConditionCheck(pageNo);
            togglePage($('.current-page')[0].previousElementSibling)
        } else {
            if (parseInt(parseInt($('.current-page')[0].firstChild.innerText) - 2) > 0) {
                let pageNo = parseInt($('.current-page')[0].firstChild.innerText) - 1 
                sortingConditionCheck(pageNo);
                setbackwardPages(parseInt($('.current-page')[0].firstChild.innerText) - 2, true)
            }
        }
    });
};

function togglePage(element) {
    let currentPage = $(element)[0].firstChild.getAttribute('value')
    let pageNo = $(element)[0].firstChild.innerText
    $('.paginate').removeClass('active')
    $('.paginate').removeClass('current-page')
    $(element).addClass('active')
    $(element).addClass('current-page')
};

function setforwardPages(pageNo) {
    let newPageNo = ""
    if (pageCount - pageNo >= 2) {
        newPageNo = `<li class="page-item paginate active current-page"><a class="page-link" id="" value="1" href="">${pageNo}</a></li>
            <li class="page-item paginate"><a class="page-link" id="" value="2" href="#">${parseInt(pageNo) + 1}</a></li>
            <li class="page-item paginate"><a class="page-link" id="" value="3" href="#">${parseInt(pageNo) + 2}</a></li>
            `
    } else if (pageCount - pageNo == 1) {
        newPageNo = `<li class="page-item paginate active current-page"><a class="page-link" id="" value="1" href="">${pageNo}</a></li>
        <li class="page-item paginate"><a class="page-link" id="" value="2" href="#">${parseInt(pageNo) + 1}</a></li>`
    } else {
        newPageNo = `<li class="page-item paginate active current-page"><a class="page-link" id="" value="1" href="">${pageNo}</a></li>`
    }
    setPaginator(newPageNo)
};

function setbackwardPages(pageNo) {
    newPageNo = `<li class="page-item paginate"><a class="page-link" id="" value="1" href="">${pageNo}</a></li>
        <li class="page-item paginate active current-page"><a class="page-link" id="" value="2" href="#">${parseInt(pageNo) + 1}</a></li>
        <li class="page-item paginate"><a class="page-link" id="" value="3" href="#">${parseInt(pageNo) + 2}</a></li>
        `
    setPaginator(newPageNo)
};

function setPaginator(newPageNo) {
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


function getAuthors(pageNo, renderData = true, updatePageData = false, sort_key) {
    product_per_page = $('.page-select')[0].value
    frappe.xcall("leftwordlatest.web_api.author.get_items_with_authors", {
        page: pageNo,
        order_by: sort_key,
        author_per_page: product_per_page
    }).then(data => {
        if (updatePageData) {
            authorCount = data.author_count
            pageCount = data.page_count
        }
        if (data.authors && renderData) {
            renderAuthors(data.authors, authorCount, data.auth_per_page, pageNo)
            if (!pageNo) {
                setforwardPages(1)
            }
        }
    })
};

function renderAuthors(authors, author_count, auth_per_page, page_no) {
    let data = ""
    hideInr = ""
    hideUsd = ""
    if ($('.transaction-currency')[0].value == "INR") {
        hideUsd = "display:none;"
    } else {
        hideInr = "display:none;"
    }
    if (authors) {
        authors.forEach(author => {
            data += (`
                <div class="col mb-4">
                    <div class="card card-item">
                        <a href="authordetails?author_name=${author.author_name}" class="card-item-img">
                            ${author.author_image ? 
                                `<img src="${author.author_image}" alt="${author.author_name}" class="">` : 
                                `<img src="/src/img/blankImg.png" alt="${author.author_name}" class="">`}
                        </a>
                        <div class="card-content">
                            <div class="authorCard-Details">
                                <h6 class="text-limit2">${author.author_name}</h6>
                                <p class="text-limit2">${author.author_description ? author.author_description : ''}
                            </div>
                            <div class="authorCard-btn">
                                <div class="add-cart-btn">
                                    <a href="authordetails?author_name=${author.author_name}" class="btn btn-primary btn100">View More</a>
                                    <a href="authordetails?author_name=${author.author_name}" class="btn btn-secondary btn-icon btn-icon-left btn-icon-book">${author.items.length}</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `);
        });
        
        if(page_no) {
            pn = page_no
        }
        else{
            pn = 1;
        }

        let start = ((parseInt(auth_per_page) * parseInt(pn)) - auth_per_page) + 1;
        let end = (start + auth_per_page) - 1;
        if (end > author_count){
            end = author_count
        }

        new_showing_count = (`
        <p>Showing ${start} - ${end} of <span class="bold">${author_count} result</span></p>
            `)
    }
    $('.author_list').html(data)
    $('.showing_count').html(new_showing_count)

    
};

function sortingConditionCheck(pageNo){

    if ($('.order-select')[0].value == "1"){
        order_key = ["custom_name", "ASC"]
        getAuthors(pageNo, true, false, order_key)
    }
    else if ($('.order-select')[0].value == "2"){
        order_key = ["custom_name", "DESC"]
        getAuthors(pageNo, true, false, order_key)
    }
    else {
        getAuthors(pageNo)
    }
}