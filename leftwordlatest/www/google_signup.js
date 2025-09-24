function googlesignUp() { 

    frappe.call({
        method: "leftwordlatest.www.google_signup.get_custom_login_context",
        callback: function(response) {
            if (response.message) {
                const context = response.message;
                const googleProvider = context.provider_logins.find(
                    provider => provider.provider_name.toLowerCase() === "google"
                );

                if (googleProvider && googleProvider.auth_url) {
                    window.location.href = googleProvider.auth_url;
                } else {
                    console.log("Google login provider not found.");
                }
            } else {
                console.log("No message received from server.");
            }
        }
    });
}