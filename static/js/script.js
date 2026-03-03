document.addEventListener("DOMContentLoaded", () => {

    const cartDisplay = document.getElementById("cart-count");
    const buttons = document.querySelectorAll(".add-to-cart");

    let cartCount = parseInt(cartDisplay?.textContent) || 0;

    buttons.forEach(button => {

        button.addEventListener("click", function () {

            // Increase cart count
            cartCount++;
            if (cartDisplay) {
                cartDisplay.textContent = cartCount;

                // Cart bounce animation
                cartDisplay.classList.add("cart-bounce");
                setTimeout(() => {
                    cartDisplay.classList.remove("cart-bounce");
                }, 300);
            }

            // Button animation
            this.classList.add("added");
            this.innerHTML = "✓ Added";

            setTimeout(() => {
                this.classList.remove("added");
                this.innerHTML = "Add to Cart";
            }, 1200);

        });

    });

});