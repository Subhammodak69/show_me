window.addEventListener('pageshow', (event) => {
  if (event.persisted) {
    console.log('Page loaded from back-forward cache, reloading...');
    window.location.reload();
  } else {
    console.log('Page loaded normally');
  }
});

// Global function (place outside listener)
function timeAgo(date) {
  const now = new Date().getTime();
  const diff = Math.floor((now - new Date(date).getTime()) / 1000);
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)} mins ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} hrs ago`;
  return `${Math.floor(diff / 86400)} days ago`;
}

window.addEventListener('DOMContentLoaded', function() {
  const field = document.querySelector('#ratingTime'); 
  if (field) {
    field.textContent = timeAgo(field.dataset.timestamp);
  }
  
  // Optional: Update every minute
  setInterval(() => {
    if (field) field.textContent = timeAgo(field.dataset.timestamp);
  }, 60000);
});





