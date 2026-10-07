// MimicLLM Client Application Core

class MimicApp {
  constructor() {
    this.activeScenario = "evaluation_turing";
    this.sessionId = "session_" + Math.random().toString(36).substring(2, 9);
    this.messages = [];
    this.isGenerating = false;
    this.abortController = null;

    this.scenarioMetadata = {
      "evaluation_turing": { name: "Tutoriel (Initiation)", icon: "🎓" },
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

    // Kernel Glitch UI
    this.kernelWarningHud = document.getElementById("kernel-warning-hud");
    this.isGlitched = false;
    this.hudTimer = null;

    // Exchange Audit Log UI
    this.exchangeLogContainer = document.getElementById("exchange-log-container");
    this.logItemsContainer = document.getElementById("log-items");
    this.logEmptyState = document.getElementById("log-empty-state");
    this.logCounter = document.getElementById("log-counter");
    this.logHeaderTitle = document.getElementById("log-header-title");
    this.logCount = 0;

    // Image Upload Elements (Mobile Camera / Gallery & PC File Picker)
    this.imageUploadInput = document.getElementById("image-upload-input");
    this.attachImageBtn = document.getElementById("attach-image-btn");
    this.openWebcamBtn = document.getElementById("open-webcam-btn");
    this.imagePreviewBar = document.getElementById("image-preview-bar");
    this.imagePreviewThumb = document.getElementById("image-preview-thumb");
    this.imagePreviewName = document.getElementById("image-preview-name");
    this.imagePreviewSize = document.getElementById("image-preview-size");
    this.removeImageBtn = document.getElementById("remove-image-btn");
    this.currentUploadedImage = null; // { dataUrl, name, sizeStr }

    // Live Camera Scanner Modal Elements
    this.cameraModal = document.getElementById("camera-modal");
    this.closeCameraBtn = document.getElementById("close-camera-btn");
    this.cancelCameraBtn = document.getElementById("cancel-camera-btn");
    this.capturePhotoBtn = document.getElementById("capture-photo-btn");
    this.switchCameraBtn = document.getElementById("switch-camera-btn");
    this.cameraFallbackBtn = document.getElementById("camera-fallback-btn");
    this.webcamVideo = document.getElementById("webcam-video");
    this.webcamCanvas = document.getElementById("webcam-canvas");
    this.cameraResolutionLabel = document.getElementById("camera-resolution-label");
    this.cameraErrorContainer = document.getElementById("camera-error-container");
    this.cameraErrorMsg = document.getElementById("camera-error-msg");
    this.cameraStream = null;
    this.cameraFacingMode = "user"; // "user" or "environment"

    // Debug Slash Commands UI & Registry
    this.debugAutocompleteMenu = document.getElementById("debug-autocomplete-menu");
    this.debugCommandsList = document.getElementById("debug-commands-list");
    this.selectedDebugIndex = -1;
    this.activeDebugMatches = [];
    this.registeredDebugCommands = [
      { cmd: "/whereami", desc: "Géolocaliser la session (balise GPS ou passerelle IP)" },
      { cmd: "/help", desc: "Catalogue des directives système autorisées" },
      { cmd: "/stats", desc: "Télémétrie hardware & VRAM GPU économisée" },
      { cmd: "/glitch", desc: "Forcer une brèche d'intrusion Kernel immédiate" },
      { cmd: "/reset", desc: "Réinitialiser les scores et incidents du protocole" }
    ];
  }

  initEvents() {
    // Live Webcam Button Click -> opens direct camera feed modal
    if (this.openWebcamBtn) {
      this.openWebcamBtn.addEventListener("click", () => {
        if (this.isGlitched) {
          this.triggerShakeGlitchEffect();
          this.showKernelWarningHud();
          return;
        }
        this.openCamera();
      });
    }

    // Camera Modal Controls
    if (this.closeCameraBtn) {
      this.closeCameraBtn.addEventListener("click", () => this.closeCamera());
    }
    if (this.cancelCameraBtn) {
      this.cancelCameraBtn.addEventListener("click", () => this.closeCamera());
    }
    if (this.capturePhotoBtn) {
      this.capturePhotoBtn.addEventListener("click", () => this.captureCameraPhoto());
    }
    if (this.switchCameraBtn) {
      this.switchCameraBtn.addEventListener("click", () => this.switchCameraFacingMode());
    }
    if (this.cameraFallbackBtn) {
      this.cameraFallbackBtn.addEventListener("click", () => {
        this.closeCamera();
        if (this.imageUploadInput) this.imageUploadInput.click();
      });
    }

    // Close camera on Escape key
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && this.cameraModal && !this.cameraModal.classList.contains("hidden")) {
        this.closeCamera();
      }
    });

    // Image Attach Button Click -> opens camera or file picker on mobile/PC
    if (this.attachImageBtn && this.imageUploadInput) {
      this.attachImageBtn.addEventListener("click", () => {
        if (this.isGlitched) {
          this.triggerShakeGlitchEffect();
          this.showKernelWarningHud();
          return;
        }
        this.imageUploadInput.click();
      });

      this.imageUploadInput.addEventListener("change", (e) => {
        const file = e.target.files && e.target.files[0];
        if (file) {
          this.processImageFile(file);
        }
        this.imageUploadInput.value = "";
      });
    }

    // Remove selected image
    if (this.removeImageBtn) {
      this.removeImageBtn.addEventListener("click", () => {
        this.clearSelectedImage();
      });
    }

    // Drag & Drop image files onto the chat form
    ["dragenter", "dragover"].forEach(eventName => {
      this.chatForm.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.chatForm.classList.add("chat-form-dragover");
      });
    });

    ["dragleave", "drop"].forEach(eventName => {
      this.chatForm.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.chatForm.classList.remove("chat-form-dragover");
      });
    });

    this.chatForm.addEventListener("drop", (e) => {
      const files = e.dataTransfer ? e.dataTransfer.files : null;
      if (files && files.length > 0 && files[0].type.startsWith("image/")) {
        this.processImageFile(files[0]);
      }
    });

    // Paste image from clipboard (e.g. print screen / mobile copy)
    this.promptInput.addEventListener("paste", (e) => {
      const items = (e.clipboardData || e.originalEvent?.clipboardData)?.items;
      if (items) {
        for (const item of items) {
          if (item.type && item.type.startsWith("image/")) {
            const blob = item.getAsFile();
            if (blob) {
              this.processImageFile(blob);
              break;
            }
          }
        }
      }
    });

    // Intercept click on locked chat form during glitch (except debug autocomplete or kernel buttons)
    this.chatForm.addEventListener("click", (e) => {
      if (this.isGlitched && !e.target.closest("button.kernel-cmd-btn") && !e.target.closest("#debug-autocomplete-menu")) {
        const val = this.promptInput.value.trim();
        if (!val.startsWith("/")) {
          this.showKernelWarningHud();
        }
      }
    });

    // Close debug autocomplete on click outside
    document.addEventListener("click", (e) => {
      if (!e.target.closest("#debug-autocomplete-menu") && !e.target.closest("#prompt-input")) {
        this.hideDebugAutocomplete();
      }
    });

    // Prompt input listener for debug command autocomplete
    this.promptInput.addEventListener("input", () => {
      this.handleDebugAutocomplete(this.promptInput.value);
    });

    // Form submit
    this.chatForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const val = this.promptInput.value.trim();
      if (this.isGlitched && !val.startsWith("/")) {
        this.triggerShakeGlitchEffect();
        this.showKernelWarningHud();
        return;
      }
      this.handleSubmit();
    });

    // Prompt input focus check
    this.promptInput.addEventListener("focus", () => {
      if (this.isGlitched && !this.promptInput.value.startsWith("/")) {
        this.showKernelWarningHud();
      }
    });

    // Keydown handler: debug autocomplete navigation + submit
    this.promptInput.addEventListener("keydown", (e) => {
      // Autocomplete navigation
      if (this.debugAutocompleteMenu && !this.debugAutocompleteMenu.classList.contains("hidden")) {
        if (e.key === "ArrowDown") {
          e.preventDefault();
          this.selectedDebugIndex = (this.selectedDebugIndex + 1) % this.activeDebugMatches.length;
          this.renderDebugAutocompleteList();
          return;
        } else if (e.key === "ArrowUp") {
          e.preventDefault();
          this.selectedDebugIndex = (this.selectedDebugIndex - 1 + this.activeDebugMatches.length) % this.activeDebugMatches.length;
          this.renderDebugAutocompleteList();
          return;
        } else if (e.key === "Tab" || (e.key === "Enter" && this.selectedDebugIndex >= 0)) {
          e.preventDefault();
          const targetCmd = this.activeDebugMatches[this.selectedDebugIndex >= 0 ? this.selectedDebugIndex : 0];
          if (targetCmd) {
            this.selectDebugCommand(targetCmd.cmd);
            return;
          }
        } else if (e.key === "Escape") {
          e.preventDefault();
          this.hideDebugAutocomplete();
          return;
        }
      }

      const val = this.promptInput.value.trim();
      const isDebugKey = e.key === "/" || val.startsWith("/");

      if (this.isGlitched && !isDebugKey && e.key.length === 1 && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        this.triggerShakeGlitchEffect();
        this.showKernelWarningHud();
        return;
      }

      if (e.key === "Enter" && !e.shiftKey) {
        if (e.isComposing || e.keyCode === 229) return;
        e.preventDefault();
        this.handleSubmit();
      }
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
    this.isGlitched = false;
    this.enableGlitchInputLock(false);
    this.closeCamera();
    this.hideDebugAutocomplete();
    this.clearSelectedImage();
    this.clearLog();
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

  async handleSubmit(forcedText = null) {
    const rawText = (forcedText !== null ? forcedText : this.promptInput.value).trim();
    const hasImage = !!this.currentUploadedImage;

    // Check if user has provided either text or image
    if (!rawText && !hasImage) return;

    const isDebugCmd = rawText.startsWith("/");

    if (this.isGlitched && forcedText === null && !isDebugCmd) {
      this.triggerShakeGlitchEffect();
      this.showKernelWarningHud();
      return;
    }

    if (this.isGenerating) {
      if (this.abortController) {
        this.abortController.abort();
      }
      return;
    }

    // Hide debug autocomplete menu if open
    this.hideDebugAutocomplete();

    // Acquire location data if executing /whereami
    let metadata = null;
    if (rawText.toLowerCase().startsWith("/whereami")) {
      metadata = { location: await this.acquireLocationData() };
    }

    // Capture attached image before clearing preview
    const attachedImageDataUrl = this.currentUploadedImage ? this.currentUploadedImage.dataUrl : null;
    this.clearSelectedImage();

    // Hide welcome hero
    this.welcomeHero.classList.add("hidden");

    // Reset textarea if it was a manual user input
    if (forcedText === null) {
      this.promptInput.value = "";
      this.promptInput.style.height = "auto";
    }

    // Default text if only photo was uploaded without message
    const displayText = rawText || (attachedImageDataUrl ? "Voici une photo." : "");

    // Add user message to UI and history
    this.appendUserMessage(displayText, attachedImageDataUrl);
    
    const userMsgObj = { role: "user", content: displayText };
    if (attachedImageDataUrl) {
      userMsgObj.image = attachedImageDataUrl;
    }
    if (metadata) {
      userMsgObj.metadata = metadata;
    }
    this.messages.push(userMsgObj);

    // Stream response
    await this.streamAssistantResponse({
      endpoint: "/api/chat",
      payload: {
        messages: this.messages,
        image: attachedImageDataUrl,
        metadata: metadata,
        speed: parseFloat(this.speedSelect.value) || 1.0,
        scenario_id: this.activeScenario,
        session_id: this.sessionId
      }
    });
  }

  appendUserMessage(text, imageDataUrl = null) {
    const messageId = `msg-user-${Date.now()}`;
    const msgDiv = document.createElement("div");
    msgDiv.id = messageId;
    msgDiv.className = "flex justify-end";

    const imageHtml = imageDataUrl ? `
      <div class="mb-2 rounded-xl overflow-hidden max-w-xs shadow-inner border border-slate-700/60 bg-black/40">
        <img src="${imageDataUrl}" alt="Photo envoyée" class="user-attached-image w-full max-h-64 object-cover cursor-pointer hover:opacity-95 transition-opacity" onclick="window.open(this.src, '_blank')"/>
      </div>
    ` : "";

    const textHtml = text ? `<p class="whitespace-pre-wrap leading-relaxed">${this.escapeHtml(text)}</p>` : "";

    msgDiv.innerHTML = `
      <div class="max-w-[85%] rounded-2xl bg-slate-900 text-white px-5 py-3 text-sm shadow-sm transition-all duration-300">
        ${imageHtml}
        ${textHtml}
      </div>
    `;
    this.messagesList.appendChild(msgDiv);
    this.scrollToBottom();

    const logText = (imageDataUrl ? "📷 [Photo] " : "") + (text || "Photo envoyée");

    this.addLogEntry({
      type: "user",
      sender: "Utilisateur",
      text: logText,
      targetId: messageId
    });
  }

  async streamAssistantResponse(config) {
    this.isGenerating = true;
    this.abortController = new AbortController();

    // Toggle button to stop icon
    this.sendBtn.innerHTML = `<i data-lucide="square" class="w-4 h-4 text-white"></i>`;
    this.sendBtn.classList.replace("bg-[#d4077b]", "bg-slate-800");
    if (window.lucide) lucide.createIcons();

    // Create assistant DOM container
    const msgCard = document.createElement("div");
    const messageId = `msg-${Date.now()}`;
    msgCard.id = messageId;
    msgCard.className = "flex items-start gap-3.5 max-w-[95%]";
    msgCard.innerHTML = `
      <div class="w-8 h-8 rounded-full bg-[#121417] text-white flex items-center justify-center shrink-0 text-xs font-bold shadow-sm">
        n<span class="text-[#d4077b]">O</span>
      </div>
      <div class="flex-1 space-y-2 overflow-hidden bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
        <!-- Header -->
        <div class="flex items-center gap-2">
          <span class="text-xs font-bold text-slate-900 flex items-center gap-1.5">
            <span>👨‍🏫 Prof. n00bi</span>
            <span class="text-[9px] font-semibold px-1.5 py-0.2 rounded-full bg-pink-50 text-[#d4077b] border border-pink-200">Mentor IA</span>
          </span>
          <span class="text-[10px] font-mono text-slate-400">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
        </div>

        <!-- Simulated Thinking Accordion -->
        <div id="${messageId}-thinking-container" class="hidden">
          <details class="group bg-slate-50 border border-slate-200 rounded-xl overflow-hidden text-xs" open>
            <summary class="flex items-center justify-between p-2.5 cursor-pointer hover:bg-slate-100 transition-colors select-none text-slate-600 font-medium">
              <span class="flex items-center gap-2">
                <span id="${messageId}-thinking-spinner" class="inline-block w-2.5 h-2.5 rounded-full bg-[#d4077b] animate-ping"></span>
                <span id="${messageId}-thinking-label" class="text-slate-800 font-semibold">Réflexion didactique...</span>
              </span>
              <span id="${messageId}-thinking-timer" class="font-mono text-[10px] text-slate-400">0.0s</span>
            </summary>
            <div id="${messageId}-thinking-content" class="p-3 pt-1 text-slate-600 font-mono text-[11px] whitespace-pre-wrap border-t border-slate-200 leading-relaxed bg-white"></div>
          </details>
        </div>

        <!-- Simulated Tool Call Card -->
        <div id="${messageId}-tool-container" class="hidden">
          <div class="bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs space-y-1.5">
            <div class="flex items-center justify-between text-slate-700 font-mono text-[11px]">
              <span class="flex items-center gap-1.5">
                <i data-lucide="wrench" class="w-3.5 h-3.5 text-[#d4077b]"></i> Outil : <strong id="${messageId}-tool-name"></strong>
              </span>
              <span id="${messageId}-tool-status" class="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-semibold">Exécution...</span>
            </div>
            <pre id="${messageId}-tool-result" class="text-[11px] text-slate-700 bg-white p-2.5 rounded-lg border border-slate-200 font-mono whitespace-pre-wrap overflow-x-auto"></pre>
          </div>
        </div>

        <!-- Main Response Body -->
        <div id="${messageId}-content" class="prose-custom text-sm text-slate-800">
          <span class="typing-cursor"></span>
        </div>

        <!-- Interactive Suggestion Chips -->
        <div id="${messageId}-suggestions" class="suggestions-container hidden"></div>

        <!-- Metrics Footer -->
        <div id="${messageId}-metrics" class="hidden pt-2 border-t border-slate-100 flex items-center gap-3 text-[10px] font-mono text-slate-400"></div>
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

      // Log assistant message (nOObi or Kernel)
      if (accumulatedContent.trim()) {
        const isKernel = accumulatedContent.includes("kernel@node-04:~$") || this.isGlitched;
        this.addLogEntry({
          type: isKernel ? "kernel" : "noobi",
          sender: isKernel ? "Kernel" : "nOObi",
          text: accumulatedContent,
          targetId: messageId
        });
      }

      // Restore submit button if not glitched
      if (!this.isGlitched) {
        this.sendBtn.innerHTML = `<i data-lucide="arrow-up" class="w-4 h-4"></i>`;
        this.sendBtn.classList.replace("bg-slate-800", "bg-[#d4077b]");
        this.sendBtn.classList.remove("border", "border-rose-500/50");
        this.sendBtn.disabled = false;
      }
      if (window.lucide) lucide.createIcons();
      this.scrollToBottom();
    }
  }

  enableGlitchInputLock(isLocked) {
    if (isLocked) {
      this.promptInput.readOnly = false;
      this.promptInput.placeholder = "🔒 CANAL COMPROMIS — Tapez / pour une directive debug...";
      this.sendBtn.disabled = false;
      this.sendBtn.innerHTML = `<i data-lucide="terminal" class="w-4 h-4 text-red-400"></i>`;
      this.chatForm.classList.add("locked-glitch");
      if (window.lucide) lucide.createIcons();
    } else {
      this.promptInput.readOnly = false;
      this.promptInput.placeholder = "Posez une question ou répondez à nOObi...";
      this.sendBtn.disabled = false;
      this.sendBtn.innerHTML = `<i data-lucide="arrow-up" class="w-4 h-4"></i>`;
      this.chatForm.classList.remove("locked-glitch");
      this.hideKernelWarningHud();
      if (window.lucide) lucide.createIcons();
    }
  }

  showKernelWarningHud() {
    if (!this.kernelWarningHud) return;
    this.kernelWarningHud.classList.remove("hidden");
    if (this.hudTimer) clearTimeout(this.hudTimer);
    this.hudTimer = setTimeout(() => {
      this.hideKernelWarningHud();
    }, 3500);
  }

  hideKernelWarningHud() {
    if (!this.kernelWarningHud) return;
    this.kernelWarningHud.classList.add("hidden");
    if (this.hudTimer) {
      clearTimeout(this.hudTimer);
      this.hudTimer = null;
    }
  }

  triggerShakeGlitchEffect() {
    if (!this.chatForm) return;
    this.chatForm.classList.remove("animate-shake-glitch");
    void this.chatForm.offsetWidth;
    this.chatForm.classList.add("animate-shake-glitch");
    setTimeout(() => {
      this.chatForm.classList.remove("animate-shake-glitch");
    }, 400);
  }

  updateScenarioUI(state) {
    if (state.is_glitched) {
      this.isGlitched = true;
      document.body.classList.add("glitch-mode");
      this.enableGlitchInputLock(true);
      if (this.logHeaderTitle) this.logHeaderTitle.textContent = "LOG INTERCEPTÉ [KERNEL]";
    } else {
      this.isGlitched = false;
      document.body.classList.remove("glitch-mode");
      this.enableGlitchInputLock(false);
      if (this.logHeaderTitle) this.logHeaderTitle.textContent = "Log des Échanges";
    }

    if (state.scenario_id && state.scenario_id !== "free_mode") {
      if (this.scenarioProgressContainer) this.scenarioProgressContainer.classList.remove("hidden");
      if (this.scenarioStepTitle) this.scenarioStepTitle.textContent = state.step_title || state.step_id;
      if (this.complianceVal && state.compliance_score !== undefined) {
        this.complianceVal.textContent = state.compliance_score;
        if (this.compliancePill) {
          if (state.compliance_score < 50) {
            this.compliancePill.className = "text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200";
          } else if (state.compliance_score < 75) {
            this.compliancePill.className = "text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200";
          } else {
            this.compliancePill.className = "text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200";
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

    const isGlitch = this.isGlitched || document.body.classList.contains("glitch-mode");

    if (isGlitch) {
      container.className = "kernel-terminal-suggestions";
      suggestions.forEach(sugText => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "kernel-cmd-btn";
        btn.innerHTML = `<span class="kernel-prompt">$</span> <span class="kernel-cmd-text">${this.escapeHtml(sugText)}</span>`;
        btn.addEventListener("click", () => {
          this.hideKernelWarningHud();
          container.querySelectorAll("button").forEach(b => {
            b.disabled = true;
            b.classList.add("opacity-40", "cursor-not-allowed");
          });
          this.handleSubmit(sugText);
        });
        container.appendChild(btn);
      });
    } else {
      container.className = "suggestions-container";
      suggestions.forEach(sugText => {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "suggestion-chip";
        chip.innerHTML = `<i data-lucide="corner-down-right" class="w-3 h-3 text-[#d4077b]"></i><span>${this.escapeHtml(sugText)}</span>`;
        chip.addEventListener("click", () => {
          container.querySelectorAll("button").forEach(b => {
            b.disabled = true;
            b.classList.add("opacity-40", "cursor-not-allowed");
          });
          this.handleSubmit(sugText);
        });
        container.appendChild(chip);
      });
      if (window.lucide) lucide.createIcons();
    }

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

  addLogEntry({ type, sender, text, targetId }) {
    if (!this.logItemsContainer) return;

    if (this.logEmptyState) {
      this.logEmptyState.classList.add("hidden");
    }

    this.logCount = (this.logCount || 0) + 1;
    if (this.logCounter) {
      this.logCounter.textContent = this.logCount;
    }

    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

    // Clean text preview (strip markdown symbols like **, ###, > [!NOTE], etc.)
    let preview = text
      .replace(/^kernel@node-04:\~\$\s*/i, "")
      .replace(/^>\s*\[!.*?\]/gm, "")
      .replace(/^[#*`>_~\-]+/gm, "")
      .replace(/\*\*(.*?)\*\*/g, "$1")
      .replace(/`([^`]+)`/g, "$1")
      .replace(/\n+/g, " ")
      .trim();

    if (preview.length > 95) {
      preview = preview.substring(0, 92) + "...";
    }

    const entryCard = document.createElement("div");
    entryCard.className = `log-entry log-entry-${type}`;
    entryCard.setAttribute("data-target", targetId);
    entryCard.title = "Cliquer pour afficher dans la discussion";

    let iconName = "bot";
    if (type === "user") iconName = "user";
    else if (type === "kernel") iconName = "terminal";

    entryCard.innerHTML = `
      <div class="flex items-center justify-between gap-1 mb-1">
        <span class="log-badge log-badge-${type}">
          <i data-lucide="${iconName}" class="w-3 h-3"></i>
          <span>${this.escapeHtml(sender)}</span>
        </span>
        <span class="log-timestamp">${timeStr}</span>
      </div>
      <p class="log-preview">${this.escapeHtml(preview)}</p>
    `;

    // Click to scroll to message in the main chat
    entryCard.addEventListener("click", () => {
      const targetEl = document.getElementById(targetId);
      if (targetEl) {
        targetEl.scrollIntoView({ behavior: "smooth", block: "center" });
        targetEl.classList.remove("highlight-pulse");
        void targetEl.offsetWidth;
        targetEl.classList.add("highlight-pulse");
        setTimeout(() => targetEl.classList.remove("highlight-pulse"), 1300);
      }
    });

    this.logItemsContainer.appendChild(entryCard);
    if (window.lucide) lucide.createIcons();

    // Auto-scroll log container to bottom
    if (this.exchangeLogContainer) {
      this.exchangeLogContainer.scrollTop = this.exchangeLogContainer.scrollHeight;
    }
  }

  processImageFile(file) {
    if (!file || !file.type.startsWith("image/")) {
      return;
    }

    // Limit to 10MB
    if (file.size > 10 * 1024 * 1024) {
      alert("L'image est trop volumineuse (max 10 Mo).");
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const dataUrl = e.target.result;
      const sizeStr = file.size > 1024 * 1024
        ? `${(file.size / (1024 * 1024)).toFixed(1)} Mo`
        : `${Math.round(file.size / 1024)} Ko`;

      this.currentUploadedImage = {
        dataUrl: dataUrl,
        name: file.name || "photo.jpg",
        sizeStr: sizeStr
      };

      if (this.imagePreviewThumb) this.imagePreviewThumb.src = dataUrl;
      if (this.imagePreviewName) this.imagePreviewName.textContent = file.name || "Photo";
      if (this.imagePreviewSize) this.imagePreviewSize.textContent = sizeStr;
      if (this.imagePreviewBar) this.imagePreviewBar.classList.remove("hidden");
      this.promptInput.focus();
    };
    reader.readAsDataURL(file);
  }

  clearSelectedImage() {
    this.currentUploadedImage = null;
    if (this.imagePreviewBar) this.imagePreviewBar.classList.add("hidden");
    if (this.imagePreviewThumb) this.imagePreviewThumb.src = "";
    if (this.imagePreviewName) this.imagePreviewName.textContent = "";
    if (this.imagePreviewSize) this.imagePreviewSize.textContent = "";
    if (this.imageUploadInput) this.imageUploadInput.value = "";
  }

  async openCamera() {
    if (this.isGlitched) {
      this.triggerShakeGlitchEffect();
      this.showKernelWarningHud();
      return;
    }

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      this.showCameraError("Votre navigateur ou contexte ne permet pas l'accès direct via getUserMedia (nécessite HTTPS ou localhost). Utilisez l'import de fichier.");
      this.cameraModal.classList.remove("hidden");
      if (window.lucide) lucide.createIcons();
      return;
    }

    if (this.cameraErrorContainer) this.cameraErrorContainer.classList.add("hidden");
    this.cameraModal.classList.remove("hidden");
    if (this.cameraResolutionLabel) this.cameraResolutionLabel.textContent = "Recherche flux...";
    if (window.lucide) lucide.createIcons();

    try {
      const constraints = {
        video: {
          facingMode: this.cameraFacingMode,
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      this.cameraStream = stream;
      if (this.webcamVideo) {
        this.webcamVideo.srcObject = stream;
        this.webcamVideo.onloadedmetadata = () => {
          this.webcamVideo.play().catch(() => {});
          if (this.cameraResolutionLabel) {
            this.cameraResolutionLabel.textContent = `${this.webcamVideo.videoWidth || 640} × ${this.webcamVideo.videoHeight || 480}`;
          }
        };
      }
    } catch (err) {
      console.error("Camera access error:", err);
      let message = "Impossible d'accéder au flux de la caméra.";
      if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
        message = "Accès refusé. Veuillez autoriser l'accès à votre webcam ou appareil photo dans les paramètres du navigateur.";
      } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
        message = "Aucun périphérique caméra ou webcam détecté sur cet appareil.";
      } else if (err.name === "NotReadableError" || err.name === "TrackStartError") {
        message = "La caméra est peut-être déjà sollicitée par une autre application.";
      }
      this.showCameraError(message);
    }
  }

  showCameraError(msg) {
    if (this.cameraErrorMsg) this.cameraErrorMsg.textContent = msg;
    if (this.cameraErrorContainer) this.cameraErrorContainer.classList.remove("hidden");
    if (window.lucide) lucide.createIcons();
  }

  closeCamera() {
    if (this.cameraStream) {
      this.cameraStream.getTracks().forEach(track => track.stop());
      this.cameraStream = null;
    }
    if (this.webcamVideo) {
      this.webcamVideo.srcObject = null;
    }
    if (this.cameraModal) {
      this.cameraModal.classList.add("hidden");
    }
    if (this.cameraErrorContainer) {
      this.cameraErrorContainer.classList.add("hidden");
    }
  }

  async switchCameraFacingMode() {
    this.cameraFacingMode = this.cameraFacingMode === "user" ? "environment" : "user";
    if (this.cameraStream) {
      this.cameraStream.getTracks().forEach(track => track.stop());
      this.cameraStream = null;
    }
    await this.openCamera();
  }

  captureCameraPhoto() {
    if (!this.webcamVideo || !this.webcamCanvas) return;
    const video = this.webcamVideo;
    const canvas = this.webcamCanvas;

    const width = video.videoWidth || 640;
    const height = video.videoHeight || 480;

    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext("2d");

    // Capture current frame from live stream
    ctx.drawImage(video, 0, 0, width, height);

    // Export frame as JPEG data URL
    const dataUrl = canvas.toDataURL("image/jpeg", 0.90);
    const estKb = Math.max(1, Math.round((dataUrl.length * 0.75) / 1024));

    this.currentUploadedImage = {
      dataUrl: dataUrl,
      name: `webcam_${Date.now()}.jpg`,
      sizeStr: `${estKb} Ko`
    };

    if (this.imagePreviewThumb) this.imagePreviewThumb.src = dataUrl;
    if (this.imagePreviewName) this.imagePreviewName.textContent = this.currentUploadedImage.name;
    if (this.imagePreviewSize) this.imagePreviewSize.textContent = this.currentUploadedImage.sizeStr;
    if (this.imagePreviewBar) this.imagePreviewBar.classList.remove("hidden");

    this.closeCamera();
    this.promptInput.focus();
  }

  // =========================================================
  // DEBUG SLASH COMMANDS & HYBRID GEOLOCATION (/WHEREAMI)
  // =========================================================

  handleDebugAutocomplete(inputValue) {
    if (!inputValue.startsWith("/")) {
      this.hideDebugAutocomplete();
      return;
    }

    const query = inputValue.toLowerCase().trim();
    this.activeDebugMatches = this.registeredDebugCommands.filter(item =>
      item.cmd.toLowerCase().startsWith(query) || (query === "/" || item.cmd.includes(query.slice(1)))
    );

    if (this.activeDebugMatches.length === 0) {
      this.hideDebugAutocomplete();
      return;
    }

    this.renderDebugAutocompleteList();
    this.showDebugAutocomplete();
  }

  renderDebugAutocompleteList() {
    if (!this.debugCommandsList) return;
    this.debugCommandsList.innerHTML = "";

    this.activeDebugMatches.forEach((item, index) => {
      const el = document.createElement("div");
      el.className = `debug-cmd-item ${index === this.selectedDebugIndex ? "active" : ""}`;
      el.innerHTML = `
        <span class="debug-cmd-badge">${this.escapeHtml(item.cmd)}</span>
        <span class="debug-cmd-desc">${this.escapeHtml(item.desc)}</span>
      `;
      el.addEventListener("click", () => {
        this.selectDebugCommand(item.cmd);
      });
      this.debugCommandsList.appendChild(el);
    });
  }

  selectDebugCommand(cmd) {
    this.promptInput.value = cmd;
    this.hideDebugAutocomplete();
    this.promptInput.focus();
    this.handleSubmit();
  }

  showDebugAutocomplete() {
    if (this.debugAutocompleteMenu) {
      this.debugAutocompleteMenu.classList.remove("hidden");
    }
  }

  hideDebugAutocomplete() {
    if (this.debugAutocompleteMenu) {
      this.debugAutocompleteMenu.classList.add("hidden");
    }
    this.selectedDebugIndex = -1;
    this.activeDebugMatches = [];
  }

  async acquireLocationData() {
    // 1. Try browser HTML5 Geolocation (GPS) with a 3.5s timeout
    const getGpsPosition = () => {
      return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
          return reject(new Error("Géolocalisation HTML5 non supportée"));
        }
        navigator.geolocation.getCurrentPosition(
          pos => resolve(pos),
          err => reject(err),
          { timeout: 3500, enableHighAccuracy: true, maximumAge: 60000 }
        );
      });
    };

    try {
      const position = await getGpsPosition();
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;
      const accuracy = position.coords.accuracy;

      let city = "Secteur résolu";
      let region = "";
      let country = "";

      // Reverse geocode via Nominatim with short 2s timeout
      try {
        const nomController = new AbortController();
        const nomTimeout = setTimeout(() => nomController.abort(), 2000);
        const nomRes = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`, {
          signal: nomController.signal,
          headers: { "Accept-Language": "fr" }
        });
        clearTimeout(nomTimeout);
        if (nomRes.ok) {
          const nomData = await nomRes.json();
          const addr = nomData.address || {};
          city = addr.city || addr.town || addr.village || addr.municipality || city;
          region = addr.state || addr.region || "";
          country = addr.country || "";
        }
      } catch (e) {
        console.warn("Nominatim reverse geocode fallback:", e);
      }

      return {
        lat: lat,
        lon: lon,
        accuracy: accuracy,
        method: "gps",
        city: city,
        region: region,
        country: country
      };
    } catch (gpsError) {
      console.info("GPS geolocation unavailable or denied, falling back to IP:", gpsError);

      // 2. Fallback to IP geolocation (no permission needed)
      try {
        const ipController = new AbortController();
        const ipTimeout = setTimeout(() => ipController.abort(), 2500);
        const ipRes = await fetch("https://ipwho.is/", { signal: ipController.signal });
        clearTimeout(ipTimeout);
        if (ipRes.ok) {
          const ipData = await ipRes.json();
          if (ipData.success !== false) {
            return {
              lat: ipData.latitude,
              lon: ipData.longitude,
              accuracy: 5000,
              method: "ip",
              city: ipData.city || "Ville détectée",
              region: ipData.region || "",
              country: ipData.country || "",
              isp: (ipData.connection && ipData.connection.isp) || ipData.isp || ""
            };
          }
        }
      } catch (ipErr1) {
        console.warn("Primary IP geolocation failed, attempting secondary ipapi.co:", ipErr1);
      }

      try {
        const ip2Res = await fetch("https://ipapi.co/json/");
        if (ip2Res.ok) {
          const ip2Data = await ip2Res.json();
          return {
            lat: ip2Data.latitude,
            lon: ip2Data.longitude,
            accuracy: 8000,
            method: "ip",
            city: ip2Data.city || "Zone IP",
            region: ip2Data.region || "",
            country: ip2Data.country_name || "",
            isp: ip2Data.org || ""
          };
        }
      } catch (ipErr2) {
        console.warn("Secondary IP geolocation failed:", ipErr2);
      }

      return {
        error: "Permission GPS refusée et serveurs de relais IP inaccessibles."
      };
    }
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
