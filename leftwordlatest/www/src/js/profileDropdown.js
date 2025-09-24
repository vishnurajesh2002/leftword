// My profile section

document.addEventListener("DOMContentLoaded", function() {
    var dropdown = document.getElementById("dropdown");
    var profileContainer = document.querySelector(".profile-container");
    var profile = document.querySelector(".profile");
    var username = document.querySelector(".username");

    var isDropdownVisible = false;

    profile.addEventListener("click", function(event) {
        event.stopPropagation();
        isDropdownVisible = !isDropdownVisible;
        dropdown.style.display = isDropdownVisible ? "block" : "none";
    });

    username.addEventListener("click", function(event) {
        event.stopPropagation();
        isDropdownVisible = !isDropdownVisible;
        dropdown.style.display = isDropdownVisible ? "block" : "none";
    });

    document.addEventListener("mousedown", function(event) {
        if (isDropdownVisible && !profileContainer.contains(event.target)) {
            dropdown.style.display = "none";
            isDropdownVisible = false;
        }
    });

    profileContainer.addEventListener("click", function(event) {
        event.stopPropagation();
    });
});

// My profile section