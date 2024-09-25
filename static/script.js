document.getElementById('load-more').addEventListener('click', function() {
    const hiddenBoxes = document.querySelectorAll('.box.hidden');
    hiddenBoxes.forEach((box, index) => {
        if (index < 4) { // Reveal up to 4 more boxes on each click
            box.classList.remove('hidden');
        }
    });

    // If there are no more hidden boxes, hide the button
    if (document.querySelectorAll('.box.hidden').length === 0) {
        this.style.display = 'none';
    }
});


// Get the modal
var modal = document.getElementById("appointmentModal");

// Get the button that opens the modal
var btn = document.querySelectorAll(".open-modal");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// Loop through all pen icons and attach event listener
btn.forEach(function(element) {
    element.addEventListener("click", function(event) {
        event.preventDefault(); // Prevent default anchor behavior
        modal.style.display = "block"; // Open the modal
    });
});

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}


// Get the modal elements
var signupModal = document.getElementById("signupModal");
var loginModal = document.getElementById("loginModal");

// Get the button that opens the modal
var signupBtn = document.getElementById("signupBtn");
var loginBtn = document.getElementById("loginBtn");

// Get the <span> element that closes the modal
var closeButtons = document.getElementsByClassName("close");

// When the user clicks the button, open the respective modal 
signupBtn.onclick = function() {
    signupModal.style.display = "block";
}

loginBtn.onclick = function() {
    loginModal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
for (var i = 0; i < closeButtons.length; i++) {
    closeButtons[i].onclick = function() {
        signupModal.style.display = "none";
        loginModal.style.display = "none";
    }
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == signupModal) {
        signupModal.style.display = "none";
    }
    if (event.target == loginModal) {
        loginModal.style.display = "none";
    }
}
