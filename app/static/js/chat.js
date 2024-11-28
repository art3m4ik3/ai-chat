class ChatUI {
    constructor() {
        this.chatContainer = document.getElementById("chat-container");
        this.messageInput = document.getElementById("message-input");
        this.sendBtn = document.getElementById("send-btn");
        this.loadingIndicator = document.getElementById("loading");
        this.messages = [];

        this.initEventListeners();
    }

    initEventListeners() {
        this.sendBtn.addEventListener("click", this.sendMessage.bind(this));
        this.messageInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }

    async sendMessage() {
        const userMessage = this.messageInput.value.trim();
        if (!userMessage) return;

        this.addMessage("user", userMessage);
        this.messageInput.value = "";
        this.toggleInputState(false);
        this.showLoading(true);

        try {
            const response = await this.fetchAIResponse(userMessage);
            this.addMessage("ai", response);
        } catch (error) {
            this.addMessage("error", "Ошибка сети. Попробуйте еще раз.");
            console.error("Chat error:", error);
        } finally {
            this.toggleInputState(true);
            this.showLoading(false);
        }
    }

    showLoading(show) {
        this.loadingIndicator.classList.toggle("hidden", !show);
    }

    toggleInputState(enabled) {
        this.messageInput.disabled = !enabled;
        this.sendBtn.disabled = !enabled;
    }

    async fetchAIResponse(userMessage) {
        this.messages.push({ role: "user", content: userMessage });

        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ messages: this.messages }),
        });

        if (!response.ok) {
            throw new Error("Network response was not ok");
        }

        const data = await response.json();
        this.messages.push({ role: "assistant", content: data.response });
        return data.response;
    }

    addMessage(sender, message) {
        const messageEl = document.createElement("div");

        messageEl.classList.add("p-2", "my-2", "rounded-lg", "max-w-[80%]");

        if (sender === "user") {
            messageEl.classList.add(
                "self-end",
                "bg-blue-500",
                "text-white",
                "ml-auto"
            );
        } else if (sender === "error") {
            messageEl.classList.add("bg-red-500", "text-white");
        } else {
            messageEl.classList.add("self-start", "bg-gray-200");
        }

        messageEl.textContent = message;
        this.chatContainer.appendChild(messageEl);
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }
}

document.addEventListener("DOMContentLoaded", () => new ChatUI());
