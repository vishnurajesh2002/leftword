frappe.call({
    method: "leftwordlatest.www.otp_signup.validate_otp",  
    args: {
        contact: user_contact, 
        otp: entered_otp,  
        user: frappe.session.user  
    },
    callback: function(response) {
        if (response.message.success) {
            frappe.msgprint(response.message.message);
            setTimeout(function() {
                location.reload();  
            }, 1000);  
        } else {
            frappe.msgprint({
                title: __("Error"),
                message: response.message.message,
                indicator: "red"
            });
        }
    }
});
