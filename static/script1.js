document.addEventListener('DOMContentLoaded', function() {
    const roleSelect = document.getElementById("role");
    const doctorField = document.getElementById("doctorFields");
    const signUpForm = document.querySelector("#signup_modal form");

    // Show/hide doctor fields based on role selection
    if (roleSelect) {
        roleSelect.addEventListener("change", function() {
            doctorField.style.display = this.value === "2" ? "block" : "none";
        });
    }

    // Form validation helpers
    function showErrorMessage(field, message) {
        clearErrorMessage(field);
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

    // Main form validation
    function validateForm(e) {
        e.preventDefault(); // Always prevent default initially
        
        // Clear all previous error messages
        document.querySelectorAll('.error-message').forEach(el => el.remove());

        let isValid = true;
        const fields = {
            fullName: document.getElementById("full_name"),
            phone: document.getElementById("phone"),
            email: document.getElementById("email"),
            dob: document.getElementById("dob"),
            password: document.getElementById("password"),
            role: document.getElementById("role")
        };

        // Basic field validation
        if (!fields.fullName.value.trim()) {
            showErrorMessage(fields.fullName, "Name is required.");
            isValid = false;
        }

        if (!validatePhone(fields.phone)) {
            showErrorMessage(fields.phone, "Please enter a valid Indian phone number.");
            isValid = false;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(fields.email.value.trim())) {
            showErrorMessage(fields.email, "Please enter a valid email address.");
            isValid = false;
        }

        if (!fields.dob.value) {
            showErrorMessage(fields.dob, "Date of birth is required.");
            isValid = false;
        }

        if (fields.password.value.length < 8) {
            showErrorMessage(fields.password, "Password must be at least 8 characters long.");
            isValid = false;
        }

        // Doctor-specific validation
        if (fields.role.value === "2") {
            const doctorFields = {
                degree: document.getElementById("degree"),
                specialization: document.getElementById("specialization"),
                experience: document.getElementById("experience"),
                address: document.getElementById("address")
            };

            Object.entries(doctorFields).forEach(([key, field]) => {
                if (!field.value.trim()) {
                    showErrorMessage(field, `${key.charAt(0).toUpperCase() + key.slice(1)} is required for doctors.`);
                    isValid = false;
                }
            });
        }

        if (isValid) {
            // If validation passes, submit the form
            signUpForm.submit();
        } else {
            // Scroll to first error
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