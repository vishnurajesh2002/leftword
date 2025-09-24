function redirectToPayment(button) {
    const form = document.createElement("form");
    form.method = "POST";
    form.action = "/ccavenue_payment";

    const fields = {
        "token_id": button.getAttribute("data-token"),
        "customer": button.getAttribute("data-customer-name"),
        "invoice_id": button.getAttribute("data-invoice"),
        "order_id": button.getAttribute("data-order-id"),
        "currency": button.getAttribute("data-currency"),
        "amount": button.getAttribute("data-amount"),
        "language": "EN",
        "phone": button.getAttribute("data-phone"),
        "street": button.getAttribute("data-street"),
        "town": button.getAttribute("data-town"),
        "state": button.getAttribute("data-state"),
        "zipcode": button.getAttribute("data-zipcode"),
        "street1": button.getAttribute("data-street1"), 
        "town1": button.getAttribute("data-town1"), 
        "state1": button.getAttribute("data-state1"), 
        "zipcode1": button.getAttribute("data-zipcode1"), 
        "phone1": button.getAttribute("data-phone1")

    };

    

    for (const key in fields) {
        if (fields[key]) {
            const input = document.createElement("input");
            input.type = "hidden";
            input.name = key;
            input.value = fields[key];
            form.appendChild(input);
        }
    }

    document.body.appendChild(form);
    form.submit();
}
