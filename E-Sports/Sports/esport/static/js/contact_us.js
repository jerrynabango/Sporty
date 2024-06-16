document.addEventListener('DOMContentLoaded', function() {
    const successMessage = document.getElementById('success-message');
    const errorMessage = document.getElementById('error-message');

    if (successMessage.innerText !== '') {
        showAndHideMessage(successMessage);
    }

    if (errorMessage.innerText !== '') {
        showAndHideMessage(errorMessage);
    }
});

function showAndHideMessage(messageElement) {
    messageElement.style.display = 'block';

    setTimeout(function() {
        messageElement.style.display = 'none';
    }, 3000);
}
