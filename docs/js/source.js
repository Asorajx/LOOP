/* =========================
   Source Highlighting
   ========================= */

function clearLineHighlights(drawer) {
    if (!drawer) return;

    drawer
        .querySelectorAll(".source-line.executing, .source-line.executed")
        .forEach(function(line) {
            line.classList.remove("executing", "executed");
        });
}

function clearAllLineHighlights() {
    document.querySelectorAll(".code-drawer").forEach(clearLineHighlights);
}

function scrollToSourceLine(line) {
    const codeBlock = line.closest(".source-code");
    if (!codeBlock) return;

    const lineRect = line.getBoundingClientRect();
    const codeRect = codeBlock.getBoundingClientRect();
    const lineTop = codeBlock.scrollTop + lineRect.top - codeRect.top;
    const targetTop = lineTop - codeBlock.clientHeight / 2 + lineRect.height / 2;

    codeBlock.scrollTo({
        top: Math.max(0, targetTop),
        behavior: "smooth"
    });
}


/* =========================
   Source Code Drawers
   ========================= */

function createCodeDrawer(button) {
    const drawer = document.createElement("div");
    drawer.className = "code-drawer";
    drawer.id = `code-${button.id}`;
    drawer.setAttribute("aria-hidden", "true");
    drawer.innerHTML = `
        <div class="code-drawer-inner">
            <pre class="source-code"><code>Source code will load when opened.</code></pre>
        </div>
    `;

    button.setAttribute("aria-expanded", "false");
    button.setAttribute("aria-controls", drawer.id);
    button.insertAdjacentElement("afterend", drawer);
}

function renderSourceLines(code, source) {
    code.innerHTML = "";

    source.trimEnd().split("\n").forEach(function(text, index) {
        const line = document.createElement("span");
        line.className = "source-line";
        line.dataset.line = String(index + 1);
        line.textContent = text || " ";
        code.appendChild(line);
    });
}

async function loadMethodSource(button, drawer) {
    if (drawer.dataset.loaded === "true") return;

    const code = drawer.querySelector("code");
    code.textContent = "Loading source...";

    try {
        const response = await fetch(`/api/source/${encodeURIComponent(button.dataset.source)}`);
        const data = await response.json();

        if (data.success) {
            renderSourceLines(code, data.source);
            drawer.dataset.loaded = "true";
        }
        else {
            code.textContent = data.message;
        }
    }
    catch (error) {
        code.textContent = "Unable to load source code.";
        console.error("Unable to load method source:", error);
    }
}

function waitForDrawerTransition(drawer) {
    return new Promise(function(resolve) {
        let finished = false;

        function finish() {
            if (finished) return;
            finished = true;
            drawer.removeEventListener("transitionend", handleTransitionEnd);
            window.clearTimeout(fallbackTimer);
            resolve();
        }

        function handleTransitionEnd(event) {
            if (event.target === drawer && event.propertyName === "grid-template-rows") {
                finish();
            }
        }

        drawer.addEventListener("transitionend", handleTransitionEnd);
        const fallbackTimer = window.setTimeout(finish, 280);
    });
}

function pauseActiveCircuitGlow() {
    document.querySelectorAll(".circuit-active").forEach(path => path.remove());
}

function closeCodeDrawer(button) {
    const drawer = document.getElementById(button.getAttribute("aria-controls"));
    if (!drawer) return Promise.resolve();

    clearLineHighlights(drawer);
    pauseActiveCircuitGlow();

    const transition = waitForDrawerTransition(drawer);
    button.setAttribute("aria-expanded", "false");
    drawer.setAttribute("aria-hidden", "true");
    drawer.classList.remove("open");

    return transition;
}

async function openCodeDrawer(button) {
    const panel = button.closest(".space");
    const drawer = document.getElementById(button.getAttribute("aria-controls"));
    if (!panel || !drawer) return null;

    const closingTransitions = [];

    panel.querySelectorAll('.method[aria-expanded="true"]').forEach(function(openButton) {
        if (openButton !== button) {
            closingTransitions.push(closeCodeDrawer(openButton));
        }
    });

    pauseActiveCircuitGlow();

    const openingTransition = waitForDrawerTransition(drawer);
    button.setAttribute("aria-expanded", "true");
    drawer.setAttribute("aria-hidden", "false");
    drawer.classList.add("open");

    await Promise.all([
        loadMethodSource(button, drawer),
        openingTransition,
        ...closingTransitions
    ]);

    const codeBlock = drawer.querySelector(".source-code");
    if (codeBlock) codeBlock.scrollTop = 0;

    redrawCircuitNetwork();
    return drawer;
}

async function toggleCodeDrawer(button) {
    const drawer = document.getElementById(button.getAttribute("aria-controls"));
    if (!drawer) return false;

    const wasOpen = button.getAttribute("aria-expanded") === "true";

    if (wasOpen) {
        await closeCodeDrawer(button);
        redrawCircuitNetwork();
        return false;
    }

    await openCodeDrawer(button);
    return true;
}

async function getEventDrawer(sourceId, rootButton) {
    const button = document.getElementById(sourceId);
    if (!button) return null;

    const drawer = document.getElementById(button.getAttribute("aria-controls"));
    if (drawer?.classList.contains("open")) return drawer;

    const samePanel = rootButton && button.closest(".space") === rootButton.closest(".space");
    if (samePanel && button !== rootButton) return null;

    return openCodeDrawer(button);
}

async function highlightSourcePattern(sourceId, pattern, rootButton, token) {
    if (!sourceId || !pattern || token !== playbackToken) return;

    const drawer = await getEventDrawer(sourceId, rootButton);
    if (!drawer || token !== playbackToken) return;

    const line = Array.from(drawer.querySelectorAll(".source-line"))
        .find(sourceLine => sourceLine.textContent.includes(pattern));

    if (!line) return;

    document.querySelectorAll(".source-line.executing").forEach(function(activeLine) {
        activeLine.classList.remove("executing");
    });

    line.classList.add("executed", "executing");
    scrollToSourceLine(line);
    await wait(PLAYBACK_DELAY);

    if (token === playbackToken) {
        line.classList.remove("executing");
    }
}