// // document.addEventListener('DOMContentLoaded', function() {
//     const cartCountElement = document.getElementById('cart-count');
//     const cartCount = parseInt(cartCountElement.textContent) || 0;

//     // Update cart count dynamically
//     function updateCartCount(count) {
//         cartCountElement.textContent = count;
//     }

//     // You can listen to cart updates using WebSocket or AJAX
//     // For simplicity, you can reload the page to update the cart count
//     function handleCartUpdate() {
//         // Example: Reload page after adding an item to the cart
//         // You can replace this with WebSocket or AJAX call
//         updateCartCount(cartCount + 1);
//     }

//     // Example: Listen for custom 'cartUpdated' event
//     document.addEventListener('cartUpdated', function() {
//         handleCartUpdate();
//     });
// });

