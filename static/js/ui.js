// Configure Marked.js safely
marked.use({
  breaks: true,
  gfm: true
});

// Custom Markdown renderer to wrap code blocks with header and copy button
const renderer = new marked.Renderer();

// Support both older Marked (string arguments) and newer Marked (token object)
renderer.code = function(codeOrToken, maybeLang) {
  let text = '';
  let language = 'plaintext';

  if (typeof codeOrToken === 'object' && codeOrToken !== null) {
    text = codeOrToken.text || codeOrToken.raw || '';
    language = codeOrToken.lang || 'plaintext';
  } else {
    text = String(codeOrToken || '');
    language = maybeLang || 'plaintext';
  }

  let highlighted = text;
  try {
    if (window.hljs && hljs.getLanguage(language)) {
      highlighted = hljs.highlight(text, { language }).value;
    } else if (window.hljs) {
      highlighted = hljs.highlightAuto(text).value;
    }
  } catch (e) {
    highlighted = text;
  }

  const escapedRaw = encodeURIComponent(text);

  return `
    <div class="code-block-wrapper my-3">
      <div class="code-header">
        <span class="font-mono text-xs text-gray-400">${language}</span>
        <button class="copy-btn text-gray-300 hover:text-white" onclick="copyCodeSnippet(this, decodeURIComponent('${escapedRaw}'))">
          <i data-lucide="copy" class="w-3.5 h-3.5"></i>
          <span>Copy</span>
        </button>
      </div>
      <pre><code class="hljs language-${language}">${highlighted}</code></pre>
    </div>
  `;
};

// Custom blockquote renderer supporting both string and token objects
renderer.blockquote = function(quoteOrToken) {
  let text = '';
  if (typeof quoteOrToken === 'object' && quoteOrToken !== null) {
    text = quoteOrToken.text || quoteOrToken.raw || '';
  } else {
    text = String(quoteOrToken || '');
  }

  let calloutClass = "";
  if (text.includes("[!NOTE]")) {
    calloutClass = "callout-note";
    text = text.replace(/\[!NOTE\]/g, "<strong>ℹ️ Note:</strong>");
  } else if (text.includes("[!TIP]")) {
    calloutClass = "callout-tip";
    text = text.replace(/\[!TIP\]/g, "<strong>💡 Tip:</strong>");
  } else if (text.includes("[!WARNING]") || text.includes("[!CAUTION]")) {
    calloutClass = "callout-warning";
    text = text.replace(/\[!(WARNING|CAUTION)\]/g, "<strong>⚠️ Warning:</strong>");
  } else if (text.includes("[!IMPORTANT]")) {
    calloutClass = "callout-warning";
    text = text.replace(/\[!IMPORTANT\]/g, "<strong>❗ Important:</strong>");
  }

  return `<blockquote class="${calloutClass}">${text}</blockquote>`;
};

marked.use({ renderer });

// Global copy helper
window.copyCodeSnippet = function(button, rawCode) {
  navigator.clipboard.writeText(rawCode).then(() => {
    const originalHTML = button.innerHTML;
    button.innerHTML = `<i data-lucide="check" class="w-3.5 h-3.5 text-emerald-400"></i><span class="text-emerald-400 font-semibold">Copied!</span>`;
    if (window.lucide) lucide.createIcons();
    setTimeout(() => {
      button.innerHTML = originalHTML;
      if (window.lucide) lucide.createIcons();
    }, 2000);
  });
};

// UI Element Helpers
document.addEventListener('DOMContentLoaded', () => {
  // Mobile sidebar controls
  const openSidebarBtn = document.getElementById('open-sidebar-btn');
  const closeSidebarBtn = document.getElementById('close-sidebar-btn');
  const sidebar = document.getElementById('sidebar');
  const sidebarOverlay = document.getElementById('sidebar-overlay');

  function openSidebar() {
    sidebar.classList.remove('-translate-x-full');
    sidebarOverlay.classList.remove('hidden');
  }

  function closeSidebar() {
    sidebar.classList.add('-translate-x-full');
    sidebarOverlay.classList.add('hidden');
  }

  if (openSidebarBtn) openSidebarBtn.addEventListener('click', openSidebar);
  if (closeSidebarBtn) closeSidebarBtn.addEventListener('click', closeSidebar);
  if (sidebarOverlay) sidebarOverlay.addEventListener('click', closeSidebar);

  // Model Selector Dropdown
  const modelSelectorBtn = document.getElementById('model-selector-btn');
  const modelDropdownMenu = document.getElementById('model-dropdown-menu');

  if (modelSelectorBtn && modelDropdownMenu) {
    modelSelectorBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      modelDropdownMenu.classList.toggle('hidden');
    });

    document.addEventListener('click', () => {
      if (!modelDropdownMenu.classList.contains('hidden')) {
        modelDropdownMenu.classList.add('hidden');
      }
    });

    modelDropdownMenu.addEventListener('click', (e) => {
      e.stopPropagation();
    });
  }

  // Scenario Selector Dropdown
  const scenarioSelectorBtn = document.getElementById('scenario-selector-btn');
  const scenarioDropdownMenu = document.getElementById('scenario-dropdown-menu');

  if (scenarioSelectorBtn && scenarioDropdownMenu) {
    scenarioSelectorBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      scenarioDropdownMenu.classList.toggle('hidden');
    });

    document.addEventListener('click', () => {
      if (!scenarioDropdownMenu.classList.contains('hidden')) {
        scenarioDropdownMenu.classList.add('hidden');
      }
    });

    scenarioDropdownMenu.addEventListener('click', (e) => {
      e.stopPropagation();
    });
  }

  // Textarea auto-resize
  const promptInput = document.getElementById('prompt-input');
  if (promptInput) {
    promptInput.addEventListener('input', () => {
      promptInput.style.height = 'auto';
      promptInput.style.height = Math.min(promptInput.scrollHeight, 180) + 'px';
    });
  }

  if (window.lucide) lucide.createIcons();
});
