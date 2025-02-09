document.addEventListener('DOMContentLoaded', function() {
    const roleSelect = document.getElementById("role");
    const doctorField = document.getElementById("doctorFields");
    const signUpForm = document.querySelector("#signup_modal form");

    // Show/hide doctor fields based on role selection
    roleSelect.addEventListener("change", function() {
        doctorField.style.display = this.value === "2" ? "block" : "none";
    });

    // Form validation function
    function showErrorMessage(field, message) {
        // Remove any existing error messages
        const existingError = field.nextElementSibling;
        if (existingError && existingError.classList.contains('error-message')) {
            existingError.remove();
        }

        // Create and insert new error message
        const errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        errorElement.style.color = "red";
        errorElement.textContent = message;
        field.insertAdjacentElement('afterend', errorElement);
    }

    function clearErrorMessage(field) {
        const errorElement = field.nextElementSibling;
        if (errorElement && errorElement.classList.contains('error-message')) {
            errorElement.remove();
        }
    }

    function validatePhone(phone) {
        const re = /^(?:\+91|91|0)?[6-9]\d{9}$/;
        return re.test(phone.value.trim());
    }

    function validateForm(e) {
        // Clear previous error messages
        document.querySelectorAll('.error-message').forEach(el => el.remove());

        let isValid = true;

        const fullName = document.getElementById("full_name");
        const phone = document.getElementById("phone");
        const email = document.getElementById("email");
        const dob = document.getElementById("dob");
        const password = document.getElementById("password");
        const role = document.getElementById("role");

        // Name validation
        if (fullName.value.trim() === "") {
            showErrorMessage(fullName, "Name is required.");
            isValid = false;
        }

        // Phone number validation
        if (!validatePhone(phone)) {
            showErrorMessage(phone, "Phone number is not valid.");
            isValid = false;
        }

        // Email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email.value.trim())) {
            showErrorMessage(email, "Please enter a valid email address.");
            isValid = false;
        }

        // Date of birth validation
        if (dob.value === "") {
            showErrorMessage(dob, "Date of birth is required.");
            isValid = false;
        }

        // Password validation
        // if (password.value.length < 8) {
        //     showErrorMessage(password, "Password must be at least 8 characters long.");
        //     isValid = false;
        // }

        // Doctor-specific field validation
        if (role.value === "2") {
            const degree = document.getElementById("degree");
            const specialization = document.getElementById("specialization");
            const experience = document.getElementById("experience");
            const address = document.getElementById("address");

            if (degree.value.trim() === "") {
                showErrorMessage(degree, "Degree is required for doctors.");
                isValid = false;
            }
            if (specialization.value.trim() === "") {
                showErrorMessage(specialization, "Specialization is required for doctors.");
                isValid = false;
            }
            if (experience.value.trim() === "") {
                showErrorMessage(experience, "Experience is required for doctors.");
                isValid = false;
            }
            if (address.value.trim() === "") {
                showErrorMessage(address, "Address is required for doctors.");
                isValid = false;
            }
        }

        // If not valid, prevent form submission and scroll to first error
        if (!isValid) {
            e.preventDefault();
            const firstError = document.querySelector('.error-message');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }

        return isValid;
    }

    // Attach validation to form submission
    if (signUpForm) {
        signUpForm.addEventListener("submit", validateForm);
    }
});