const chatBox = document.getElementById("chat-box");

function addMessage(content, sender) {
    const div = document.createElement("div");
    div.className = `message ${sender}`;

    if (sender === "bot") {
        div.innerHTML = marked.parse(content);

        // highlight code
        div.querySelectorAll("pre code").forEach((block) => {
            hljs.highlightElement(block);

            // add copy button
            const btn = document.createElement("button");
            btn.innerText = "Copy";
            btn.className = "copy-btn";

            btn.onclick = () => {
                navigator.clipboard.writeText(block.innerText);
                btn.innerText = "Copied!";
                setTimeout(() => btn.innerText = "Copy", 1500);
            };

            block.parentElement.appendChild(btn);
        });
    } else {
        div.innerText = content;
    }

    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;

    return div;
}

/* Typing animation (streaming effect) */
async function typeText(element, text) {
    let current = "";

    for (let char of text) {
        current += char;
        element.innerHTML = marked.parse(current);
        chatBox.scrollTop = chatBox.scrollHeight;
        await new Promise(r => setTimeout(r, 10)); // speed
    }
}

async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();
    if (!message) return;

    addMessage(message, "user");
    input.value = "";

    const botDiv = document.createElement("div");
    botDiv.className = "message bot";
    chatBox.appendChild(botDiv);

    const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    });

    const data = await res.json();

    // typing animation
    await typeText(botDiv, data.response);

    // re-apply code highlighting + copy
    botDiv.querySelectorAll("pre code").forEach((block) => {
        hljs.highlightElement(block);

        const btn = document.createElement("button");
        btn.innerText = "Copy";
        btn.className = "copy-btn";

        btn.onclick = () => {
            navigator.clipboard.writeText(block.innerText);
            btn.innerText = "Copied!";
            setTimeout(() => btn.innerText = "Copy", 1500);
        };

        block.parentElement.appendChild(btn);
    });
}
