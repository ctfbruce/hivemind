document.addEventListener('DOMContentLoaded', function () {
    console.log("main.js is logged after dom content loaded");
    const newPostButton = document.getElementById('new-post-button');
    const newPostFormContainer = document.getElementById('new-post-form-container');

    newPostButton.addEventListener('click', function () {
        // Toggle the display of the new post form
        console.log("i am pressed");
        if (newPostFormContainer.style.display === 'none') {
            newPostFormContainer.style.display = 'block';
        } else {
            newPostFormContainer.style.display = 'none';
        }
    });
});