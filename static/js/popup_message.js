document.addEventListener('DOMContentLoaded', function() {
    var messageContainer = document.getElementById('popup-message-container');

    messagesData.forEach(function(message) {
        var messageElement = document.createElement('div');
        messageElement.classList.add('popup-message', message.tags);
        messageElement.textContent = message.message;

        messageContainer.appendChild(messageElement);

        // Show the message
        setTimeout(function() {
            messageElement.style.display = 'block';
            messageElement.style.opacity = '1';
        }, 100); // Slight delay to ensure the message is appended

        // Hide the message after a delay
        setTimeout(function() {
            messageElement.style.opacity = '0';
            setTimeout(function() {
                messageElement.style.display = 'none';
                messageContainer.removeChild(messageElement);
            }, 600); // Delay to allow the fade-out transition
        }, 5000); // Display the popup for 5 seconds
    });
});
