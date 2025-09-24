// login.js
// don't remove this line (used in test)

window.disable_signup = {{ disable_signup and "true" or "false" }};

window.login = {};

window.verify = {};
frappe.ready(function () {
	if (frappe.session.user != 'Guest') {
		window.location.href = '/leftword_home';
	}
})

login.bind_events = function () {
	$(window).on("hashchange", function () {
		login.route();
	});


	$(".form-login").on("click", function (event) {
		event.preventDefault();
		var args = {};
		args.cmd = "login";
		args.usr = frappe.utils.xss_sanitise(($("#login_email").val() || "").trim());
		args.pwd = $("#login_password").val();
		args.device = "desktop";
		if (!args.usr || !args.pwd) {
			login.set_status('{{ _("Both login and password required") }}');
			return false;
		}
		login.call(args);
		return false;
	});

	$(".form-signup").on("click", function (event) {
		event.preventDefault();
		var args = {};
		args.cmd = "frappe.core.doctype.user.user.sign_up";
		args.email = ($("#signup_email").val() || "").trim();
		args.redirect_to = frappe.utils.sanitise_redirect(frappe.utils.get_url_arg("redirect-to"));
		args.full_name = frappe.utils.xss_sanitise(($("#signup_fullname").val() || $("#signup_email").val()).trim());
		if (!args.email || !validate_email(args.email) || !args.full_name) {
			login.set_status('{{ _("Valid email and name required") }}', 'red');
			return false;
		}
		login.set_status('{{ _("Verifying...") }}', 'blue');

		login.call(args).then((response) => {
			if (response.message[0] == '0') {
				var signup_button = document.getElementById("signup_button")
				signup_button.textContent = response.message[1]

			} else if (response.message[0] == '2') {

				var signup_button = document.getElementById("signup_button")
				signup_button.textContent = 'Registered ' + response.message[1]

			} else if (response.message[0] == '1') {

				var signup_button = document.getElementById("signup_button")
				signup_button.textContent = 'Registered ' + response.message[1]

			} else {
				var signup_button = document.getElementById("signup_button")
				signup_button.textContent = response.message[1]
			}

		})
		return false;
	});

	// $(".form-forgot").on("click", function (event) {
	// 	event.preventDefault();
	// 	var args = {};
	// 	args.cmd = "frappe.core.doctype.user.user.reset_password";
	// 	args.user = ($("#forgot_email").val() || "").trim();
	// 	if (!args.user) {
	// 		login.set_status('{{ _("Valid Login id required.") }}', 'red');
	// 		return false;
	// 	}
	// 	login.call(args);
	// 	return false;
	// });

	$(".form-login-with-email-link").on("submit", function (event) {
		event.preventDefault();
		var args = {};
		args.cmd = "frappe.www.login.send_login_link";
		args.email = ($("#login_with_email_link_email").val() || "").trim();
		if (!args.email) {
			login.set_status('{{ _("Valid Login id required.") }}', 'red');
			return false;
		}
		login.call(args).then(() => {
			login.set_status('{{ _("Login link sent to your email") }}', 'blue');
			$("#login_with_email_link_email").val("");
		}).catch(() => {
			login.set_status('{{ _("Send login link") }}', 'blue');
		});

		return false;
	});

	$(".toggle-password").click(function () {
		var input = $($(this).attr("toggle"));
		$(".password-icon path").toggleClass("password-visible");
		if (input.attr("type") == "password") {
			input.attr("type", "text");
			$(this).text('{{ _("Hide") }}')
		} else {
			input.attr("type", "password");
			$(this).text('{{ _("Show") }}')
		}
	});

	{% if ldap_settings and ldap_settings.enabled %}
	$(".btn-ldap-login").on("click", function () {
		var args = {};
		args.cmd = "{{ ldap_settings.method }}";
		args.usr = ($("#login_email").val() || "").trim();
		args.pwd = $("#login_password").val();
		args.device = "desktop";
		if (!args.usr || !args.pwd) {
			login.set_status('{{ _("Both login and password required") }}', 'red');
			return false;
		}
		login.call(args);
		return false;
	});
	{% endif %}
}


login.route = function () {
	var route = window.location.hash.slice(1);
	if (!route) route = "login";
	route = route.replaceAll("-", "_");
	login[route]();
}

login.reset_sections = function (hide) {
	if (hide || hide === undefined) {
		$("section.for-login").toggle(false);
		$("section.for-email-login").toggle(false);
		$("section.for-forgot").toggle(false);
		$("section.for-login-with-email-link").toggle(false);
		$("section.for-signup").toggle(false);
	}
	$('section:not(.signup-disabled) .indicator').each(function () {
		$(this).removeClass().addClass('indicator').addClass('blue')
			.text($(this).attr('data-text'));
	});
}

login.login = function () {
	login.reset_sections();
	$(".for-login").toggle(true);
}

login.email = function () {
	login.reset_sections();
	$(".for-email-login").toggle(true);
	$("#login_email").focus();
}

login.steptwo = function () {
	login.reset_sections();
	$(".for-login").toggle(true);
	$("#login_email").focus();
}

login.forgot = function () {
	login.reset_sections();
	if ($("#login_email").val()) {
		$("#forgot_email").val($("#login_email").val());
	}
	$(".for-forgot").toggle(true);
	$("#forgot_email").focus();
}

login.login_with_email_link = function () {
	login.reset_sections();
	if ($("#login_email").val()) {
		$("#login_with_email_link_email").val($("#login_email").val());
	}
	$(".for-login-with-email-link").toggle(true);
	$("#login_with_email_link_email").focus();
}

login.signup = function () {
	login.reset_sections();
	$(".for-signup").toggle(true);
	$("#signup_fullname").focus();
}


// Login
login.call = function (args, callback) {
	return frappe.call({
		type: "POST",
		args: args,
		callback: callback,
		freeze: true,
		statusCode: login.login_handlers
	});
}

login.set_status = function (message, color) {
	if (['Verifying...', 'Already Registered', 'Registered', 'Valid email and password required'].includes(message)) {
		$('#signup_button').text(message)
	} else if(['Valid Login id required.'].includes(message)){
		$('#forgot_button').text(message)
	} else {
		$('#login_button').text(message)
	}
	if (color == "red") {
		$('section:visible .page-card-body').addClass("invalid");
	}
}

login.set_invalid = function (message) {
	$(".login-content.page-card").addClass('invalid-login');
	setTimeout(() => {
		$(".login-content.page-card").removeClass('invalid-login');
	}, 500)
	login.set_status(message, 'red');
	$("#login_password").focus();
}

login.login_handlers = (function () {
	var get_error_handler = function (default_message) {
		return function (xhr, data) {
			if (xhr.responseJSON) {
				data = xhr.responseJSON;
			}

			var message = default_message;
			if (data._server_messages) {
				message = ($.map(JSON.parse(data._server_messages || '[]'), function (v) {
					// temp fix for messages sent as dict
					try {
						return JSON.parse(v).message;
					} catch (e) {
						return v;
					}
				}) || []).join('<br>') || default_message;
			}

			if (message === default_message) {
				login.set_invalid(message);
			} else {
				login.reset_sections(false);
			}

		};
	}

	var login_handlers = {
		200: function (data) {
			if (data.message == 'Logged In') {
				login.set_status('{{ _("Success") }}', 'green');
				document.body.innerHTML = `{% include "templates/includes/splash_screen.html" %}`;
				window.location.href = frappe.utils.sanitise_redirect(frappe.utils.get_url_arg("redirect-to")) || data.home_page;
			} else if (data.message == 'Password Reset') {
				window.location.href = frappe.utils.sanitise_redirect(data.redirect_to);
			} else if (data.message == "No App") {
				login.set_status("{{ _('Success') }}", 'green');
				if (localStorage) {
					var last_visited =
						localStorage.getItem("last_visited")
						|| frappe.utils.sanitise_redirect(frappe.utils.get_url_arg("redirect-to"));
					localStorage.removeItem("last_visited");
				}

				if (data.redirect_to) {
					window.location.href = frappe.utils.sanitise_redirect(data.redirect_to);
				}

				if (last_visited && last_visited != "/login") {
					window.location.href = last_visited;
				} else {
					window.location.href = data.home_page;
				}
			} else if (window.location.hash === '#forgot') {
				if (data.message === 'not found') {
					login.set_status('{{ _("Not a valid user") }}', 'red');
				} else if (data.message == 'not allowed') {
					login.set_status('{{ _("Not Allowed") }}', 'red');
				} else if (data.message == 'disabled') {
					login.set_status('{{ _("Not Allowed: Disabled User") }}', 'red');
				} else {
					login.set_status('{{ _("Instructions Emailed") }}', 'green');
				}


			} else if (window.location.hash === '#signup') {
				if (cint(data.message[0]) == 0) {
					login.set_status(data.message[1], 'red');
				} else {
					login.set_status('{{ _("Success") }}', 'green');
					frappe.msgprint(data.message[1])
				}
				//login.set_status(__(data.message), 'green');
			}

			//OTP verification
			if (data.verification && data.message != 'Logged In') {
				login.set_status('{{ _("Success") }}', 'green');

				document.cookie = "tmp_id=" + data.tmp_id;

				if (data.verification.method == 'OTP App') {
					continue_otp_app(data.verification.setup, data.verification.qrcode);
				} else if (data.verification.method == 'SMS') {
					continue_sms(data.verification.setup, data.verification.prompt);
				} else if (data.verification.method == 'Email') {
					continue_email(data.verification.setup, data.verification.prompt);
				}
			}
		},
		401: get_error_handler('{{ _("Invalid Login. Try again.") }}'),
		417: get_error_handler('{{ _("Oops! Something went wrong") }}'),
		404: get_error_handler('{{ _("User does not exist.")}}')
	};

	return login_handlers;
})();

frappe.ready(function () {


		login.bind_events();

		if (!window.location.hash) {
			window.location.hash = "#login";
		} else {
			$(window).trigger("hashchange");
		}

		$(".form-signup, .form-forgot, .form-login-with-email-link").removeClass("hide");
		$(document).trigger('login_rendered');

		$('.signin_hide').on('click', function(event) {
			$('#lwsignIn').hide();
		});

		$('.signin_show').on('click', function(event) {
			$('#lwsignIn').show();
		});


		

		$('.signin_show_otp').on('click', function(event) {
			$('.lw_otp').hide();
			$('#lwsignIn').show();
		});

		$('#login_otp_btn').on('click', function(event) {
			$('#lwsigInOtp').show();
		})

		send_otp_login();

		otp_forgotpassword();
		otp_verify();
		otp_verify_sms();

		
		verify_otp_login();

		reset_btn_disabled()
	
});

var verify_token = function (event) {
	$(".form-verify").on("submit", function (eventx) {
		eventx.preventDefault();
		var args = {};
		args.cmd = "login";
		args.otp = $("#login_token").val();
		args.tmp_id = frappe.get_cookie('tmp_id');
		if (!args.otp) {
			frappe.msgprint('{{ _("Login token required") }}');
			return false;
		}
		login.call(args);
		return false;
	});
}

var request_otp = function (r) {
	$('.login-content').empty();
	$('.login-content:visible').append(
		`<div id="twofactor_div">
			<form class="form-verify">
				<div class="page-card-head">
					<span class="indicator blue" data-text="Verification">{{ _("Verification") }}</span>
				</div>
				<div id="otp_div"></div>
				<input type="text" id="login_token" autocomplete="off" class="form-control" placeholder={{ _("Verification Code") }} required="" autofocus="">
				<button class="btn btn-sm btn-primary btn-block mt-3" id="verify_token">{{ _("Verify") }}</button>
			</form>
		</div>`
	);
	// add event handler for submit button
	verify_token();
}

var continue_otp_app = function (setup, qrcode) {
	request_otp();
	var qrcode_div = $('<div class="text-muted" style="padding-bottom: 15px;"></div>');

	if (setup) {
		direction = $('<div>').attr('id', 'qr_info').html('{{ _("Enter Code displayed in OTP App.") }}');
		qrcode_div.append(direction);
		$('#otp_div').prepend(qrcode_div);
	} else {
		direction = $('<div>').attr('id', 'qr_info').html('{{ _("OTP setup using OTP App was not completed. Please contact Administrator.") }}');
		qrcode_div.append(direction);
		$('#otp_div').prepend(qrcode_div);
	}
}

var continue_sms = function (setup, prompt) {
	request_otp();
	var sms_div = $('<div class="text-muted" style="padding-bottom: 15px;"></div>');

	if (setup) {
		sms_div.append(prompt)
		$('#otp_div').prepend(sms_div);
	} else {
		direction = $('<div>').attr('id', 'qr_info').html(prompt || '{{ _("SMS was not sent. Please contact Administrator.") }}');
		sms_div.append(direction);
		$('#otp_div').prepend(sms_div)
	}
}

var continue_email = function (setup, prompt) {
	request_otp();
	var email_div = $('<div class="text-muted" style="padding-bottom: 15px;"></div>');

	if (setup) {
		email_div.append(prompt)
		$('#otp_div').prepend(email_div);
	} else {
		var direction = $('<div>').attr('id', 'qr_info').html(prompt || '{{ _("Verification code email not sent. Please contact Administrator.") }}');
		email_div.append(direction);
		$('#otp_div').prepend(email_div);
	}
}


document.addEventListener("DOMContentLoaded", function () {
	var formSignup = document.getElementById("enter_login");

	if (formSignup) {
		document.addEventListener("keydown", function (event) {
			if (event.key === "Enter") {
				event.preventDefault();
				$(".form-login").click();
			}
		});
	} else {
		console.error("Element with ID 'enter_login' not found.");
	}
});



var send_otp_login = function() {
	
	$('.otp_signin_btn').on('click', function(event) {
		event.preventDefault();
		let otp_credential = $('#otpEmailPhone')[0].value
		let otp_type = ""

		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		const phoneRegex = /^\d{10}$/;

		if (! otp_credential) {
			$('.otp_signin_btn').text("Email Required")
		} else {
			if (emailRegex.test(otp_credential)) {
				otp_type = "Email"
				$('.otp_signin_btn').text("Verifying...").prop("disabled", true);
			}
			else if (phoneRegex.test(otp_credential)) {
				otp_type = "Phone"
				$('.otp_signin_btn').text("Verifying...").prop("disabled", true);
			}
			else {
				$('.otp_signin_btn').text("Invalid Login ID")
			}
		}

		if (otp_type == "Email") {
			frappe.call({
				method: "leftwordlatest.web_api.user.send_otp_email",
				args: {
					email: otp_credential,
					check_existing_user: true
				},
				callback: function(r) {
					if (r.error) {
						$('.otp_signin_btn').text(r.message)
					}
					else {
						$('.otp_signin_btn').text("OTP Send")
						$('#lwsigInOtp').hide()
						$('#lwsignInOtpVerificationEmail').show()
					}
				}
			})
			$('#forgotEmail').val('');
		}
		else if (otp_type == "Phone") {
			frappe.call({
				method: "leftwordlatest.web_api.user.send_otp_sms",
				args: {
					phone: otp_credential,
					allow_sms: false,
					check_existing_user: true
				},
				callback: function(r) {
					if (r.error) {
						$('.otp_signin_btn').text(r.message)
					}
					else {
						$('.otp_signin_btn').text("OTP Send")
						$('#lwsigInOtp').hide()
						$('#lwsignInOtpVerificationPhone').show()
						
					}
				}
			})
		}

	})
}

var reset_btn_disabled = function() {
    const input = document.getElementById("otpEmailPhone");
    const button = document.querySelector(".otp_signin_btn");

    input.addEventListener("input", function() {
        if (input.value.trim() === "") {
            button.textContent = "Submit";
            button.disabled = false;
        }
    });
}


var otp_forgotpassword=function(){
	$('.form-forgot').on('click', function(event) {
		event.preventDefault();
		let otp_credential = $('#forgotEmail')[0].value
		let otp_type = ""

		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		const phoneRegex = /^\d{10}$/;

		if (! otp_credential) {
			$('.form-forgot').text("Email Required")
		} else {
			if (emailRegex.test(otp_credential)) {
				otp_type = "Email"
				$('.form-forgot').text("Verifying...")
			}
			else if (phoneRegex.test(otp_credential)) {
				otp_type = "Phone"
				$('.form-forgot').text("Verifying...")
			}
			else {
				$('.form-forgot').text("Invalid Login ID")
			}		
		}

		if (otp_type == "Email") {
			frappe.call({
				method: "leftwordlatest.web_api.user.send_otp_email",
				args: {
					email: otp_credential,
					check_existing_user: true
				},
				callback: function(r) {		
					if (r.error) {
						$('.form-forgot').text(r.message)
					}
					else {
						$('.form-forgot').text("OTP Send")
						$('#lwforgotpass').hide()
						$('#lwotpemail').show()
					}
				}
			})
		}
		
		else if (otp_type == "Phone") {
			frappe.call({
				method: "leftwordlatest.web_api.user.send_otp_sms",
				args: {
					phone: otp_credential,
					allow_sms: false,
					check_existing_user: true
				},
				callback: function(r) {
					if (r.error) {				
						$('.form-forgot').text(r.message)
					}
					else {
						$('.form-forgot').text("OTP Send")
						$('#lwforgotpass').hide()
						$('#lwotpphone').show()
						
					}
				}
			})
		}

	})

}
var otp_verify = function() {
    $('.form-confirm').on('click', function(event) {
        event.preventDefault();		

        let otp_code = '';
        otp_code += $('#input9').val();
        otp_code += $('#input10').val();
        otp_code += $('#input11').val();
        otp_code += $('#input12').val();
        $('.form-confirm').text("Verifying...").prop("disabled", true);

        frappe.call({
            method: "leftwordlatest.web_api.user.verify_otp_email",
            args: {
                email: $('#forgotEmail')[0].value,
                otp_code: otp_code 
            },
            callback: function(response) {
                if (response.error) {
                    $('.form-confirm').text("Confirm").prop("disabled", false);
                    alert(response.message);
                } else {
                    $('.form-confirm').text("OTP Verified").prop("disabled", false);

                    setTimeout(function() {
                        
						clearOtpFields();
                        
                        $('#lwresetpass').modal('show');
                        $('#lwforgotpass').hide(); 
                        $('#lwotpemail').hide(); 
                    }, 500);
                }
            }
        });
    });
} 

function clearOtpFields() {
    document.getElementById("input9").value = '';
    document.getElementById("input10").value = '';
    document.getElementById("input11").value = '';
    document.getElementById("input12").value = '';
}
$(document).ready(function () {

	clearOtpFields();
	$('#forgotEmail').val('');

const $newPassword = $('#newPassword');
const $confirmPassword = $('#confirmPassword');
const $submitButton = $('#resetSubmitButton');
const $passwordError = $('#passwordError');
const $passwordStrength = $('#passwordStrength');
const $passwordRequirements = $('#passwordRequirements');
const $passwordSuccessMessage = $('#passwordSuccessMessage');

function checkPasswordField() {
    const password = $newPassword.val();
    const passwordStrengthMessage = [];
    const passwordValidations = {
        length: password.length >= 8,
        lowercase: /[a-z]/.test(password),
        uppercase: /[A-Z]/.test(password),
        number: /[0-9]/.test(password),
        specialCharacter: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };

    updatePasswordRequirement('length', passwordValidations.length);
    updatePasswordRequirement('lowercase', passwordValidations.lowercase);
    updatePasswordRequirement('uppercase', passwordValidations.uppercase);
    updatePasswordRequirement('number', passwordValidations.number);
    updatePasswordRequirement('specialCharacter', passwordValidations.specialCharacter);

    if (Object.values(passwordValidations).every(val => val)) {
        $submitButton.prop('disabled', false); 
        $passwordStrength.text('Password strength: Strong').removeClass('text-danger text-warning').addClass('text-success');
        $passwordSuccessMessage.removeClass('d-none'); 
    } else {
        $submitButton.prop('disabled', true); // Keep submit button disabled
        $passwordStrength.text('Password strength: Weak').removeClass('text-success text-warning').addClass('text-danger');
        $passwordSuccessMessage.addClass('d-none'); 
    }

    // Show or hide confirm password field
    $confirmPassword.prop('disabled', !passwordValidations.length); 
    validatePasswords(password);
}

// Update password requirement validation
function updatePasswordRequirement(rule, isValid) {
    const requirement = $(`#${rule}Requirement`);
    if (isValid) {
        requirement.removeClass('text-muted').addClass('text-success');
    } else {
        requirement.removeClass('text-success').addClass('text-muted');
    }
}

// Function to validate password fields
function validatePasswords() {
    if ($newPassword.val() && $newPassword.val() === $confirmPassword.val()) {
        $passwordError.addClass('d-none');
        $submitButton.prop('disabled', false);
    } else if ($confirmPassword.val()) {
        $passwordError.removeClass('d-none');
        $submitButton.prop('disabled', true);
    } else {
        $passwordError.addClass('d-none');
        $submitButton.prop('disabled', true);
    }
}

// Event listeners
$newPassword.on('input', checkPasswordField);
$confirmPassword.on('input', validatePasswords);

// Clear the password fields when the modal is shown
$('#lwresetpass').on('shown.bs.modal', function () {
    $newPassword.val('');
    $confirmPassword.val('');
    $passwordError.addClass('d-none');
    $submitButton.prop('disabled', true);
    $passwordStrength.text('');
    $passwordRequirements.find('p').removeClass('text-success').addClass('text-muted');
    $passwordSuccessMessage.addClass('d-none');
});

    // Reset password for provided email with async function
    document.getElementById("resetSubmitButton").addEventListener("click", async function (e) {
        e.preventDefault();
        const email = document.getElementById("forgotEmail").value;
        const newPassword = document.getElementById("newPassword").value;
        const confirmPassword = document.getElementById("confirmPassword").value;

        // Check if passwords match
        if (newPassword !== confirmPassword) {
            document.getElementById("passwordError").classList.remove("d-none");
            return;
        } else {
            document.getElementById("passwordError").classList.add("d-none");
        }

        // Call the server-side function to reset the password
        try {
            await frappe.call({
                method: "leftwordlatest.www.resetyourpassword.reset_password",
                args: { email: email, new_password: newPassword },
                callback: function (response) {
                    if (response.message === "Password updated successfully") {

						$('#resetSubmitButton').text("Password updated successfully").prop("disabled", false);

                        $('#').modal('hide'); 
                    }
                }
            });
        } catch (error) {
            console.error(error);
            alert("Error resetting password. Please try again.");
			$('#resetSubmitButton').text("Error resetting password").prop("disabled", false);
        }
    });

    $('#lwresetpass').on('hidden.bs.modal', function () {
        window.location.href = ''; // Redirect to the specified URL
    });
});

function checkPasswordField() {
	const newPassword = document.getElementById('newPassword').value;
	const confirmPassword = document.getElementById('confirmPassword');
  
	if (newPassword.trim() !== '') {
	  confirmPassword.removeAttribute('disabled');
	} else {
	  confirmPassword.setAttribute('disabled', true); 
	  confirmPassword.value = ''; 
	}
  }
  function showMessageIfEmpty() {
	const newPassword = document.getElementById('newPassword').value;
	const confirmPasswordMessage = document.getElementById('confirmPasswordMessage');
	const confirmPassword = document.getElementById('confirmPassword');
  
	if (newPassword.trim() === "") {
	  confirmPasswordMessage.classList.remove('d-none'); 
	  confirmPassword.setAttribute('disabled', 'true'); 
	} else {
	  confirmPasswordMessage.classList.add('d-none'); 
	  confirmPassword.removeAttribute('disabled'); 
	}
  }
  
  
  document.getElementById('newPassword').addEventListener('input', showMessageIfEmpty);
  document.getElementById('confirmPassword').addEventListener('focus', showMessageIfEmpty);
  
  function togglePassword(inputId, toggleButton) {
	const passwordField = document.getElementById(inputId);
	const icon = toggleButton.querySelector('i');
	const currentType = passwordField.getAttribute('type');
  
	if (currentType === 'password') {
	  passwordField.setAttribute('type', 'text'); 
	  icon.classList.remove('fa-eye'); 
	  icon.classList.add('fa-eye-slash');
	} else {
	  passwordField.setAttribute('type', 'password'); 
	  icon.classList.remove('fa-eye-slash'); 
	  icon.classList.add('fa-eye');
	}
  }




//phone otp verification
var otp_verify_sms=function(){
	$('.form-confirm-sms').on('click', function(event) {
        event.preventDefault();		

        // Capture the OTP entered by the user
        let otp_code = '';
		otp_code += $('#input5').val();
		otp_code += $('#input6').val();
    	otp_code += $('#input7').val();
    	otp_code += $('#input8').val();
		$('.form-confirm-sms').text("Verifying...").prop("disabled", true);
		frappe.call({
            method: "leftwordlatest.web_api.user.verify_otp_sms", // Backend method to verify OTP
            args: {
                phone: $('#forgotEmail')[0].value, // User's email entered earlier
                otp_code: otp_code // OTP entered by the user
            },
            callback: function(response) {
                if (response.error) {
                    // If there's an error, show the message from the server
                    $('.form-confirm-sms').text("Confirm").prop("disabled", false);
                    alert(response.message);
                } else {
                    // If OTP verification is successful, submit the form
                    $('.form-confirm-sms').text("OTP Verified").prop("disabled", false);
                    alert("OTP verified successfully!");
					clearOtpFields();

                    // You can proceed with submitting the form here if needed
                    // For example, you can submit the form or show the next screen
                    //$('#lwforgotpass').show();
                    $('#lwotpphone').hide();	
                }
            }
        });
    });
}
function clearOtpFields() {
    document.getElementById("input9").value = '';
    document.getElementById("input10").value = '';
    document.getElementById("input11").value = '';
    document.getElementById("input12").value = '';
}
$(document).ready(function() {
    clearOtpFields();
});


function moveToNext(current, nextFieldID) {
    if (current.value.length === 1 && nextFieldID) {
        document.getElementById(nextFieldID).focus();
    }
    resetButtonIfNeeded(); 
}

function resetButtonIfNeeded() {
    const fields = ["otpEmail1", "otpEmail2", "otpEmail3", "otpEmail4"];
    let anyEmpty = fields.some(id => document.getElementById(id).value.trim() === "");
    if (anyEmpty) {
        document.getElementById('otpLoginSubmitEmail').innerText = "Confirm";
    }
}

var verify_otp_login = function() {
	$('.otp_submit_email').on('click', function(event) {
		event.preventDefault();
		let otp_email = $('#otpEmailPhone')[0].value
		const otp = [
			document.getElementById("otpEmail1").value,
			document.getElementById("otpEmail2").value,
			document.getElementById("otpEmail3").value,
			document.getElementById("otpEmail4").value
		].join('');

		if (otp.length !== 4 || !/^\d+$/.test(otp)) {
			alert("Please enter a valid 4-digit OTP.");
			$('.otp_submit_email').text("Please enter a valid 4-digit OTP.")
			return;
		}

		$('.otp_submit_email').text("Verifying...")
		frappe.call({
			method: "leftwordlatest.web_api.user.otp_login",
			args: {
				otp: otp,
				email: otp_email
			},
			callback: function(r) {
				if (r.error) {
					$('.otp_submit_email').text(r.message)
					resetButtonIfNeeded();
				}
				else if (r.message == "Authentication success"){
					$('.otp_submit_email').text(r.message)
					window.location.href = ""
				}
				else {
					$('.otp_submit_email').text(r.message)
				}
			}
		})
	});

	$('.otp_submit_phone').on('click', function(event){
		event.preventDefault();
		let otp_phone = $('#otpEmailPhone')[0].value
		const otp = [
			document.getElementById("otpPhone1").value,
			document.getElementById("otpPhone2").value,
			document.getElementById("otpPhone3").value,
			document.getElementById("otpPhone4").value
		].join('');
		if (otp.length !== 4 || !/^\d+$/.test(otp)) {
			alert("Please enter a valid 4-digit OTP.");
			$('.otp_submit_phone').text("Please enter a valid 4-digit OTP.")
			return;
		}

		$('.otp_submit_phone').text("Verifying...")
		frappe.call({
			method: "leftwordlatest.web_api.user.otp_login",
			args: {
				otp: otp,
				phone: otp_phone 
			},
			callback: function(r) {
				if (r.error) {
					$('.otp_submit_phone').text(r.message)
					resetButtonIfNeeded();
				}	
				else if (r.message == "Authentication success"){
					$('.otp_submit_phone').text(r.message)
					window.location.href = ""
				}
				else {
					$('.otp_submit_phone').text(r.message)
				}

			}
		})
	});

	$('.btn-close-otp').on('click', function(e) {
		e.preventDefault();
		$('#lwsignInOtpVerificationPhone').hide()
	}) 
}



// from sign in popup to sign up
document.addEventListener("DOMContentLoaded", function () {
    const signUpLink = document.getElementById("openSignUpLink");

    signUpLink.addEventListener("click", function (event) {
        event.preventDefault();

        // Close the Sign In modal
        const signInModal = bootstrap.Modal.getInstance(document.getElementById("lwsignIn"));
        if (signInModal) {
            signInModal.hide();
        }

        // Show the Sign Up modal
        new bootstrap.Modal(document.getElementById("lwsignUp")).show();
    });
});
