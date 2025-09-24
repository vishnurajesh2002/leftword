document.addEventListener("DOMContentLoaded", () => {
    const alphabetLinks = document.querySelectorAll(".alphabet-letter");
    const categoriesContainer = document.querySelector("#categories");
    const doneButton = document.querySelector("#done-button");
    const clearButton = document.querySelector("#clear-button"); 
    let selectedCategories = [];

    const fetchCategories = (letter = null) => {
        frappe.call({
            method: "leftwordlatest.www.all_categories.get_categories_by_alphabet",
            args: { letter: letter },
            callback: (response) => {
                const categories = response.message;
                categoriesContainer.innerHTML = "";

                if (categories && categories.length) {
                    categories.forEach((category) => {
                        const categoryDiv = document.createElement("div");
                        categoryDiv.classList.add("category-item");
                        categoryDiv.innerHTML = `
                           <label style="display: flex; align-items: center; gap: 10px;">
                                <input type="checkbox" class="category-checkbox" data-category="${category.category_name}">
                                <span>${category.category_name}</span>
                            </label>`;
                        categoriesContainer.appendChild(categoryDiv);
                    });

                    // Checkbox Event Handling
                    const checkboxes = document.querySelectorAll(".category-checkbox");
                    checkboxes.forEach((checkbox) => {
                        checkbox.addEventListener("change", (event) => {
                            const categoryName = event.target.getAttribute("data-category");
                            if (event.target.checked) {
                                if (!selectedCategories.includes(categoryName)) {
                                    selectedCategories.push(categoryName);
                                }
                            } else {
                                selectedCategories = selectedCategories.filter(
                                    (cat) => cat !== categoryName
                                );
                            }

                            // Enable or disable buttons based on selection
                            doneButton.disabled = selectedCategories.length === 0;
                            clearButton.disabled = selectedCategories.length === 0;
                        });
                    });
                } else {
                    categoriesContainer.innerHTML =
                        "<p class='no-categories'>No categories available</p>";
                    doneButton.disabled = true; 
                    clearButton.disabled = true; 
                }
            },
        });
    };
   
    

    // Fetch categories initially
    fetchCategories();

    // Alphabet Letter Event Handling
    alphabetLinks.forEach((letter) => {
        letter.addEventListener("click", () => {
            alphabetLinks.forEach((l) => l.classList.remove("active"));
            letter.classList.add("active");

            const selectedLetter = letter.getAttribute("data-letter");
            fetchCategories(selectedLetter);
        });
    });

    // Done Button Event
    doneButton.addEventListener("click", () => {
        if (selectedCategories.length > 0) {
            const filterArgs = selectedCategories.join(",");
            window.location.href = `/categories?filter_args=${encodeURIComponent(filterArgs)}`;
        }
    });

    // Clear Button Event
    clearButton.addEventListener("click", () => {
        const checkboxes = document.querySelectorAll(".category-checkbox");
        checkboxes.forEach((checkbox) => {
            checkbox.checked = false;
        });

        selectedCategories = [];
        doneButton.disabled = true;
        clearButton.disabled = true;
    });
});

