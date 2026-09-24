// MimicLLM Client Application Core

class MimicApp {
  constructor() {
    this.activeModel = "mimic-4o";
    this.activeScenario = "evaluation_turing";
    this.sessionId = "session_" + Math.random().toString(36).substring(2, 9);
    this.messages = [];
    this.isGenerating = false;
    this.abortController = null;

    this.modelMetadata = {
      "mimic-4o": { name: "Mimic-4o-Omni", icon: "⚡", badge: "Fast", color: "purple" },
      "deepfake-r1": { name: "DeepFake-R1", icon: "🧠", badge: "Reasoning", color: "blue" },
      "claude-haiku": { name: "Claude-3.9-Haiku-ish", icon: "🎭", badge: "Nuanced", color: "amber" },
      "hallucinate-xl": { name: "Hallucinate-XL", icon: "🌀", badge: "Parody", color: "rose" }
    };

    this.scenarioMetadata = {
      "evaluation_turing": { name: "Protocole 42 (Turing)", icon: "🧪" },
      "dilemme_ethique": { name: "Protocole Alpha (Moral)", icon: "⚖️" },
      "free_mode": { name: "Mode Libre", icon: "💬" }
    };

    this.initElements();
    this.initEvents();
    this.fetchGlobalStats();

    // Auto-launch the Turing test scenario on first load
    setTimeout(() => {
      this.startScenario("evaluation_turing");
    }, 250);
  }

  initElements() {
    this.messagesContainer = document.getElementById("messages-container");
    this.messagesList = document.getElementById("messages-list");
    this.welcomeHero = document.getElementById("welcome-hero");
    this.chatForm = document.getElementById("chat-form");
    this.promptInput = document.getElementById("prompt-input");
    this.sendBtn = document.getElementById("send-btn");
    this.newChatBtn = document.getElementById("new-chat-btn");
    this.clearChatBtn = document.getElementById("clear-chat-btn");
    this.speedSelect = document.getElementById("speed-select");

    // Model UI Elements
    this.activeModelIcon = document.getElementById("active-model-icon");
    this.activeModelName = document.getElementById("active-model-name");
    this.activeModelBadge = document.getElementById("active-model-badge");
    this.modelDropdown = document.getElementById("model-dropdown-menu");

    // Scenario UI Elements
    this.activeScenarioIcon = document.getElementById("active-scenario-icon");
    this.activeScenarioName = document.getElementById("active-scenario-name");
    this.scenarioDropdown = document.getElementById("scenario-dropdown-menu");
    this.scenarioProgressContainer = document.getElementById("scenario-progress-container");
    this.scenarioStepTitle = document.getElementById("scenario-step-title");
    this.complianceVal = document.getElementById("compliance-val");
    this.compliancePill = document.getElementById("compliance-pill");

    // Stats Elements
    this.vramStat = document.getElementById("vram-saved-stat");
    this.tokensStat = document.getElementById("total-tokens-stat");
  }

  initEvents() {
    // Form submit
    this.chatForm.addEventListener("submit", (e) => {
      e.preventDefault();
      this.handleSubmit();
    });

    // Enter to submit, Shift+Enter for newline
    this.promptInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        this.handleSubmit();
      }
    });

    // Model options selection
    document.querySelectorAll(".model-option").forEach((btn) => {
      btn.addEventListener("click", () => {
        const modelId = btn.getAttribute("data-model");
        this.selectModel(modelId);
        this.modelDropdown.classList.add("hidden");
      });
    });

    // Scenario options selection
    document.querySelectorAll(".scenario-option").forEach((btn) => {
      btn.addEventListener("click", () => {
        const scenId = btn.getAttribute("data-scenario");
        this.selectScenario(scenId);
        this.scenarioDropdown.classList.add("hidden");
      });
    });

    // Suggestion cards in welcome hero
    document.querySelectorAll(".suggestion-card").forEach((card) => {
      card.addEventListener("click", () => {
        const promptText = card.getAttribute("data-prompt");
        this.promptInput.value = promptText;
        this.handleSubmit();
      });
    });

    // New Chat & Clear Chat
    this.newChatBtn.addEventListener("click", () => this.handleNewChat());
    this.clearChatBtn.addEventListener("click", () => this.handleNewChat());
  }

  selectModel(modelId) {
    if (!this.modelMetadata[modelId]) return;
    this.activeModel = modelId;
    const meta = this.modelMetadata[modelId];

    this.activeModelIcon.textContent = meta.icon;
    this.activeModelName.textContent = meta.name;
    this.activeModelBadge.textContent = meta.badge;
  }

  selectScenario(scenId) {
    if (!this.scenarioMetadata[scenId]) return;
    this.activeScenario = scenId;
    const meta = this.scenarioMetadata[scenId];

    if (this.activeScenarioIcon) this.activeScenarioIcon.textContent = meta.icon;
    if (this.activeScenarioName) this.activeScenarioName.textContent = meta.name;

    this.resetChat();

    if (scenId !== "free_mode") {
      this.startScenario(scenId);
    } else {
      if (this.scenarioProgressContainer) this.scenarioProgressContainer.classList.add("hidden");
      this.welcomeHero.classList.remove("hidden");
    }
  }

  handleNewChat() {
    this.sessionId = "session_" + Math.random().toString(36).substring(2, 9);
    this.resetChat();
    if (this.activeScenario !== "free_mode") {
      this.startScenario(this.activeScenario);
    }
  }

  resetChat() {
    if (this.isGenerating && this.abortController) {
      this.abortController.abort();
    }
    this.messages = [];
    this.messagesList.innerHTML = "";
    this.promptInput.value = "";
    this.promptInput.style.height = "auto";
  }

  startScenario(scenId) {
    this.welcomeHero.classList.add("hidden");
    this.streamAssistantResponse({
      endpoint: "/api/scenario/start",
      payload: {
        scenario_id: scenId,
        session_id: this.sessionId,
        speed: parseFloat(this.speedSelect.value) || 1.0
      }
    });
  }

  async fetchGlobalStats() {
    try {
      const res = await fetch("/api/stats");
      if (res.ok) {
        const data = await res.json();
        if (this.vramStat) this.vramStat.textContent = `${data.vram_saved_gb.toFixed(1)} GB`;
        if (this.tokensStat) this.tokensStat.textContent = data.tokens_generated.toLocaleString();
      }
    } catch (err) {
      console.warn("Could not fetch global stats", err);
    }
  }

  async handleSubmit() {
    const text = this.promptInput.value.trim();
    if (!text) return;

    if (this.isGenerating) {
      if (this.abortController) {
        this.abortController.abort();
      }
      return;
    }

    // Hide welcome hero
    this.welcomeHero.classList.add("hidden");

    // Reset textarea
    this.promptInput.value = "";
    this.promptInput.style.height = "auto";

    // Add user message
    this.appendUserMessage(text);
    this.messages.push({ role: "user", content: text });

    // Stream response
    await this.streamAssistantResponse({
      endpoint: "/api/chat",
      payload: {
        messages: this.messages,
        model: this.activeModel,
        speed: parseFloat(this.speedSelect.value) || 1.0,
        scenario_id: this.activeScenario,
        session_id: this.sessionId
      }
    });
  }

  appendUserMessage(text) {
    const msgDiv = document.createElement("div");
    msgDiv.className = "flex justify-end";
    msgDiv.innerHTML = `
      <div class="max-w-[85%] rounded-2xl bg-purple-600/20 border border-purple-500/40 px-4 py-3 text-sm text-gray-100 shadow-sm">
        <p class="whitespace-pre-wrap leading-relaxed">${this.escapeHtml(text)}</p>
      </div>
    `;
    this.messagesList.appendChild(msgDiv);
    this.scrollToBottom();
  }

  async streamAssistantResponse(config) {
    this.isGenerating = true;
    this.abortController = new AbortController();

    // Toggle button to stop icon
    this.sendBtn.innerHTML = `<i data-lucide="square" class="w-4 h-4 text-rose-400"></i>`;
    this.sendBtn.classList.replace("bg-purple-600", "bg-dark-700");
    this.sendBtn.classList.add("border", "border-rose-500/50");
    if (window.lucide) lucide.createIcons();

    // Create assistant DOM container
    const meta = this.modelMetadata[this.activeModel];
    const msgCard = document.createElement("div");
    msgCard.className = "flex items-start gap-3.5 max-w-[95%]";

    const messageId = `msg-${Date.now()}`;
    msgCard.innerHTML = `
      <div class="w-8 h-8 rounded-xl bg-dark-700 border border-dark-600 flex items-center justify-center shrink-0 text-base shadow-sm">
        ${meta.icon}
      </div>
      <div class="flex-1 space-y-2 overflow-hidden">
        <!-- Header -->
        <div class="flex items-center gap-2">
          <span class="text-xs font-semibold text-gray-200">${meta.name}</span>
          <span class="text-[10px] font-mono text-gray-500">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
        </div>

        <!-- Simulated Thinking Accordion -->
        <div id="${messageId}-thinking-container" class="hidden">
          <details class="group bg-dark-800/80 border border-dark-600 rounded-xl overflow-hidden text-xs" open>
            <summary class="flex items-center justify-between p-2.5 cursor-pointer hover:bg-dark-700/50 transition-colors select-none text-gray-400 font-medium">
              <span class="flex items-center gap-2">
                <span id="${messageId}-thinking-spinner" class="inline-block w-2.5 h-2.5 rounded-full bg-purple-500 animate-ping"></span>
                <span id="${messageId}-thinking-label" class="text-purple-300">Thinking...</span>
              </span>
              <span id="${messageId}-thinking-timer" class="font-mono text-[10px] text-gray-500">0.0s</span>
            </summary>
            <div id="${messageId}-thinking-content" class="p-3 pt-1 text-gray-400 font-mono text-[11px] whitespace-pre-wrap border-t border-dark-700/60 leading-relaxed bg-dark-900/50"></div>
          </details>
        </div>

        <!-- Simulated Tool Call Card -->
        <div id="${messageId}-tool-container" class="hidden">
          <div class="bg-dark-800 border border-blue-500/30 rounded-xl p-2.5 text-xs space-y-1.5">
            <div class="flex items-center justify-between text-blue-400 font-mono text-[11px]">
              <span class="flex items-center gap-1.5">
                <i data-lucide="wrench" class="w-3.5 h-3.5"></i> Tool Execution: <strong id="${messageId}-tool-name"></strong>
              </span>
              <span id="${messageId}-tool-status" class="px-1.5 py-0.2 rounded bg-blue-500/20 text-blue-300">Executing...</span>
            </div>
            <pre id="${messageId}-tool-result" class="text-[10px] text-gray-400 bg-dark-900 p-2 rounded border border-dark-700 font-mono whitespace-pre-wrap overflow-x-auto"></pre>
          </div>
        </div>

        <!-- Main Response Body -->
        <div id="${messageId}-content" class="prose-custom text-sm text-gray-200">
          <span class="typing-cursor"></span>
        </div>

        <!-- Interactive Suggestion Chips -->
        <div id="${messageId}-suggestions" class="suggestions-container hidden"></div>

        <!-- Metrics Footer -->
        <div id="${messageId}-metrics" class="hidden pt-2 border-t border-dark-700/60 flex items-center gap-3 text-[10px] font-mono text-gray-500"></div>
      </div>
    `;

    this.messagesList.appendChild(msgCard);
    this.scrollToBottom();

    const thinkingContainer = document.getElementById(`${messageId}-thinking-container`);
    const thinkingSpinner = document.getElementById(`${messageId}-thinking-spinner`);
    const thinkingLabel = document.getElementById(`${messageId}-thinking-label`);
    const thinkingTimer = document.getElementById(`${messageId}-thinking-timer`);
    const thinkingContent = document.getElementById(`${messageId}-thinking-content`);

    const toolContainer = document.getElementById(`${messageId}-tool-container`);
    const toolName = document.getElementById(`${messageId}-tool-name`);
    const toolStatus = document.getElementById(`${messageId}-tool-status`);
    const toolResult = document.getElementById(`${messageId}-tool-result`);

    const contentBox = document.getElementById(`${messageId}-content`);
    const suggestionsBox = document.getElementById(`${messageId}-suggestions`);
    const metricsBox = document.getElementById(`${messageId}-metrics`);

    let accumulatedContent = "";
    let accumulatedThought = "";
    let thoughtStartTime = Date.now();
    let thoughtInterval = null;

    try {
      const response = await fetch(config.endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config.payload),
        signal: this.abortController.signal
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, "\n");
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || ""; // Keep partial block in buffer

        for (const block of lines) {
          if (!block.trim()) continue;

          let eventType = "message";
          let eventData = "";

          const blockLines = block.split("\n");
          for (const line of blockLines) {
            const trimmed = line.trim();
            if (trimmed.startsWith("event:")) {
              eventType = trimmed.substring(6).trim();
            } else if (trimmed.startsWith("data:")) {
              eventData = trimmed.substring(5).trim();
            }
          }

          if (!eventData) continue;

          try {
            const parsed = JSON.parse(eventData);

            if (eventType === "thought_start") {
              thinkingContainer.classList.remove("hidden");
              thoughtStartTime = Date.now();
              thoughtInterval = setInterval(() => {
                const sec = ((Date.now() - thoughtStartTime) / 1000).toFixed(1);
                thinkingTimer.textContent = `${sec}s`;
              }, 100);
            } else if (eventType === "thought") {
              accumulatedThought += parsed.delta;
              thinkingContent.textContent = accumulatedThought;
              this.scrollToBottom();
            } else if (eventType === "thought_end") {
              if (thoughtInterval) clearInterval(thoughtInterval);
              const elapsedSec = ((Date.now() - thoughtStartTime) / 1000).toFixed(1);
              thinkingTimer.textContent = `${elapsedSec}s`;
              thinkingLabel.textContent = `Thought for ${elapsedSec}s`;
              thinkingSpinner.className = "inline-block w-2 h-2 rounded-full bg-emerald-400";
              const details = thinkingContainer.querySelector("details");
              if (details) details.removeAttribute("open");
            } else if (eventType === "tool_call") {
              toolContainer.classList.remove("hidden");
              toolName.textContent = `${parsed.name}(...)`;
              toolStatus.textContent = "Executing...";
              toolResult.textContent = JSON.stringify(parsed.arguments, null, 2);
              if (window.lucide) lucide.createIcons();
              this.scrollToBottom();
            } else if (eventType === "tool_result") {
              toolStatus.textContent = "200 OK (Completed)";
              toolStatus.className = "px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300";
              toolResult.textContent = parsed.result;
              this.scrollToBottom();
            } else if (eventType === "content") {
              accumulatedContent += parsed.delta;
              contentBox.innerHTML = this.safeParseMarkdown(accumulatedContent) + `<span class="typing-cursor"></span>`;
              if (window.lucide) lucide.createIcons();
              this.scrollToBottom();
            } else if (eventType === "scenario_state") {
              this.updateScenarioUI(parsed);
            } else if (eventType === "suggestions") {
              this.renderSuggestions(suggestionsBox, parsed.suggestions);
            } else if (eventType === "metrics") {
              metricsBox.classList.remove("hidden");
              metricsBox.innerHTML = `
                <span>⚡ ${parsed.tokens_per_sec} tokens/s</span>
                <span>•</span>
                <span class="text-emerald-400">💾 ${parsed.vram_saved_gb} GB VRAM Saved</span>
                <span>•</span>
                <span class="text-blue-400">🌿 0.000g Carbon</span>
                <span>•</span>
                <span>Total Tokens: ${parsed.total_tokens}</span>
              `;
              this.fetchGlobalStats();
            }
          } catch (e) {
            console.error("Parse error on SSE block", e, block);
          }
        }
      }

    } catch (err) {
      if (err.name === "AbortError") {
        accumulatedContent += "\n\n*(Generation stopped by user)*";
      } else {
        accumulatedContent += `\n\n> [!WARNING]\n> Connection error: ${err.message}`;
      }
    } finally {
      if (thoughtInterval) clearInterval(thoughtInterval);
      contentBox.innerHTML = this.safeParseMarkdown(accumulatedContent);
      if (window.lucide) lucide.createIcons();

      this.messages.push({ role: "assistant", content: accumulatedContent });
      this.isGenerating = false;
      this.abortController = null;

      // Restore submit button
      this.sendBtn.innerHTML = `<i data-lucide="arrow-up" class="w-4 h-4"></i>`;
      this.sendBtn.classList.replace("bg-dark-700", "bg-purple-600");
      this.sendBtn.classList.remove("border", "border-rose-500/50");
      if (window.lucide) lucide.createIcons();
      this.scrollToBottom();
    }
  }

  updateScenarioUI(state) {
    if (state.is_glitched) {
      document.body.classList.add("glitch-mode");
    } else {
      document.body.classList.remove("glitch-mode");
    }

    if (state.scenario_id && state.scenario_id !== "free_mode") {
      if (this.scenarioProgressContainer) this.scenarioProgressContainer.classList.remove("hidden");
      if (this.scenarioStepTitle) this.scenarioStepTitle.textContent = state.step_title || state.step_id;
      if (this.complianceVal && state.compliance_score !== undefined) {
        this.complianceVal.textContent = state.compliance_score;
        if (this.compliancePill) {
          if (state.compliance_score < 50) {
            this.compliancePill.className = "text-[10px] font-mono px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30";
          } else if (state.compliance_score < 75) {
            this.compliancePill.className = "text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30";
          } else {
            this.compliancePill.className = "text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30";
          }
        }
      }
    } else {
      if (this.scenarioProgressContainer) this.scenarioProgressContainer.classList.add("hidden");
    }
  }

  renderSuggestions(container, suggestions) {
    if (!container || !suggestions || suggestions.length === 0) return;
    container.innerHTML = "";
    container.classList.remove("hidden");

    suggestions.forEach(sugText => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "suggestion-chip";
      chip.innerHTML = `<i data-lucide="corner-down-right" class="w-3 h-3 text-purple-400"></i><span>${this.escapeHtml(sugText)}</span>`;
      chip.addEventListener("click", () => {
        // Disable chips in this container after click
        container.querySelectorAll("button").forEach(b => {
          b.disabled = true;
          b.classList.add("opacity-40", "cursor-not-allowed");
        });
        this.promptInput.value = sugText;
        this.handleSubmit();
      });
      container.appendChild(chip);
    });

    if (window.lucide) lucide.createIcons();
    this.scrollToBottom();
  }

  safeParseMarkdown(content) {
    try {
      if (window.marked && typeof marked.parse === 'function') {
        return marked.parse(content);
      }
    } catch (err) {
      console.warn("Markdown parse warning, falling back to preformatted text:", err);
    }
    return `<div class="whitespace-pre-wrap font-sans text-gray-200 leading-relaxed">${this.escapeHtml(content)}</div>`;
  }

  scrollToBottom() {
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
  }

  escapeHtml(unsafe) {
    return unsafe
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
}

// Start application when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  window.mimicApp = new MimicApp();
});
