// Tooltip initialization
document.addEventListener('DOMContentLoaded', function () {
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.forEach(function (tooltipTriggerEl) {
    new bootstrap.Tooltip(tooltipTriggerEl);
  });
});

// Category dropdown functionality
document.addEventListener("DOMContentLoaded", function () {
    fetch('/api/all/category/')
        .then(response => response.json())
        .then(data => {
            // Target both spans
            const sidebarList = document.getElementById('sidebar-category-list');
            const dropdownList = document.getElementById('dropdown-category-list');
            
            // Clear both
            sidebarList.innerHTML = '';
            dropdownList.innerHTML = '';

            // Populate both with same data
            data.forEach(category => {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.className = 'dropdown-item';  // Works for both sidebar and dropdown
                a.href = `/category/products/${category.id}/`;
                a.textContent = category.name;
                
                li.appendChild(a);
                
                // Add to both containers
                sidebarList.appendChild(li.cloneNode(true));  // Clone for sidebar
                dropdownList.appendChild(li);  // Original for dropdown
            });
        })
        .catch(error => {
            console.error('Error fetching categories:', error);
            // Optional: Show error in both spans
            const errorMsg = document.createElement('p');
            errorMsg.className = 'text-danger small';
            errorMsg.textContent = 'Failed to load categories.';
            document.getElementById('sidebar-category-list').appendChild(errorMsg.cloneNode(true));
            document.getElementById('dropdown-category-list').appendChild(errorMsg);
        });
});


// Search toggle for mobile
const icon = document.getElementById('searchToggleIcon');
const mobileInput = document.getElementById('searchInputMobile');
const desktopInput = document.getElementById('searchInputDesktop');

icon.addEventListener('click', (e) => {
  e.stopPropagation();
  if (mobileInput.classList.contains('active')) {
    mobileInput.classList.remove('active');
    icon.style.display = 'inline-block';
  } else {
    mobileInput.classList.add('active');
    icon.style.display = 'none';
  }
});

document.addEventListener('click', (e) => {
  if (
    window.innerWidth <= 662 &&
    !e.target.closest('.mobile-search-container') &&
    e.target !== icon
  ) {
    mobileInput.classList.remove('active');
    icon.style.display = 'inline-block';
  }
});

window.addEventListener('resize', () => {
  if (window.innerWidth > 662) {
    icon.style.display = 'none';
    mobileInput.classList.remove('active');
    desktopInput.style.display = 'inline-block';
  } else {
    icon.style.display = 'inline-block';
    desktopInput.style.display = 'none';
  }
});

window.addEventListener('load', () => {
  if (window.innerWidth > 662) {
    icon.style.display = 'none';
    desktopInput.style.display = 'inline-block';
  } else {
    icon.style.display = 'inline-block';
    desktopInput.style.display = 'none';
  }
});

// Dropdown toggle functionality
document.addEventListener("DOMContentLoaded", function () {
  const toggleButton = document.getElementById("dropdownToggleBtn");
  const dropdownMenu = document.querySelector(".custom-dropdown-menu");
  const navDropdown = document.querySelector(".nav-item.dropdown");

  toggleButton.addEventListener("click", function (event) {
    event.preventDefault();
    dropdownMenu.classList.toggle("show");
    event.stopPropagation();
  });

  navDropdown.addEventListener("click", function (event) {
    event.stopPropagation();
  });

  document.addEventListener("click", function () {
    dropdownMenu.classList.remove("show");
  });
});

// jQuery search functionality
$(document).ready(function () {
    let $searchInput = $('#searchInputDesktop, #searchInputMobile');
    
    // Google-style results container
    let $resultsList = $(
        '<div id="searchResults" style="\
            position: absolute; \
            top: 100%; left: 0;right: 0;\
            width: 70%; max-width: 600px; \
            background: white; \
            border: 1px solid #dfe1e5; \
            border-radius: 24px; \
            box-shadow: 0 4px 12px rgba(0,0,0,0.15); \
            max-height: 400px; \
            overflow-y: auto; \
            z-index: 10000; \
            display: none; margin:0 auto;\
        "></div>'
    );
    
    $searchInput.after($resultsList);
    $resultsList.hide();

    let debounceTimer;

    $searchInput.on('input', function () {
        clearTimeout(debounceTimer);
        let query = $(this).val().trim();
        
        if (query.length < 2) {
            $resultsList.empty().hide();
            return;
        }

        debounceTimer = setTimeout(function () {
            $.ajax({
                url: `/category/products/search/?q=${encodeURIComponent(query)}`,
                method: 'GET',
                success: function (data) {
                    $resultsList.empty();
                    
                    if (data.length === 0) {
                        $resultsList.html('<div class="search-no-result">No products found</div>');
                    } else {
                        data.forEach(function (item) {
                            let $result = $(`
                                <div class="google-search-result" data-product-id="${item.id}">
                                    <div class="result-image">
                                        <img src="${item.photo_url || '/static/no_image.png'}" alt="${item.product_name}">
                                    </div>
                                    <div class="result-content">
                                        <div class="result-title">${item.product_name}</div>
                                        <div class="result-details">
                                            <span class="result-price">${item.price ? '₹' + item.price : 'Price not available'}</span>
                                            <span class="result-category">${item.category || 'Category'}</span>
                                        </div>
                                    </div>
                                    <div class="result-arrow">
                                        <i class="bi bi-chevron-right"></i>
                                    </div>
                                </div>
                            `);
                            
                            $result.on('click', function () {
                                window.location.href = `/product/details/${item.id}/`;
                            });
                            
                            $resultsList.append($result);
                        });
                    }
                    $resultsList.show();
                },
                error: function () {
                    $resultsList.html('<div class="search-error">Error fetching results</div>').show();
                }
            });
        }, 300);
    });

    // Click outside to hide
    $(document).on('click', function (e) {
        if (!$(e.target).closest($searchInput).length && !$(e.target).closest($resultsList).length) {
            $resultsList.hide();
        }
    });
});



window.showMessage = function(type, message, redirectUrl = null) {
  const errorDiv = document.getElementById('error');
  const successDiv = document.getElementById('success');

  errorDiv.style.display = 'none';
  successDiv.style.display = 'none';

  if (type === 'success') {
    successDiv.innerText = message;
    successDiv.style.display = 'block';
    setTimeout(() => {
      successDiv.style.display = 'none';
      if (redirectUrl) {
        window.location.href = redirectUrl;
      }
    }, 2000);  // Show message for 2 seconds, then hide and redirect
  } else if (type === 'error') {
    errorDiv.innerText = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
      errorDiv.style.display = 'none';
    }, 2000);
  }
};
