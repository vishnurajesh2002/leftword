// $("#btnMembership").click(function() {
//     const button = $(this);

//     if (button.hasClass('already-member')) {
//         button.text("Already Member");
//         return;
//     }

//     var currency = $('.transaction-currency').val();
//     frappe.xcall('leftwordlatest.create_member_membership_sales_invoice.create_sales_invoice_first', {
//         "customer_name": $('#customer-name').text(),
//         "customer_id": $('#customer-id').text(),
//         "membership_type": "Yearly Membership",
//         "year": 1,
//         "email_id": frappe.session.user,
//         "currency" : currency,
//     }).then(function(invoice) {
//         if (invoice === 'Member already exists') {
//             frappe.msgprint('Member already exists');
//             setTimeout(() => {
//                 window.location.href = '/start_payment/?order=' + invoice_name;
//             },2000);
//         } else if (invoice_name === 'Invalid membership type') {
//             frappe.msgprint('Invalid membership type');
//         }
//         else if(invoice_name === 'Address not found'){
//             frappe.msgprint('Address not found');
//             setTimeout(() => {
//                 window.location.href = '/my_addresses';
//             }, 2000);
//         } else {
//             $("input[type='text']").prop('readonly', true);
//             window.location.href = '/start_payment/?order=' + invoice_name;
//         }
//     }).catch(err => {
//         frappe.msgprint('An error occurred: ' + err.message);
//     });

// });


$("#btnMembership").click(function() {
    const button = $(this);  
    var currency = $('.transaction-currency').val();  

    if (button.hasClass('already-member')) {
        button.text("Already Member");
        return;
    }

    // Lock input
    $("input[type='text']").prop('readonly', true);

    frappe.call({
        method: "leftwordlatest.create_member_membership_sales_invoice.create_sales_invoice_first",
        args: {
            "customer_name": $('#customer-name').text(),
            "customer_id": $('#customer-id').text(),
            "membership_type": "Yearly Membership",
            "year": 1,
            "email_id": frappe.session.user,
            "currency": currency
        },
        callback: function(r) {
            if (r.message) {
                let res = r.message;

                if (res.status === "invalid") {
                    frappe.msgprint(res.reason);
                    if (res.reason === "Address not found") {
                        setTimeout(() => {
                            window.location.href = '/my_addresses';
                        }, 2000);
                    }
                    return;
                }

                if (res.status === "exists") {
                    frappe.msgprint("Unpaid Invoice Exists: " + res.invoice_name);
                    window.location.href = '/start_payment/?order=' + res.invoice_name;
                    return;
                }

                if (res.status === "created") {
                    frappe.msgprint("Sales Invoice Created: " + res.invoice_name);
                    window.location.href = '/start_payment/?order=' + res.invoice_name;
                    return;
                }

                if (res.status === "error") {
                    frappe.msgprint("Error: " + res.message);
                }
            }
        }
    });
});



