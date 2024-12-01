console.log("re login is at least seen");
document.addEventListener('DOMContentLoaded', function () {
    console.log('re_login is loaded after dom is loaded.');
    grecaptcha.ready(function() {
        console.log("passed checkpoint 1");
        grecaptcha.execute('{{ recaptcha_site_key }}', {action: 'login'}).then(function(token) {
            console.log("passed checkpoint 2");

            const tokenField = document.getElementById('id_recaptcha_token');
            if (tokenField) {
                tokenField.value = token;
                console.log('Token assigned successfully.');
            } else {
                console.error('Hidden input field not found!');
            }
        });
    });
});