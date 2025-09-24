frappe.ready(() => {

    $('.logout').on("click", function(e){
        e.preventDefault()
        frappe.xcall("logout").then(data=>{
            window.location.href = '/leftword_home'
        })
    })






    
});