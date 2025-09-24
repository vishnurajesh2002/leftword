frappe.ready(function(){
    if (frappe.session.user == 'Guest'){
        window.location.href = '/leftword_home'

    }
    $('.logout').on("click", function(e){
        e.preventDefault()
        frappe.xcall("logout").then(data=>{
            window.location.href = '/leftword_home'
        })
    })
   $('.btn-update-user').on("click", function(e) {
    $('#btnEditProfile').attr('disabled', 'true');

    frappe.xcall('leftwordlatest.web_api.user.update_user_account', {
        "first_name": $('#first-name').val(),
        "last_name": $('#last-name').val(),
        "custom_display_name": $('#display-name').val(),
        "email_id": $('#email-id').val(),
        "phone": $('#phone-number').val()
    }).then(data => {
        $('#btnEditProfile').removeAttr('disabled');
        $('#user-name').text($('#display-name').val());
        document.getElementById('phone-number').value = data["phone"] || "";
        window.location.reload();
    }).catch(err => {
        $('#btnEditProfile').removeAttr('disabled');
        console.error('Error updating user:', err);
        alert('Failed to save changes. Please try again.');
    });
});

    $('#imageUpload').on('input', function(e){
        var file = $('#imageUpload')[0].files[0];
        if (file) {
            var reader = new FileReader();
            reader.onloadend = function() {
                var base64String = reader.result;
                frappe.xcall('leftwordlatest.web_api.utils.upload_cus_img', {
                    "image": base64String,
                    "customer": $('#last-name').val(),
                }).then(data=>{
                    if(data){
                        $('.user-img').attr('src', data.file_url)
                    }
                })
                document.getElementById('base64result').textContent = base64String;
            };
            reader.readAsDataURL(file);
        } else {
            alert("Please select a file first.");
        }

    })
});
