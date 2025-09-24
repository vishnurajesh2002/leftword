frappe.ready(function(){
    getItems(null, false, true);
    initializeFilters();
    initializePagination();
})

let catFilters = []
var itemCount = 0
var pageCount = $('.pagination')[0].getAttribute('data-item_count') | 0

function initializeFilters(){
    $('.category_filter').on('click', function(e){
        if(e.target.checked){
            catFilters.push(e.target.value)
            getItems(null, true, true)
        }
        else if(!e.target.checked){
            catFilters.pop(e.target.value)
            getItems(null, true, true)
        }
    });
};

// Pagination
function initializePagination() {
    $('.paginate').on('click', function(e) {
        e.preventDefault();
        let pageNo = parseInt($(e.target).text());
        togglePage($(e.target).closest('.page-item'));
        getItems(pageNo);
    });

    $('.next-forward').on('click', function(e) {
        e.preventDefault();
        let currentPage = parseInt($('.current-page a').text());
        if (currentPage < pageCount) {
            getItems(currentPage + 1);
            setforwardPages(currentPage + 1);
        }
    });
    $('.next-backward').on('click', function(e) {
        e.preventDefault();
        let currentPage = parseInt($('.current-page a').text());
        if (currentPage > 1) {
            getItems(currentPage - 1);
    
            let targetPage = currentPage - 2;
            if (targetPage < 1) {
                targetPage = 1;
            }
    
            setbackwardPages(targetPage);
        }
    });
    
}


function togglePage(element){
    let currentPage = $(element)[0].firstChild.getAttribute('value')
    let pageNo = $(element)[0].firstChild.innerText
    $('.paginate').removeClass('active')
    $('.paginate').removeClass('current-page')
    $(element).addClass('active')
    $(element).addClass('current-page')
};
function setforwardPages(pageNo) {
    let newPageNo = "";
    pageNo = parseInt(pageNo); // Ensure pageNo is a number

    if (pageCount - pageNo >= 2) {
        newPageNo = `<li class="page-item paginate active current-page"><a class="page-link" value="1" href="#">${pageNo}</a></li>
                     <li class="page-item paginate"><a class="page-link" value="2" href="#">${pageNo + 1}</a></li>
                     <li class="page-item paginate"><a class="page-link" value="3" href="#">${pageNo + 2}</a></li>`;
    } else if (pageCount - pageNo === 1) {
        newPageNo = `<li class="page-item paginate active current-page"><a class="page-link" value="1" href="#">${pageNo}</a></li>
                     <li class="page-item paginate"><a class="page-link" value="2" href="#">${pageNo + 1}</a></li>`;
    } else {
        newPageNo = `<li class="page-item paginate active current-page"><a class="page-link" value="1" href="#">${pageNo}</a></li>`;
    }
    setPaginator(newPageNo);
}

function setbackwardPages(pageNo) {
    pageNo = parseInt(pageNo); // Ensure pageNo is a number

    let newPageNo = `<li class="page-item paginate"><a class="page-link" value="1" href="#">${pageNo}</a></li>
                     <li class="page-item paginate active current-page"><a class="page-link" value="2" href="#">${pageNo + 1}</a></li>
                     <li class="page-item paginate"><a class="page-link" value="3" href="#">${pageNo + 2}</a></li>`;
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


// Get Items and render
function getItems(pageNo, renderData = true, updatePageData = false) {
    frappe.xcall("leftwordlatest.web_api.items.makeup_pagination", {
        filters: {
            product_category: catFilters
        },
        page: pageNo // Pass page number to backend
    }).then(data => {
        if (updatePageData) {
            itemCount = data.item_count; // Total number of items
            pageCount = Math.ceil(itemCount / 12); // Calculate pages based on 12 items per page
        }
        if (data.items && renderData) {
            renderItems(data.items);
            if (!pageNo) {
                setforwardPages(1); // Default to the first page
            }
        }
    });
}


function renderItems(items){
    let data = ""
    hideInr = ""
    hideUsd = ""
    if($('.transaction-currency')[0].value == "INR"){
        hideUsd = "display:none;"
    }else{
        hideInr = "display:none;"
    }
    if (items) {
        items.forEach(item => {
            // Determine the correct image source based on the order of precedence
            let imageSrc = item.image 
                || item.custom_website_image 
                || item.website_image 
                || item.custom_image1 
                || item.custom_image2 
                || item.custom_image3 
                || '/src/img/blankImg.png';
    
            data += `
                <div class="col mb-4">
                    <div class="itembooks card card-item">
                        <a href="/productdetailspage?id=${item.item_code}" class="card-item-img">
                            <img src="${imageSrc}" class="img-fluid" alt="${item.web_item_name || 'Default Image'}" 
                                 onerror="this.onerror=null; this.src='/src/img/blankImg.png';">
                        </a>
                        <div class="card-content">
                            <div class="itemDetails">
                                <a href="/productdetailspage?id=${item.item_code}">
                                    <h6 class="text-limit2">${__(item.web_item_name)}</h6>
                                </a>
                                <p>${item.brand || ''}</p>
                            </div>
                            <div class="cart-hover-sec">
                                <div class="price-amount">
                                    <div class="price-amount currency_inr" style="${hideInr}">
                                        <span>INR</span> ${item.price_list_rate_inr.toFixed(1)}
                                    </div>
                                    <div class="price-amount currency_usd" style="${hideUsd}">
                                        <span>USD</span> ${item.price_list_rate_usd.toFixed(1)}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
    }
    
    $('.product_list').html(data)
};