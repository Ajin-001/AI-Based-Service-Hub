document.addEventListener("DOMContentLoaded", function () {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendButton = document.getElementById("send-btn");

    // Function to append a message to the chat box
    function appendMessage(sender, message) {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add(sender === "bot" ? "bot-message" : "user-message");
        msgDiv.textContent = message;
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the bottom
    }

    // Function to send a message to the chatbot
    function sendMessage() {
        const message = userInput.value.trim();
        if (message === "") return;

        appendMessage("user", message); // Add the user's message to the chat box
        userInput.value = ""; // Clear the input field

        // Send the message to the chatbot API
        fetch("/api/chatbot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Received response:", data); // Debugging
            if (data.redirect) {
                // Redirect to the specified URL (e.g., /appointment)
                window.location.href = data.redirect;
            } else {
                // Add the bot's response to the chat box
                appendMessage("bot", data.response);
            }
        })
        .catch(error => {
            appendMessage("bot", "⚠️ Error: Could not connect.");
            console.error("Error:", error);
        });
    }

    // Event listener for the send button
    sendButton.addEventListener("click", sendMessage);

    // Event listener for the Enter key
    userInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") sendMessage();
    });
});