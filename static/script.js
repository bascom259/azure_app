async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();

    if (!message) return;

    const chatBox = document.getElementById("chat-box");

    // User message
    const userDiv = document.createElement("div");
    userDiv.className = "message user-message";
    userDiv.innerText = message;
    chatBox.appendChild(userDiv);

    input.value = "";

    // Bot typing indicator
    const botDiv = document.createElement("div");
    botDiv.className = "message bot-message";
    botDiv.innerText = "Typing...";
    chatBox.appendChild(botDiv);

    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message })
        });

        const data = await res.json();

        // Convert Markdown → HTML
        botDiv.innerHTML = marked.parse(data.response);

    } catch (err) {
        botDiv.innerText = "Error: Could not connect.";
    }

    chatBox.scrollTop = chatBox.scrollHeight;
}
