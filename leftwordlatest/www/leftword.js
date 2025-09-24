
frappe.ready(function () {
    // document.cookie =  "cart_id=12345;"
    frappe.xcall("leftwordlatest.web_api.cart.update_cart_count").then(data => {
        $('#cart-count').text(data)
    })

    function getTimeZoneBasedCurrency() {
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        return (timezone.includes("Asia/Calcutta") || timezone.includes("Asia/Kolkata")) ? "INR" : "USD";
    }

    let defaultCurrency = getTimeZoneBasedCurrency();
    let savedCurrency = sessionStorage.getItem("selectedCurrency");

    let currentCurrency = savedCurrency || defaultCurrency;

    if (savedCurrency) {
        currentCurrency = savedCurrency;
        updateCurrencyDropdown(currentCurrency);
    }
    else if (!savedCurrency) {
        frappe.xcall("leftwordlatest.utils.detect_country_and_currency").then(data => {
            if (!savedCurrency) {
                currentCurrency = data || defaultCurrency;
                sessionStorage.setItem("selectedCurrency", currentCurrency);
            }
            updateCurrencyDropdown(currentCurrency);
        });
    }

    function updateCurrencyDropdown(currency) {
        if (currency === "INR") {
            $('.transaction-currency').html(`
                    <option selected value="INR">INR</option>
                    <option value="USD">USD</option>
                `);
            $('.currency_usd').hide();
            $('.currency_inr').show();

            // Hide USD timer, show INR timer
            $('#discount-timer-usd').hide();
            $('#bc-discount-timer-usd').hide();
            $('#discount-timer-inr').show();
            $('#bc-discount-timer-inr').show();
        } else {
            $('.transaction-currency').html(`
                    <option value="INR">INR</option>
                    <option selected value="USD">USD</option>
                `);
            $('.currency_inr').hide();
            $('.currency_usd').show();

            //  Hide INR timer, show USD timer
            $('#discount-timer-inr').hide();
            $('#bc-discount-timer-inr').hide();
            $('#discount-timer-usd').show();
            $('#bc-discount-timer-usd').show();
        }
    }

    if (frappe.session && frappe.session.user && frappe.session.user !== "Guest") {
        frappe.xcall("leftwordlatest.web_api.cart.get_cart_currency_info").then(res => {
            const effectiveCurrency = res.currency || savedCurrency;
            sessionStorage.setItem("selectedCurrency", effectiveCurrency);
            if (effectiveCurrency == savedCurrency) {
                updateCurrencyDropdown(effectiveCurrency);
            }
        }).catch((error) => {
            console.error("Error checking draft quotation currency:", error);
        });
    }

    $('.transaction-currency').on('change', function (e) {
        const selectedCurrency = e.target.value;

        showCustomPopup(selectedCurrency, savedCurrency, function (confirmed) {
            if (confirmed) {
                sessionStorage.setItem("selectedCurrency", selectedCurrency);
                updateCurrencyDropdown(selectedCurrency);

            } else {
                $(e.target).val(sessionStorage.getItem("selectedCurrency") || "");
            }
        });
    });

    function showCustomPopup(selectedCurrency, callback) {
        isPopupOpen = true;

        const overlay = document.createElement("div");
        overlay.style.position = "fixed";
        overlay.style.top = "0";
        overlay.style.left = "0";
        overlay.style.width = "100%";
        overlay.style.height = "100%";
        overlay.style.background = "rgba(0, 0, 0, 0.5)";
        overlay.style.display = "flex";
        overlay.style.justifyContent = "center";
        overlay.style.alignItems = "center";
        overlay.style.zIndex = "1000";

        const popup = document.createElement("div");
        popup.style.background = "#fff";
        popup.style.padding = "20px";
        popup.style.borderRadius = "8px";
        popup.style.boxShadow = "0px 4px 6px rgba(0,0,0,0.1)";
        popup.style.textAlign = "center";
        popup.style.width = "300px";


        const message = document.createElement("p");
        message.innerText = `Do you want to change the currency?`;
        popup.appendChild(message);

        const buttonsDiv = document.createElement("div");
        buttonsDiv.style.marginTop = "15px";
        buttonsDiv.style.display = "flex";
        buttonsDiv.style.justifyContent = "space-around";

        const noButton = document.createElement("button");
        noButton.innerText = "No";
        noButton.style.padding = "8px 16px";
        noButton.style.background = "#dc3545";
        noButton.style.color = "white";
        noButton.style.border = "none";
        noButton.style.borderRadius = "4px";
        noButton.style.cursor = "pointer";
        noButton.onclick = function () {
            document.body.removeChild(overlay);
            isPopupOpen = false;
            callback(false);
        };


        const yesButton = document.createElement("button");
        yesButton.innerText = "Yes";
        yesButton.style.padding = "8px 16px";
        yesButton.style.background = "#28a745";
        yesButton.style.color = "white";
        yesButton.style.border = "none";
        yesButton.style.borderRadius = "4px";
        yesButton.style.cursor = "pointer";
        yesButton.onclick = function () {
            document.body.removeChild(overlay);
            isPopupOpen = false;

            frappe.xcall("leftwordlatest.web_api.cart.update_cart_count").then(data => {
                if (data > 0) {

                    const clearCartPopup = document.createElement("div");
                    clearCartPopup.style.position = "fixed";
                    clearCartPopup.style.top = "50%";
                    clearCartPopup.style.left = "50%";
                    clearCartPopup.style.transform = "translate(-50%, -50%)";
                    clearCartPopup.style.backgroundColor = "#fff";
                    clearCartPopup.style.padding = "20px";
                    clearCartPopup.style.borderRadius = "8px";
                    clearCartPopup.style.boxShadow = "0px 4px 10px rgba(0, 0, 0, 0.2)";
                    clearCartPopup.style.zIndex = "10000";
                    clearCartPopup.style.width = "300px";
                    clearCartPopup.style.textAlign = "center";

                    const clearCartMessage = document.createElement("p");
                    clearCartMessage.innerText = `You have items in your cart in ${currentCurrency}. Switching to ${selectedCurrency} will clear your cart. Do you want to proceed?`;
                    clearCartMessage.style.fontSize = "14px";
                    clearCartMessage.style.color = "#333";
                    clearCartMessage.style.marginBottom = "20px";
                    clearCartPopup.appendChild(clearCartMessage);

                    const clearButtonsDiv = document.createElement("div");
                    clearButtonsDiv.style.display = "flex";
                    clearButtonsDiv.style.justifyContent = "space-between";

                    const noButton = document.createElement("button");
                    noButton.innerText = "No";
                    noButton.style.padding = "10px 16px";
                    noButton.style.background = "#dc3545";
                    noButton.style.color = "white";
                    noButton.style.border = "none";
                    noButton.style.borderRadius = "5px";
                    noButton.style.cursor = "pointer";
                    noButton.style.flex = "1";
                    noButton.style.marginRight = "10px";
                    noButton.style.fontSize = "14px";
                    noButton.style.fontWeight = "bold";
                    noButton.onclick = function () {
                        document.body.removeChild(clearCartPopup);
                    };


                    const yesButtonClear = document.createElement("button");
                    yesButtonClear.innerText = "Clear Cart";
                    yesButtonClear.style.padding = "10px 16px";
                    yesButtonClear.style.background = "#28a745";
                    yesButtonClear.style.color = "white";
                    yesButtonClear.style.border = "none";
                    yesButtonClear.style.borderRadius = "5px";
                    yesButtonClear.style.cursor = "pointer";
                    yesButtonClear.style.flex = "1";
                    yesButtonClear.style.fontSize = "14px";
                    yesButtonClear.style.fontWeight = "bold";
                    yesButtonClear.style.position = "relative";
                    yesButtonClear.style.zIndex = "999";
                    yesButtonClear.onclick = function () {
                        sessionStorage.setItem("selectedCurrency", selectedCurrency);

                        frappe.xcall("leftwordlatest.web_api.cart.delete_last_draft_quotation").then((response) => {
                            $('#cart-count').text(0);
                            document.body.removeChild(clearCartPopup);
                            sessionStorage.setItem("selectedCurrency", selectedCurrency);
                            updateCurrencyDropdown(selectedCurrency);
                            location.reload();

                        }).catch((error) => {
                            console.error("Error clearing the cart: ", error);
                        });
                    };

                    clearButtonsDiv.appendChild(noButton);
                    clearButtonsDiv.appendChild(yesButtonClear);
                    clearCartPopup.appendChild(clearButtonsDiv);
                    document.body.appendChild(clearCartPopup);



                } else {
                    sessionStorage.setItem("selectedCurrency", selectedCurrency);
                    updateCurrencyDropdown(selectedCurrency);
                }
            }).catch((error) => {
                console.error("Error fetching cart count: ", error);
            });
        };

        buttonsDiv.appendChild(noButton);
        buttonsDiv.appendChild(yesButton);

        popup.appendChild(buttonsDiv);

        overlay.appendChild(popup);

        document.body.appendChild(overlay);

    }

    // function showCurrencyPopup(currency) {
    //     if (!isPopupOpen && !sessionStorage.getItem("currencyPopupSeen")) {
    //         isPopupOpen = true;

    //         const popupHtml = `
    //             <div id="currency-popup-overlay" style="
    //                 position: fixed;
    //                 top: 0; left: 0; right: 0; bottom: 0;
    //                 background: rgba(0, 0, 0, 0.5);
    //                 display: flex;
    //                 justify-content: center;
    //                 align-items: center;
    //                 z-index: 10000;
    //             ">
    //                 <div style="
    //                     background: white;
    //                     padding: 20px 30px;
    //                     border-radius: 8px;
    //                     text-align: center;
    //                     max-width: 400px;
    //                     box-shadow: 0 0 15px rgba(0,0,0,0.3);
    //                 ">
    //                     <h5 style="margin-bottom: 10px;">Currency Notice</h5>
    //                     <p>Your current currency is <strong style="color: red;">${currency}</strong>.</p>
    //                      <button id="currency-change-button" style="
    //                     padding: 8px 20px;
    //                     border: none;
    //                     background: red;
    //                     color: white;
    //                     border-radius: 5px;
    //                     cursor: pointer;
    //                 ">Change Currency</button>
    //                     <button id="currency-ok-button" style="
    //                         margin-top: 20px;
    //                         padding: 8px 20px;
    //                         border: none;
    //                         background:green;
    //                         color: white;
    //                         border-radius: 5px;
    //                         cursor: pointer;
    //                     ">OK</button>
    //                 </div>
    //             </div>
    //         `;

    //         $('body').append(popupHtml);

    //         $('#currency-ok-button').click(function () {
    //             sessionStorage.setItem("currencyPopupSeen", "1"); 
    //             $('#currency-popup-overlay').remove();
    //             location.reload();
    //             frappe.xcall("leftword.web_api.utils.update_transaction_currency", {
    //                 currency: currency
    //             }).then(() => {
    //                 sessionStorage.setItem("selectedCurrency", currency);
    //                 updateCurrencyDropdown(currency);
    //                 location.reload();
    //             }).catch((error) => {
    //                 console.error("Error updating currency: ", error);
    //             });
    //         });

    // $('#currency-change-button').click(function () {
    //     const newCurrency = (currency === "INR") ? "USD" : "INR";

    //     const proceedWithCurrencyChange = () => {
    //         frappe.xcall("leftword.web_api.utils.update_transaction_currency", {
    //             currency: newCurrency
    //         }).then(() => {
    //             sessionStorage.setItem("selectedCurrency", newCurrency);
    //             sessionStorage.setItem("currencyPopupSeen", "1");
    //             updateCurrencyDropdown(newCurrency);
    //             $('#currency-popup-overlay').remove();
    //             location.reload();
    //         }).catch((error) => {
    //             console.error("Error updating currency:", error);
    //         });
    //     };

    //     if (parseInt($('#cart-count').text()) === 0) {

    //         proceedWithCurrencyChange();
    //     } else {

    //         frappe.xcall("leftword.web_api.cart.delete_last_draft_quotation")
    //             .then(() => {
    //                 proceedWithCurrencyChange();
    //             }).catch((error) => {
    //                 console.error("Error deleting cart:", error);
    //             });
    //     }
    // });



    //     }
    // }
    // $(document).ready(function () {
    // sessionStorage.setItem("userTimeZon")
    // const currency = sessionStorage.getItem("selectedCurrency") || "INR";
    // const currency = document.getElementsByClassName("transaction-currency")[0].value || "INR";


    // if (!sessionStorage.getItem("currencyUpdatedOnLoad")) {
    //     sessionStorage.setItem("currencyUpdatedOnLoad", "1");
    //     sessionStorage.removeItem("userSelectedCurrency");


    //     frappe.xcall("leftword.web_api.cart.get_cart_currency_info").then(res => {
    //         const effectiveCurrency = res.currency || currency;

    //         frappe.xcall("leftword.web_api.utils.update_transaction_currency", {
    //             currency: effectiveCurrency
    //         }).then(() => {
    //             sessionStorage.setItem("selectedCurrency", effectiveCurrency);
    //             updateCurrencyDropdown(effectiveCurrency);
    //             console.log("Transaction currency updated based on draft quotation or fallback.");
    //         }).catch((error) => {
    //             console.error("Error updating currency on page load:", error);
    //         });
    //     }).catch((error) => {
    //         console.error("Error checking draft quotation currency:", error);
    //     });
    // }


    // if (frappe.session && frappe.session.user && frappe.session.user !== "Guest") {
    //     const currentUser = frappe.session.user;
    //     const previousUser = sessionStorage.getItem("previousSessionUser");

    //     if (!previousUser || previousUser === "Guest") {
    //         sessionStorage.setItem("previousSessionUser", currentUser);
    //         sessionStorage.removeItem("userSelectedCurrency");

    //         frappe.xcall("leftword.web_api.cart.get_cart_currency_info").then(res => {
    //             const effectiveCurrency = res.currency || currency;

    //             frappe.xcall("leftword.web_api.utils.update_transaction_currency", {
    //                 currency: effectiveCurrency
    //             }).then(() => {
    //                 sessionStorage.setItem("selectedCurrency", effectiveCurrency);
    //                 updateCurrencyDropdown(effectiveCurrency);
    //                 console.log("Currency updated after user login using draft quotation.");
    //             }).catch((error) => {
    //                 console.error("Error updating currency on login:", error);
    //             });
    //         }).catch((error) => {
    //             console.error("Error getting currency on login:", error);
    //         });
    //     } else {
    //         sessionStorage.setItem("previousSessionUser", currentUser);
    //     }
    // } else {
    //     sessionStorage.setItem("previousSessionUser", "Guest");
    // }

    // const savedCurrency = document.getElementsByClassName("transaction-currency")[0].value || "INR";

    // $('.transaction-currency').on('change', function (e) {
    //     const selectedCurrency = e.target.value;
    //     console.log("Selected currency:", selectedCurrency);

    //     showCustomPopup(selectedCurrency, savedCurrency, function (confirmed) {
    //         if (confirmed) {
    //             // sessionStorage.setItem("userSelectedCurrency", "1");
    //             frappe.xcall("leftwordlatest.utils.update_transaction_currency", {
    //                 currency: selectedCurrency
    //             }).then(() => {
    //                 // sessionStorage.setItem("selectedCurrency", selectedCurrency);
    //                 updateCurrencyDropdown(selectedCurrency);
    //             });
    //         } else {
    //             $(e.target).val(selectedCurrency || "");
    //         }
    //     });
    // });

    // setInterval(() => {
    //     let newTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    //     let hasUserSelectedCurrency = sessionStorage.getItem("userSelectedCurrency") === "1";
    //     if (sessionStorage.getItem("userTimeZone") !== newTimeZone && !hasUserSelectedCurrency && !isPopupOpen) {
    //         sessionStorage.setItem("userTimeZone", newTimeZone);
    //         let newCurrency = getTimeZoneBasedCurrency();
    //         sessionStorage.setItem("selectedCurrency", newCurrency);

    //         sessionStorage.removeItem("currencyUpdatedOnLoad");

    //         updateCurrencyDropdown(newCurrency);
    //         location.reload();
    //     }
    // }, 2000);
    // });




    // function showCustomPopup(selectedCurrency, callback) {
    //     isPopupOpen = true;

    //     const overlay = document.createElement("div");
    //     overlay.style.position = "fixed";
    //     overlay.style.top = "0";
    //     overlay.style.left = "0";
    //     overlay.style.width = "100%";
    //     overlay.style.height = "100%";
    //     overlay.style.background = "rgba(0, 0, 0, 0.5)";
    //     overlay.style.display = "flex";
    //     overlay.style.justifyContent = "center";
    //     overlay.style.alignItems = "center";
    //     overlay.style.zIndex = "1000";

    //     const popup = document.createElement("div");
    //     popup.style.background = "#fff";
    //     popup.style.padding = "20px";
    //     popup.style.borderRadius = "8px";
    //     popup.style.boxShadow = "0px 4px 6px rgba(0,0,0,0.1)";
    //     popup.style.textAlign = "center";
    //     popup.style.width = "300px";


    //     const message = document.createElement("p");
    //     message.innerText = `Do you want to change the currency?`;
    //     popup.appendChild(message);

    //     const buttonsDiv = document.createElement("div");
    //     buttonsDiv.style.marginTop = "15px";
    //     buttonsDiv.style.display = "flex";
    //     buttonsDiv.style.justifyContent = "space-around";

    //     const noButton = document.createElement("button");
    //     noButton.innerText = "No";
    //     noButton.style.padding = "8px 16px";
    //     noButton.style.background = "#dc3545";
    //     noButton.style.color = "white";
    //     noButton.style.border = "none";
    //     noButton.style.borderRadius = "4px";
    //     noButton.style.cursor = "pointer";
    //     noButton.onclick = function () {
    //         document.body.removeChild(overlay);
    //         isPopupOpen = false;
    //         callback(false);
    //     };


    //     const yesButton = document.createElement("button");
    //     yesButton.innerText = "Yes";
    //     yesButton.style.padding = "8px 16px";
    //     yesButton.style.background = "#28a745";
    //     yesButton.style.color = "white";
    //     yesButton.style.border = "none";
    //     yesButton.style.borderRadius = "4px";
    //     yesButton.style.cursor = "pointer";
    //     yesButton.onclick = function () {
    //         document.body.removeChild(overlay);
    //         isPopupOpen = false;

    //         frappe.xcall("leftword.web_api.cart.update_cart_count").then(data => {
    //             if (data > 0) {

    //                 const clearCartPopup = document.createElement("div");
    //                 clearCartPopup.style.position = "fixed";
    //                 clearCartPopup.style.top = "50%";
    //                 clearCartPopup.style.left = "50%";
    //                 clearCartPopup.style.transform = "translate(-50%, -50%)";
    //                 clearCartPopup.style.backgroundColor = "#fff";
    //                 clearCartPopup.style.padding = "20px";
    //                 clearCartPopup.style.borderRadius = "8px";
    //                 clearCartPopup.style.boxShadow = "0px 4px 10px rgba(0, 0, 0, 0.2)";
    //                 clearCartPopup.style.zIndex = "10000";
    //                 clearCartPopup.style.width = "300px";
    //                 clearCartPopup.style.textAlign = "center";

    //                 const clearCartMessage = document.createElement("p");
    //                 clearCartMessage.innerText = `You have items in your cart in ${currentCurrency}. Switching to ${selectedCurrency} will clear your cart. Do you want to proceed?`;
    //                 clearCartMessage.style.fontSize = "14px";
    //                 clearCartMessage.style.color = "#333";
    //                 clearCartMessage.style.marginBottom = "20px";
    //                 clearCartPopup.appendChild(clearCartMessage);

    //                 const clearButtonsDiv = document.createElement("div");
    //                 clearButtonsDiv.style.display = "flex";
    //                 clearButtonsDiv.style.justifyContent = "space-between";

    //                 const noButton = document.createElement("button");
    //                 noButton.innerText = "No";
    //                 noButton.style.padding = "10px 16px";
    //                 noButton.style.background = "#dc3545";
    //                 noButton.style.color = "white";
    //                 noButton.style.border = "none";
    //                 noButton.style.borderRadius = "5px";
    //                 noButton.style.cursor = "pointer";
    //                 noButton.style.flex = "1";
    //                 noButton.style.marginRight = "10px";
    //                 noButton.style.fontSize = "14px";
    //                 noButton.style.fontWeight = "bold";
    //                 noButton.onclick = function () {
    //                     document.body.removeChild(clearCartPopup);
    //                 };


    //                 const yesButtonClear = document.createElement("button");
    //                 yesButtonClear.innerText = "Clear Cart";
    //                 yesButtonClear.style.padding = "10px 16px";
    //                 yesButtonClear.style.background = "#28a745";
    //                 yesButtonClear.style.color = "white";
    //                 yesButtonClear.style.border = "none";
    //                 yesButtonClear.style.borderRadius = "5px";
    //                 yesButtonClear.style.cursor = "pointer";
    //                 yesButtonClear.style.flex = "1";
    //                 yesButtonClear.style.fontSize = "14px";
    //                 yesButtonClear.style.fontWeight = "bold";
    //                 yesButtonClear.style.position = "relative";
    //                 yesButtonClear.style.zIndex = "999";
    //                 yesButtonClear.onclick = function () {
    //                     sessionStorage.setItem("selectedCurrency", selectedCurrency);

    //                     frappe.xcall("leftword.web_api.cart.delete_last_draft_quotation").then((response) => {
    //                         console.log(response.message);
    //                         $('#cart-count').text(0);
    //                         document.body.removeChild(clearCartPopup);
    //                         sessionStorage.setItem("selectedCurrency", selectedCurrency);
    //                         updateCurrencyDropdown(selectedCurrency);

    //                     }).catch((error) => {
    //                         console.error("Error clearing the cart: ", error);
    //                     });
    //                 };

    //                 clearButtonsDiv.appendChild(noButton);
    //                 clearButtonsDiv.appendChild(yesButtonClear);
    //                 clearCartPopup.appendChild(clearButtonsDiv);
    //                 document.body.appendChild(clearCartPopup);



    //             } else {
    //                 sessionStorage.setItem("selectedCurrency", selectedCurrency);
    //                 updateCurrencyDropdown(selectedCurrency);
    //             }
    //         }).catch((error) => {
    //             console.error("Error fetching cart count: ", error);
    //         });
    //     };

    //     buttonsDiv.appendChild(noButton);
    //     buttonsDiv.appendChild(yesButton);

    //     popup.appendChild(buttonsDiv);

    //     overlay.appendChild(popup);

    //     document.body.appendChild(overlay);

    // }

    // const currentSavedCurrency = document.getElementsByClassName("transaction-currency")[0].value || "INR";

    // $('.transaction-currency').on('change', function (e) {
    //     const selectedCurrency = e.target.value;

    //     showCustomPopup(selectedCurrency, function (confirmed) {
    //         if (confirmed) {
    //             frappe.xcall("leftwordlatest.utils.update_transaction_currency", {
    //                 currency: selectedCurrency
    //             }).then(() => {
    //                 sessionStorage.setItem("selectedCurrency", selectedCurrency);
    //                 updateCurrencyDropdown(selectedCurrency);
    //             });
    //         } else {
    //             $(e.target).val(currentSavedCurrency || "");
    //         }
    //     });
    // });

    // setInterval(() => {
    //     let newTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    //     if (sessionStorage.getItem("userTimeZone") !== newTimeZone && !isPopupOpen) {
    //         sessionStorage.setItem("userTimeZone", newTimeZone);
    //         let newCurrency = getTimeZoneBasedCurrency();
    //         sessionStorage.setItem("selectedCurrency", newCurrency);
    //         updateCurrencyDropdown(newCurrency);
    //         location.reload();
    //     }
    // }, 2000);
    // });





    $('.leftword_search_button').on('click', function (e) {
        e.preventDefault()
        window.location.href = `/all_products?search_key=${$('.leftword_search')[0].value}`;
    });
    const searchParams = new URLSearchParams(window.location.search);
    if (searchParams.has('search_key')) {
        $('.leftword_search')[0].value = searchParams.get('search_key')
    };

    ebooks_base_filters();
    hindi_base_filters();
    author_base_filters();
    category_base_filters();




    $('.leftword_search_button1').on('click', function (e) {
        e.preventDefault()
        window.location.href = `/all_products?search_key=${$('.leftword_search1')[0].value}`;
    });
    const searchParams1 = new URLSearchParams(window.location.search);
    if (searchParams1.has('search_key')) {
        $('.leftword_search1')[0].value = searchParams1.get('search_key')
    };

    ebooks_base_filters();
    hindi_base_filters();
    author_base_filters();
    category_base_filters();
});



function moveToNext(currentInput, nextInputId) {
    if (currentInput.value.length >= currentInput.maxLength) {
        const nextInput = document.getElementById(nextInputId);
        if (nextInput) {
            nextInput.focus();
        }
    }
}

document.querySelectorAll('input').forEach((input, index) => {
    input.addEventListener('keydown', function (event) {
        if (event.key === 'Backspace' && this.value === '') {
            const prevInput = index > 0 ? document.querySelectorAll('input')[index - 1] : null;
            if (prevInput) {
                prevInput.focus();
            }
        }
    });
});


var ebooks_base_filters = function () {
    $('.done-btn').on('click', function (e) {
        e.preventDefault();
        let ebooks = document.getElementsByClassName('ebooks_check');
        let checked_ebooks = []
        for (let ebook of ebooks) {
            if (ebook.checked) {
                checked_ebooks.push(ebook.value);
            }
        }
        if (checked_ebooks.length > 0) {
            window.location.href = `/e_books?filter_args=${checked_ebooks}`
        }
    })
}


var hindi_base_filters = function () {
    $('.done-btn').on('click', function (e) {
        e.preventDefault();
        let hindiBooks = document.getElementsByClassName('hindi_check');
        let checkedHindiBooks = []
        for (let hindiBook of hindiBooks) {
            if (hindiBook.checked) {
                checkedHindiBooks.push(hindiBook.value);
            }
        }
        if (checkedHindiBooks.length > 0) {
            window.location.href = `/hindi?filter_args=${checkedHindiBooks}`
        }
    })
}

var author_base_filters = function () {
    $('.done-btn').on('click', function (e) {
        e.preventDefault();

        let authors = document.getElementsByClassName('author_check');
        let checkedAuthors = [];

        for (let author of authors) {
            if (author.checked) {
                checkedAuthors.push(author.value);
            }
        }


        if (checkedAuthors.length > 0) {
            window.location.href = `/author?filter_args=${checkedAuthors.join(',')}`;
        }
    });
}




var category_base_filters = function () {
    $('.done-btn').on('click', function (e) {
        e.preventDefault();
        let categories = document.getElementsByClassName('categories_check');
        let checked_categories = []
        for (let category of categories) {
            if (category.checked) {
                checked_categories.push(category.value);
            }
        }
        if (checked_categories.length > 0) {
            window.location.href = `/categories?filter_args=${checked_categories}`
        }
    })

    $('.leftword_search').on('keydown', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            redirectToSearch();
        }
    });


    $('.leftword_search_button').on('click', function (e) {
        e.preventDefault();
        redirectToSearch();
    });


    function redirectToSearch() {
        const searchValue = $('.leftword_search').val().trim();
        if (searchValue) {

            window.location.href = `/all_products?search_key=${encodeURIComponent(searchValue)}`;
        } else {
            alert('Please enter a search term');
        }
    }

    const searchParams = new URLSearchParams(window.location.search);
    if (searchParams.has('search_key')) {
        $('.leftword_search').val(searchParams.get('search_key'));
    }


    window.addEventListener('pageshow', function (event) {
        if (event.persisted || performance.getEntriesByType('navigation')[0]?.type === 'back_forward') {

            $('.leftword_search').refresh();


            window.location.reload();
        }
    });



}
