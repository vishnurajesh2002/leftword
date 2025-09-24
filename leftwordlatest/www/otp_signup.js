// Function to handle the OTP submission for signup
function sendSignupOTP() {
    const submitButton = document.querySelector('button[onclick="sendSignupOTP()"]');
    if (submitButton) {
        submitButton.disabled = true;
    }

    const contact = document.getElementById("inputContact").value.trim();
    // const additionalEmail = document.getElementById("inputEmail").value.trim();
    const emailField = document.getElementById("inputEmail");
    const additionalEmail = emailField.value.trim();
    const contactMessageDiv = document.getElementById("contactMessage");

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const phoneRegex = /^\d{10}$/;

    // Validate primary contact
    if (!contact || (!emailRegex.test(contact) && !phoneRegex.test(contact))) {
        contactMessageDiv.innerText = "Please enter a valid email or 10-digit phone number.";
        contactMessageDiv.classList.remove("alert-success");
        contactMessageDiv.classList.add("alert-danger");
        contactMessageDiv.style.display = "block";
        if (submitButton) submitButton.disabled = false;
        return;
    }

    // If phone is entered, validate additional email
    if (phoneRegex.test(contact)) {
        emailField.style.display = "block";

        if (!additionalEmail || !emailRegex.test(additionalEmail)) {
            contactMessageDiv.innerText = "Please enter a valid email address.";
            contactMessageDiv.classList.remove("alert-success");
            contactMessageDiv.classList.add("alert-danger");
            contactMessageDiv.style.display = "block";
            if (submitButton) submitButton.disabled = false;
            return;
        }
    } else {
        emailField.style.display = "none";
    }

    // Frappe call with both contact and additional_email
    frappe.call({
        method: "leftwordlatest.www.otp_signup.handle_otp_submission",
        args: {
            contact: contact,
            additional_email: additionalEmail || null
        },
        callback: function (response) {
            if (response.message.success === true) {
                contactMessageDiv.innerText = response.message.message;
                contactMessageDiv.classList.remove("alert-danger");
                contactMessageDiv.classList.add("alert-success");
                contactMessageDiv.style.display = "block";

                // Dynamically update the OTP message based on input type
                const otpMessage = document.getElementById("otpMessage");
                if (otpMessage) {
                    if (phoneRegex.test(contact)) {
                        otpMessage.innerText = "We have sent you a One-Time Password (OTP) on your mobile number.";
                    } else if (emailRegex.test(contact)) {
                        otpMessage.innerText = "We have sent you a One-Time Password (OTP) on your email address.";
                    }
                }

                //Hide current modal and show OTP verification modal
                const contactModal = bootstrap.Modal.getInstance(document.getElementById("lwsignUpOtp"));
                contactModal.hide();
                new bootstrap.Modal(document.getElementById("lwsignupverifyOtp")).show();

                showSuccessMessage("OTP sent successfully!");
            } else {
                contactMessageDiv.innerText = response.message.message;
                contactMessageDiv.classList.remove("alert-success");
                contactMessageDiv.classList.add("alert-danger");
                contactMessageDiv.style.display = "block";

                setTimeout(() => {
                    contactMessageDiv.style.display = "none";
                }, 5000);
            }
            if (submitButton) submitButton.disabled = false;
        },
        error: function () {
            if (submitButton) submitButton.disabled = false;
        }
    });
}

function showSuccessMessage(message) {
    const modalBody = $('#lwsignupverifyOtp .modal-body1');
    const messageDiv = $('<div class="success-message"></div>').text(message);
    modalBody.append(messageDiv);
    messageDiv.css({
        'position': 'absolute',
        'top': '20px',
        'right': '20px',
        'background-color': '#28a745',
        'color': '#ffffff',
        'padding': '5px 15px',
        'border-radius': '3px',
        'font-size': '14px',
        'box-shadow': '0 2px 5px rgba(0,0,0,0.2)',
        'z-index': '1050'
    });
    setTimeout(() => {
        messageDiv.fadeOut(300, () => {
            messageDiv.remove();
        });
    }, 3000);
}

function verifySignupOTP() {
    const contact = document.getElementById("inputContact").value.trim();
    const email = document.getElementById("inputEmail").value.trim();
    const otp = document.getElementById("input1").value +
        document.getElementById("input2").value +
        document.getElementById("input3").value +
        document.getElementById("input4").value;
    const fullName = document.getElementById("inputName").value.trim();
    const otpMessageDiv = document.getElementById("otpMessage");

    if (otp.length !== 4) {
        otpMessageDiv.innerText = "Please enter a valid 4-digit OTP.";
        otpMessageDiv.classList.add("alert-danger");
        otpMessageDiv.style.display = "block";
        return;
    }

    if (!fullName) {
        otpMessageDiv.innerText = "Please enter your full name.";
        otpMessageDiv.classList.add("alert-danger");
        otpMessageDiv.style.display = "block";
        return;
    }

    frappe.call({
        method: "leftwordlatest.www.otp_signup.verify_signup_otp",
        args: { contact: contact, otp: otp, full_name: fullName, email: email },
        callback: function (response) {
            if (response.message.success) {
                otpMessageDiv.innerText = response.message.message;
                otpMessageDiv.classList.add("alert-success");
                otpMessageDiv.style.display = "block";
                setTimeout(() => {
                    $('#lwsignupverifyOtp').modal('hide');
                    window.location.href = '/leftword_home';
                }, 1000);
            } else {
                otpMessageDiv.innerText = response.message.message;
                otpMessageDiv.classList.add("alert-danger");
                otpMessageDiv.style.display = "block";
            }
        }
    });
}


setupOTPInputFields();
// Setup function for OTP input fields to navigate automatically
function setupOTPInputFields() {
    const inputs = document.querySelectorAll("#input1, #input2, #input3, #input4");

    inputs.forEach((input, index) => {
        input.addEventListener("input", () => {
            if (input.value.length === 1 && index < inputs.length - 1) {
                inputs[index + 1].focus();
            }
        });

        input.addEventListener("keydown", (event) => {
            if (event.key === "Backspace" && input.value.length === 0 && index > 0) {
                inputs[index - 1].focus();
            }
        });
    });
}
setupOTPInputFields();

// From sign up popup to sign in
document.addEventListener("DOMContentLoaded", function () {
    const signInLinks = document.querySelectorAll('a[href="#"][id="openSignInLink"]');
    signInLinks.forEach(function (link) {
        link.addEventListener("click", function (event) {
            event.preventDefault();
            const currentModal = link.closest(".modal");
            const currentModalInstance = bootstrap.Modal.getInstance(currentModal);
            if (currentModalInstance) {
                currentModalInstance.hide();
            }
            new bootstrap.Modal(document.getElementById("lwsignIn")).show();
        });
    });
});

// Clear the input field
function refreshPage() {
    document.getElementById('inputContact').value = '';
    const contactMessage = document.getElementById('contactMessage');
    contactMessage.style.display = 'none';
    contactMessage.textContent = '';
    document.getElementById('input1').value = '';
    document.getElementById('input2').value = '';
    document.getElementById('input3').value = '';
    document.getElementById('input4').value = '';
    const otpMessage = document.getElementById('otpMessage');
    otpMessage.style.display = 'none';
    otpMessage.textContent = '';
    document.getElementById('inputName').value = '';
    document.getElementById('inputEmail').value = '';
    document.getElementById('inputContact').focus();
    location.reload();
}

//resend otp for signin
function resendOtp() {
    let emailOrPhone = '';

    if (document.getElementById('lwsigInOtp')?.classList.contains('show')) {
        emailOrPhone = document.getElementById('otpEmailPhone').value.trim();
    } else if (document.getElementById('lwforgotpass')?.classList.contains('show')) {
        emailOrPhone = document.getElementById('forgotEmail').value.trim();
    }

    if (emailOrPhone) {
        frappe.call({
            method: "leftwordlatest.web_api.user.send_otp_email",
            args: {
                email: emailOrPhone
            },
            callback: function (response) {
                if (response.message) {
                    showSuccessMessageFrg('#lwsignInOtpVerificationEmail', 'OTP sent successfully!');
                    showSuccessMessageFrg('#lwotpemail', 'OTP sent successfully!');    
                }
            },
        });
    }
}

//resend otp for signup
function resendSignupOtp() {
    const contact = document.getElementById("inputContact").value.trim();

    if (!contact) {
        showErrorMessage("Please enter your email or phone number.");
        return;
    }

    frappe.call({
        method: "leftwordlatest.www.otp_signup.handle_otp_submission",
        args: { contact: contact },
        callback: function (response) {
            if (response.message.success) {
                showSuccessMessage("OTP resent successfully!");
            } else {
                showErrorMessage(response.message.message);
            }
        },
        error: function () {
            showErrorMessage("Something went wrong. Please try again.");
        }
    });
}

function showSuccessMessageFrg(modalId, message) {
    const modalBody = $(`${modalId} .modal-body1`);
    const messageDiv = $('<div class="success-message"></div>').text(message);
    modalBody.append(messageDiv);
    messageDiv.css({
        'position': 'absolute',
        'top': '20px',
        'right': '20px',
        'background-color': '#28a745',
        'color': '#ffffff',
        'padding': '5px 15px',
        'border-radius': '3px',
        'font-size': '14px',
        'box-shadow': '0 2px 5px rgba(0,0,0,0.2)',
        'z-index': '1050'
    });
    setTimeout(() => {
        messageDiv.fadeOut(300, () => {
            messageDiv.remove();
        });
    }, 3000);
}
