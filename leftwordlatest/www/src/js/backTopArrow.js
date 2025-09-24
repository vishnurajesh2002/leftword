// Heart Like

document.querySelectorAll('.heart-icon').forEach(function(icon) {
    icon.addEventListener('click', function(event) {
        event.preventDefault(); // Prevent default behavior
        var heartIcon = this.querySelector('.fa-heart');
        if (heartIcon.classList.contains('fa-regular')) {
            heartIcon.classList.remove('fa-regular');
            heartIcon.classList.add('fa-solid');
        } else {
            heartIcon.classList.remove('fa-solid');
            heartIcon.classList.add('fa-regular');
        }
    });
});

// Heart Like


// Scroll to Top Button

var scrollToTopBtn = document.querySelector(".scrollToTopBtn")
var rootElement = document.documentElement

function handleScroll() {
    var scrollTotal = rootElement.scrollHeight - rootElement.clientHeight
    if ((rootElement.scrollTop / scrollTotal) > 0.15) {
        scrollToTopBtn.classList.add("showBtn")
    } else {
        scrollToTopBtn.classList.remove("showBtn")
    }
}

function scrollToTop() {
    rootElement.scrollTo({
        top: 0,
        behavior: "smooth"
    })
}
scrollToTopBtn.addEventListener("click", scrollToTop)
document.addEventListener("scroll", handleScroll)

// Scroll to Top Button