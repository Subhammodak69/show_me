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

  let $resultsList = $('<ul id="searchResults" style="left: 20%; top: 100%; position: absolute; background: white; border: 1px solid rgb(204, 204, 204); width: 60%; max-height: 200px; overflow-y: auto; z-index: 1000;"></ul>');
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
            $resultsList.append('<li>No results found</li>');
          } else {
            data.forEach(function (item) {
              let $li = $('<li style="padding: 5px; cursor: pointer;"></li>');
              $li.text(item.product_name);
              $li.on('click', function () {
                window.location.href = `/product/details/${item.id}/`;
              });
              $resultsList.append($li);
            });
          }
          $resultsList.show();
        },
        error: function () {
          $resultsList.empty().append('<li>Error fetching results</li>').show();
        }
      });
    }, 300);
  });

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
