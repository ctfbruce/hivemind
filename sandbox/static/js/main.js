document.addEventListener('DOMContentLoaded', function () {
    console.log("main.js is logged after dom content loaded");
    const newPostButton = document.getElementById('new-post-button');
    const newPostFormContainer = document.getElementById('new-post-form-container');

    console.log("the site key is", JSON.parse(document.getElementById('recaptcha_site_key').textContent));

    newPostButton.addEventListener('click', function () {
        // Toggle the display of the new post form
        console.log("i am pressed");
        if (newPostFormContainer.style.display === 'none') {
            newPostFormContainer.style.display = 'block';
        } else {
            newPostFormContainer.style.display = 'none';
        }
    });
    let recaptchaToken = '';

        // Generate the reCAPTCHA token when the page loads
    grecaptcha.ready(function() {
        grecaptcha.execute(JSON.parse(document.getElementById('recaptcha_site_key').textContent), { action: 'page_load' }).then(function(token) {
            recaptchaToken = token;  // Store the token globally
            });
        });

        // Function to get a fresh token dynamically
    function getRecaptchaToken(actionName, callback) {
        grecaptcha.execute(JSON.parse(document.getElementById('recaptcha_site_key').textContent), { action: actionName }).then(function(token) {
            callback(token);
            });
        }



});
