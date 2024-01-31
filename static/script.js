<script>
    // Function to validate the login form
    function validateLoginForm() {
        var username = document.getElementById('username').value;
        var password = document.getElementById('password').value;

        if (username === '' || password === '') {
            alert('Please fill in all fields.');
            return false;
        }
        return true;
    }

    // Function to validate the registration form
    function validateRegistrationForm() {
        var username = document.getElementById('username').value;
        var password = document.getElementById('password').value;

        if (username === '' || password === '') {
            alert('Please fill in all fields.');
            return false;
        }
        return true;
    }

    // Function to display a success message
    function showSuccessMessage(message) {
        alert(message);
    }
</script>
