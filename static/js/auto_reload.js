window.addEventListener('pageshow', (event) => {
  if (event.persisted) {
    console.log('Page loaded from back-forward cache, reloading...');
    window.location.reload();
  } else {
    console.log('Page loaded normally');
  }
});


