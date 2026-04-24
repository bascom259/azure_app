const input = document.getElementById("msg");

input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        send();
    }
});

async function send() {
    let text = input.value.trim();
    if (!text) return;

    addMessage("👤 " + text, "user");
    input.value = "";

    let botMsg = addMessage("🤖 Typing...", "bot");

    const res = await fetch("/chat-stream", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: text})
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder();

    botMsg.innerText = "🤖 ";

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        botMsg.innerText += decoder.decode(value);
    }
}

function addMessage(text, type) {
    let chat = document.getElementById("chat");

    let div = document.createElement("div");
    div.className = "msg " + type;
    div.innerText = text;

    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;

    return div;
}
