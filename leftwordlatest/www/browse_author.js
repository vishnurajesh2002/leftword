frappe.ready(function() {
       
    function loadAuthors(letter, clickedLink) {
    
        const grid = document.getElementById('authors-grid');
        grid.innerHTML = ''; 

        frappe.call({
            method: "leftwordlatest.www.browse_author.get_authors_by_letter",
            args: { letter: letter },
            callback: function(response) {
                const authors = response.message;

                const letterLinks = document.querySelectorAll(`#alphabet-nav a`);
                letterLinks.forEach(link => {
                    link.style.color = 'black'; 
                });

            
                clickedLink.style.color = 'red';

               
                if (authors.length === 0) {
                    grid.innerHTML = `<p>No authors found for this letter.</p>`;
                    return;
                }

                const sectionSize = 50; 
                const left = authors.slice(0, sectionSize);
                const middle = authors.slice(sectionSize, sectionSize * 2);
                const right = authors.slice(sectionSize * 2, sectionSize * 3);

                let html = `
                    <div class="author-section left">
                        <ul>
                            ${left.map(author => `<li><a href="authordetails?author_name=${author.custom_name}" class="author-link">${author.custom_name}</a></li>`).join('')}
                        </ul>
                    </div>
                    <div class="author-section middle">
                        <ul>
                            ${middle.map(author => `<li><a href="authordetails?author_name=${author.custom_name}" class="author-link">${author.custom_name}</a></li>`).join('')}
                        </ul>
                    </div>
                    <div class="author-section right">
                        <ul>
                            ${right.map(author => `<li><a href="authordetails?author_name=${author.custom_name}" class="author-link">${author.custom_name}</a></li>`).join('')}
                        </ul>
                    </div>
                `;
                
                grid.innerHTML = html;
            }
        });
    }
    document.getElementById('alphabet-nav').addEventListener('click', function(e) {
      
        if (e.target && e.target.matches('a.letter-link')) {
            const letter = e.target.textContent;
            loadAuthors(letter, e.target);
        }
    });

    const urlParams = new URLSearchParams(window.location.search);
    const letter = urlParams.get('letter') || 'A';  
   
    if (letter && 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.includes(letter.toUpperCase())) {
       
        const initialLink = document.querySelector(`a.letter-link:nth-child(${"ABCDEFGHIJKLMNOPQRSTUVWXYZ".indexOf(letter) + 1})`);
        loadAuthors(letter, initialLink);
    } else {
       
        const defaultLetter = 'A';
        const initialLink = document.querySelector(`a.letter-link:nth-child(${"ABCDEFGHIJKLMNOPQRSTUVWXYZ".indexOf(defaultLetter) + 1})`);
        loadAuthors(defaultLetter, initialLink);
    }
});