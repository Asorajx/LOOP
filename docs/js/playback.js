/* =========================
   Simulation State
   ========================= */

async function getSimulationState() {
    try {
        const response = await fetch("/api/state");
        const data = await response.json();
        simulationState = {
            devices: data.devices || [],
            connections: data.connections || []
        };
    }
    catch (error) {
        console.error("Unable to load simulation state:", error);
    }
}

/* =========================
   Playback State
   ========================= */

let executionEvents = [];
let currentEventIndex = 0;
let currentExecutionData = null;
let currentRootButton = null;
let playbackMethodStack = [];
let playbackCallCounts = {};
let isPlaying = false;
let isProcessingEvent = false;
let isResetting = false;
let isGuidedPreparing = false;
let currentMode = simulationModes.MANUAL;
let guidedSceneIndex = 0;

function hasPlaybackEvents() {
    return executionEvents.length > 0;
}

function playbackComplete() {
    return hasPlaybackEvents() && currentEventIndex >= executionEvents.length;
}

function updatePlaybackControls() {
    const previousButton = document.getElementById("playback-previous");
    const nextButton = document.getElementById("playback-next");
    const playButton = document.getElementById("playback-play");
    const pauseButton = document.getElementById("playback-pause");
    const replayButton = document.getElementById("playback-replay");
    const resetButton = document.getElementById("playback-reset");
    const progress = document.getElementById("playback-progress");
    const busy = isProcessingEvent || isResetting || isGuidedPreparing;
    const complete = playbackComplete();
    const guidedComplete = isGuidedSequenceComplete();

    if (previousButton) {
        previousButton.disabled = !hasPlaybackEvents() || currentEventIndex <= 0 || isPlaying || busy;
    }
    if (nextButton) {
        nextButton.disabled = !hasPlaybackEvents() || complete || isPlaying || busy;
    }
    if (playButton) {
        if (currentMode === simulationModes.GUIDED) {
            playButton.disabled = guidedComplete || isPlaying || busy;
        }
        else {
            playButton.disabled = !hasPlaybackEvents() || complete || isPlaying || busy;
        }
    }
    if (pauseButton) {
        pauseButton.disabled = !isPlaying;
    }
    if (replayButton) {
        replayButton.disabled = !hasPlaybackEvents() || isPlaying || busy;
    }
    if (resetButton) {
        resetButton.disabled = isResetting;
    }

    if (progress) {
        const displayedIndex = isProcessingEvent
            ? currentEventIndex + 1
            : currentEventIndex;

        progress.textContent = `${Math.min(displayedIndex, executionEvents.length)} / ${executionEvents.length}`;
    }

    updateModeControls();
}

function resetPlaybackPosition() {
    currentEventIndex = 0;
    playbackMethodStack = [];
    playbackCallCounts = {};
}

function clearPlaybackSession() {
    executionEvents = [];
    currentExecutionData = null;
    currentRootButton = null;
    isPlaying = false;
    isProcessingEvent = false;
    resetPlaybackPosition();
    clearInheritanceCallVisual();
    updatePlaybackControls();
}

function resetPlaybackVisuals() {
    clearAllLineHighlights();
    clearActiveVisuals();
    clearInheritanceCallVisual();
    clearStateChanges();
    currentRootButton?.classList.add("active-source");
}

/* =========================
   Guided Mode
   ========================= */

function getCurrentGuidedScene() {
    return guidedScenes[guidedSceneIndex] || null;
}

function isGuidedSequenceComplete() {
    return (
        currentMode === simulationModes.GUIDED
        && guidedSceneIndex === guidedScenes.length - 1
        && hasPlaybackEvents()
        && playbackComplete()
    );
}

function updateModeControls() {
    const manualButton = document.getElementById("mode-manual");
    const guidedButton = document.getElementById("mode-guided");
    const busy = isPlaying || isProcessingEvent || isResetting || isGuidedPreparing;

    if (manualButton) {
        const active = currentMode === simulationModes.MANUAL;
        manualButton.classList.toggle("active", active);
        manualButton.setAttribute("aria-pressed", String(active));
        manualButton.disabled = busy;
    }

    if (guidedButton) {
        const active = currentMode === simulationModes.GUIDED;
        guidedButton.classList.toggle("active", active);
        guidedButton.setAttribute("aria-pressed", String(active));
        guidedButton.disabled = busy;
    }
}

function updateGuidedSceneDisplay(message = null) {
    const bar = document.getElementById("guided-scene-bar");
    const number = document.getElementById("guided-scene-number");
    const title = document.getElementById("guided-scene-title");
    const focus = document.getElementById("guided-scene-focus");
    const status = document.getElementById("guided-scene-status");

    if (!bar) return;

    if (currentMode !== simulationModes.GUIDED) {
        bar.hidden = true;
        return;
    }

    const scene = getCurrentGuidedScene();
    bar.hidden = false;

    if (number) number.textContent = `Scene ${guidedSceneIndex + 1} / ${guidedScenes.length}`;
    if (title) title.textContent = scene?.title || "Guided Mode";
    if (focus) focus.textContent = scene ? `Focus: ${scene.focus}` : "";
    if (status && message !== null) status.textContent = message;
}

function showGuidedReady(totalEvents = 0) {
    const scene = getCurrentGuidedScene();
    const count = document.getElementById("terminal-event-count");
    const log = document.getElementById("terminal-log");

    updateGuidedSceneDisplay("Press Play to begin.");
    if (count) count.textContent = `Event 0 / ${totalEvents}`;
    if (!log || !scene) return;

    log.innerHTML = "";
    const empty = document.createElement("div");
    empty.className = "terminal-empty";
    empty.appendChild(createTerminalText("terminal-empty-title", `${scene.title} · Ready`));
    empty.appendChild(createTerminalText("terminal-empty-copy", scene.intro));
    empty.appendChild(createTerminalText("terminal-empty-copy", "Press Play to run the real Python scene, then use Previous or Next to review its events."));
    log.appendChild(empty);
    log.scrollTop = 0;
}

async function resetBackendState() {
    const response = await fetch("/api/reset", {
        method: "POST"
    });
    const data = await response.json();

    if (!data.success) {
        throw new Error(data.message || "Unable to reset simulation.");
    }

    simulationState = {
        devices: data.devices || [],
        connections: data.connections || []
    };
}

function closeAllCodeDrawers() {
    document
        .querySelectorAll('.method[aria-expanded="true"]')
        .forEach(function(button) {
            closeCodeDrawer(button);
        });
}

async function startGuidedScene() {
    const scene = getCurrentGuidedScene();
    if (!scene || isResetting || isGuidedPreparing) return;

    const button = document.getElementById(scene.action);
    if (!button) {
        setSystemStatus("Guided Error");
        console.error(`Guided source not found: ${scene.action}`);
        return;
    }

    isGuidedPreparing = true;
    updatePlaybackControls();

    try {
        setSystemStatus(`Scene ${guidedSceneIndex + 1}`);
        updateGuidedSceneDisplay("Preparing scene...");
        await resetBackendState();

        stopEventPlayback();
        closeAllCodeDrawers();
        clearPlaybackSession();
        clearAllLineHighlights();
        clearActiveVisuals();
        clearStateChanges();
        await openCodeDrawer(button);

        updateGuidedSceneDisplay("Running scene...");
        isGuidedPreparing = false;
        updatePlaybackControls();
        await executeMethod(button, scene.request || {}, true);
    }
    catch (error) {
        setSystemStatus("Guided Error");
        updateGuidedSceneDisplay("Unable to start this scene.");
        console.error("Unable to start guided scene:", error);
    }
    finally {
        isGuidedPreparing = false;
        updatePlaybackControls();
    }
}

async function setSimulationMode(mode) {
    if (!Object.values(simulationModes).includes(mode)) return;
    if (mode === currentMode || isPlaying || isProcessingEvent || isResetting) return;

    currentMode = mode;
    guidedSceneIndex = 0;
    updateModeControls();
    updateGuidedSceneDisplay();
    await resetSimulation();
}

/* =========================
   Playback Helpers
   ========================= */

function stopEventPlayback() {
    playbackToken += 1;
    isPlaying = false;

    document.querySelectorAll(".source-line.executing").forEach(function(line) {
        line.classList.remove("executing");
    });

    updatePlaybackControls();
}

function getEventPatterns(event) {
    if (event.event_type === "METHOD_STARTED") {
        return ["method_started("];
    }

    if (event.event_type === "METHOD_COMPLETED") {
        return ["method_completed("];
    }

    if (event.event_type === "STATE_CHANGED") {
        const statePattern = stateLinePatterns[event.source_id]?.[event.attribute];
        return [statePattern, "state_changed("].filter(Boolean);
    }

    return [];
}

function getParentCallPattern(parentSourceId, childSourceId) {
    const patterns = parentCallPatterns[parentSourceId]?.[childSourceId];
    if (!patterns?.length) return null;

    const key = `${parentSourceId}->${childSourceId}`;
    const count = playbackCallCounts[key] || 0;
    playbackCallCounts[key] = count + 1;
    return patterns[Math.min(count, patterns.length - 1)];
}

async function markSourcePatternExecuted(sourceId, pattern) {
    if (!sourceId || !pattern || !currentRootButton) return null;

    const drawer = await getEventDrawer(sourceId, currentRootButton);
    if (!drawer) return null;

    const line = Array.from(drawer.querySelectorAll(".source-line"))
        .find(sourceLine => sourceLine.textContent.includes(pattern));

    if (line) {
        line.classList.add("executed");
    }

    return line || null;
}

function removeMethodFromStack(sourceId) {
    for (let index = playbackMethodStack.length - 1; index >= 0; index -= 1) {
        if (playbackMethodStack[index] === sourceId) {
            playbackMethodStack.splice(index, 1);
            break;
        }
    }
}

/* =========================
   Inheritance Visualization
   ========================= */

let activeInheritanceCallKey = null;

function getInheritanceCall(childSourceId, parentSourceId) {
    const call = inheritanceCalls[childSourceId];
    if (!call || call.parentSourceId !== parentSourceId) return null;
    return call;
}

function clearInheritanceCallVisual() {
    document.querySelectorAll(".inheritance-child-call").forEach(function(element) {
        element.classList.remove("inheritance-child-call");
    });

    document.querySelectorAll(".inheritance-parent-call").forEach(function(element) {
        element.classList.remove("inheritance-parent-call");
    });

    document.querySelectorAll(".inheritance-call-active").forEach(function(label) {
        if (label.dataset.inheritanceOriginalText) {
            label.textContent = label.dataset.inheritanceOriginalText;
        }
        label.classList.remove("inheritance-call-active");
    });

    activeInheritanceCallKey = null;
}

function showInheritanceCallVisual(childSourceId, parentSourceId) {
    const call = getInheritanceCall(childSourceId, parentSourceId);
    if (!call) {
        clearInheritanceCallVisual();
        return;
    }

    const key = `${childSourceId}->${parentSourceId}`;
    if (activeInheritanceCallKey === key) return;

    clearInheritanceCallVisual();

    const childButton = document.getElementById(childSourceId);
    const parentButton = document.getElementById(parentSourceId);
    const inheritanceLabel = childButton?.closest(".class-card")?.querySelector(".inheritance");

    childButton?.classList.add("inheritance-child-call");
    parentButton?.classList.add("inheritance-parent-call");

    if (inheritanceLabel) {
        if (!inheritanceLabel.dataset.inheritanceOriginalText) {
            inheritanceLabel.dataset.inheritanceOriginalText = inheritanceLabel.textContent.trim();
        }

        inheritanceLabel.textContent = `super(): ${call.childLabel} → ${call.parentLabel}`;
        inheritanceLabel.classList.add("inheritance-call-active");
    }

    activeInheritanceCallKey = key;
}

function syncInheritanceCallVisual() {
    for (let index = 0; index < playbackMethodStack.length - 1; index += 1) {
        const childSourceId = playbackMethodStack[index];
        const parentSourceId = playbackMethodStack[index + 1];

        if (getInheritanceCall(childSourceId, parentSourceId)) {
            showInheritanceCallVisual(childSourceId, parentSourceId);
            return;
        }
    }

    clearInheritanceCallVisual();
}

/* =========================
   Terminal
   ========================= */

let terminalFollowLatest = true;
let terminalScrollTrackingReady = false;

function formatStateValue(value) {
    if (typeof value === "boolean") return value ? "True" : "False";
    if (value === null || value === undefined) return "None";
    return String(value);
}

function setupTerminalScrollTracking() {
    if (terminalScrollTrackingReady) return;

    const log = document.getElementById("terminal-log");
    if (!log) return;

    terminalScrollTrackingReady = true;
    log.addEventListener("scroll", function() {
        const distanceFromBottom = log.scrollHeight - log.scrollTop - log.clientHeight;
        terminalFollowLatest = distanceFromBottom < 24;
    });
}

function pulseTerminal() {
    const terminal = document.getElementById("terminal");
    if (!terminal) return;

    terminal.classList.remove("updated");
    window.requestAnimationFrame(function() {
        terminal.classList.add("updated");
        window.setTimeout(function() {
            terminal.classList.remove("updated");
        }, 420);
    });
}

function createTerminalText(className, text) {
    const element = document.createElement("span");
    element.className = className;
    element.textContent = text;
    return element;
}

function createExplanationRow(label, text) {
    const fragment = document.createDocumentFragment();
    fragment.appendChild(createTerminalText("terminal-explanation-label", label));
    fragment.appendChild(createTerminalText("terminal-explanation-text", text));
    return fragment;
}

function getTerminalExplanation(sourceId) {
    return terminalExplanations[sourceId] || {
        code: "Runs the current Python method and records its execution through ExecutionTracer.",
        description: "Performs part of the fictional cybersecurity simulation.",
        oopConcepts: "Object Interaction"
    };
}

function createTerminalEntry(event, eventIndex, parentEvent) {
    const entry = document.createElement("article");
    entry.className = "terminal-entry";
    entry.dataset.eventIndex = String(eventIndex);

    const number = createTerminalText("terminal-entry-number", String(eventIndex + 1).padStart(2, "0"));
    const head = document.createElement("div");
    head.className = "terminal-entry-head";

    const typeLabels = {
        METHOD_STARTED: "Method",
        METHOD_COMPLETED: "Done",
        STATE_CHANGED: "State"
    };
    head.appendChild(createTerminalText("terminal-entry-type", typeLabels[event.event_type] || "Event"));

    if (event.event_type === "STATE_CHANGED") {
        head.appendChild(createTerminalText("terminal-entry-title", `${event.object_id} · ${event.attribute}`));

        const state = document.createElement("div");
        state.className = "terminal-state-change";
        state.appendChild(createTerminalText("terminal-state-value", formatStateValue(event.previous_value)));
        state.appendChild(createTerminalText("terminal-state-arrow", "→"));
        state.appendChild(createTerminalText("terminal-state-value", formatStateValue(event.new_value)));

        entry.append(number, head, state);
        return entry;
    }

    const methodLabel = `${event.class_name}.${event.method_name}()`;
    const inheritedCall = event.event_type === "METHOD_STARTED"
        ? getInheritanceCall(parentEvent?.source_id, event.source_id)
        : null;

    head.appendChild(createTerminalText("terminal-entry-title", methodLabel));
    entry.append(number, head);

    const metaParts = [];
    if (event.object_id) metaParts.push(event.object_id);
    if (event.target_id) metaParts.push(`→ ${event.target_id}`);
    if (parentEvent && event.event_type === "METHOD_STARTED") {
        metaParts.push(`Called from ${parentEvent.class_name}.${parentEvent.method_name}()`);
    }
    if (metaParts.length) {
        entry.appendChild(createTerminalText("terminal-entry-meta", metaParts.join(" · ")));
    }

    if (event.message) {
        entry.appendChild(createTerminalText("terminal-message", event.message));
    }

    if (inheritedCall) {
        entry.classList.add("inherited-call");

        const inherited = document.createElement("div");
        inherited.className = "terminal-inherited-call";
        inherited.appendChild(createTerminalText("terminal-inherited-label", "Inherited Call"));
        inherited.appendChild(createTerminalText(
            "terminal-inherited-route",
            `${inheritedCall.childLabel} → ${inheritedCall.parentLabel}`
        ));
        inherited.appendChild(createTerminalText(
            "terminal-inherited-copy",
            `super() reuses the parent implementation on the same ${inheritedCall.objectLabel} object.`
        ));
        entry.appendChild(inherited);
    }

    if (event.event_type === "METHOD_STARTED") {
        const explanation = inheritedCall || getTerminalExplanation(event.source_id);
        const details = document.createElement("div");
        details.className = "terminal-explanation";
        details.appendChild(createExplanationRow("Code", explanation.code));
        details.appendChild(createExplanationRow("Description", explanation.description));
        details.appendChild(createExplanationRow("OOP Concepts", explanation.oopConcepts));
        entry.appendChild(details);
    }

    return entry;
}

function getTerminalParentEvents(position) {
    const parents = new Map();
    const stack = [];

    for (let index = 0; index < position; index += 1) {
        const event = executionEvents[index];

        if (event.event_type === "METHOD_STARTED") {
            parents.set(index, stack[stack.length - 1] || null);
            stack.push(event);
        }
        else if (event.event_type === "METHOD_COMPLETED") {
            for (let stackIndex = stack.length - 1; stackIndex >= 0; stackIndex -= 1) {
                const active = stack[stackIndex];
                if (active.source_id === event.source_id) {
                    stack.splice(stackIndex, 1);
                    break;
                }
            }
        }
    }

    return parents;
}

function scrollTerminalToCurrent(forceScroll = false) {
    const log = document.getElementById("terminal-log");
    const current = log?.querySelector(".terminal-entry.current");
    if (!log || !current || (!terminalFollowLatest && !forceScroll)) return;

    const targetTop = Math.max(0, current.offsetTop - log.clientHeight + current.offsetHeight + 12);
    log.scrollTo({
        top: targetTop,
        behavior: "smooth"
    });
}

function resetTerminal() {
    setupTerminalScrollTracking();
    terminalFollowLatest = true;

    const count = document.getElementById("terminal-event-count");
    const log = document.getElementById("terminal-log");
    if (count) count.textContent = "Event 0 / 0";
    if (!log) return;

    log.innerHTML = "";
    const empty = document.createElement("div");
    empty.className = "terminal-empty";
    empty.appendChild(createTerminalText("terminal-empty-title", "Waiting for execution..."));
    empty.appendChild(createTerminalText("terminal-empty-copy", "Select a method to begin. The execution history will appear here."));
    log.appendChild(empty);
    log.scrollTop = 0;
}

function clearStateChanges() {
    resetTerminal();
}

function showTerminalLoading(button) {
    setupTerminalScrollTracking();
    terminalFollowLatest = true;

    const count = document.getElementById("terminal-event-count");
    const log = document.getElementById("terminal-log");
    const explanation = getTerminalExplanation(button.id);
    const className = button.closest(".class-card")?.querySelector(".class-header span:first-child")?.textContent;
    if (count) count.textContent = "Preparing trace...";
    if (!log) return;

    log.innerHTML = "";
    const entry = document.createElement("article");
    entry.className = "terminal-entry current";
    entry.appendChild(createTerminalText("terminal-entry-number", "··"));

    const head = document.createElement("div");
    head.className = "terminal-entry-head";
    head.appendChild(createTerminalText("terminal-entry-type", "Running"));
    head.appendChild(createTerminalText("terminal-entry-title", className ? `${className}.${button.textContent.trim()}` : button.textContent.trim()));
    entry.appendChild(head);
    entry.appendChild(createTerminalText("terminal-entry-meta", "Executing the real Python method through FastAPI."));

    const details = document.createElement("div");
    details.className = "terminal-explanation";
    details.appendChild(createExplanationRow("Code", explanation.code));
    details.appendChild(createExplanationRow("Description", explanation.description));
    details.appendChild(createExplanationRow("OOP Concepts", explanation.oopConcepts));
    entry.appendChild(details);
    log.appendChild(entry);
    pulseTerminal();
}

function renderTerminalAtPosition(position, forceScroll = false) {
    setupTerminalScrollTracking();

    const count = document.getElementById("terminal-event-count");
    const log = document.getElementById("terminal-log");
    if (!log) return;

    const safePosition = Math.max(0, Math.min(position, executionEvents.length));
    if (count) count.textContent = `Event ${safePosition} / ${executionEvents.length}`;

    if (safePosition === 0) {
        if (currentMode === simulationModes.GUIDED) {
            showGuidedReady(executionEvents.length);
        }
        else {
            resetTerminal();
            if (count) count.textContent = `Event 0 / ${executionEvents.length}`;
        }
        return;
    }

    const previousScrollTop = log.scrollTop;
    const parents = getTerminalParentEvents(safePosition);
    const fragment = document.createDocumentFragment();

    for (let index = 0; index < safePosition; index += 1) {
        const entry = createTerminalEntry(executionEvents[index], index, parents.get(index));
        if (index === safePosition - 1) entry.classList.add("current");
        fragment.appendChild(entry);
    }

    log.replaceChildren(fragment);

    if (terminalFollowLatest || forceScroll) {
        scrollTerminalToCurrent(forceScroll);
    }
    else {
        log.scrollTop = previousScrollTop;
    }
}

function renderTerminalEvent(event, eventIndex) {
    if (!event) {
        resetTerminal();
        return;
    }

    renderTerminalAtPosition(eventIndex + 1);
    pulseTerminal();
}

function setSystemStatus(text) {
    const status = document.getElementById("system-status");
    if (status) status.textContent = text;
}

/* =========================
   Event Playback
   ========================= */

async function playExecutionEvent(event, token) {
    if (!currentRootButton || token !== playbackToken) return false;

    const rootSourceId = currentRootButton.id;
    const circuitType = findCircuitType(rootSourceId);

    renderTerminalEvent(event, currentEventIndex);
    highlightEventInstances(event);

    if (event.event_type === "METHOD_STARTED") {
        const parentSourceId = playbackMethodStack[playbackMethodStack.length - 1];
        const callPattern = getParentCallPattern(parentSourceId, event.source_id);

        if (callPattern) {
            await highlightSourcePattern(parentSourceId, callPattern, currentRootButton, token);
            if (token !== playbackToken) return false;
        }

        if (circuitType && event.source_id) {
            activateTarget(circuitType, rootSourceId, event.source_id);
        }

        if (rootSourceId === "defender-inspect" && event.source_id === "defender-inspect") {
            activateTarget("defender", rootSourceId, "network-device");
        }

        playbackMethodStack.push(event.source_id);
        syncInheritanceCallVisual();
    }

    for (const pattern of getEventPatterns(event)) {
        await highlightSourcePattern(event.source_id, pattern, currentRootButton, token);
        if (token !== playbackToken) return false;
    }

    if (event.event_type === "METHOD_COMPLETED") {
        removeMethodFromStack(event.source_id);
        syncInheritanceCallVisual();
    }

    await wait(PLAYBACK_DELAY);
    return token === playbackToken;
}

async function rebuildPlaybackTo(targetIndex) {
    const safeTarget = Math.max(0, Math.min(targetIndex, executionEvents.length));
    const rootSourceId = currentRootButton?.id;
    const circuitType = rootSourceId ? findCircuitType(rootSourceId) : null;
    let lastExecutedLine = null;

    resetPlaybackPosition();
    resetPlaybackVisuals();

    for (let index = 0; index < safeTarget; index += 1) {
        const event = executionEvents[index];
        highlightEventInstances(event);

        if (event.event_type === "METHOD_STARTED") {
            const parentSourceId = playbackMethodStack[playbackMethodStack.length - 1];
            const callPattern = getParentCallPattern(parentSourceId, event.source_id);

            if (callPattern) {
                const line = await markSourcePatternExecuted(parentSourceId, callPattern);
                if (line) lastExecutedLine = line;
            }

            if (circuitType && event.source_id) {
                activateTarget(circuitType, rootSourceId, event.source_id);
            }

            if (rootSourceId === "defender-inspect" && event.source_id === "defender-inspect") {
                activateTarget("defender", rootSourceId, "network-device");
            }

            playbackMethodStack.push(event.source_id);
            syncInheritanceCallVisual();
        }

        for (const pattern of getEventPatterns(event)) {
            const line = await markSourcePatternExecuted(event.source_id, pattern);
            if (line) lastExecutedLine = line;
        }

        if (event.event_type === "METHOD_COMPLETED") {
            removeMethodFromStack(event.source_id);
            syncInheritanceCallVisual();
        }

        currentEventIndex = index + 1;
    }

    renderTerminalAtPosition(safeTarget, true);

    if (lastExecutedLine) {
        scrollToSourceLine(lastExecutedLine);
    }
}

function finishPlayback() {
    isPlaying = false;

    if (currentExecutionData) {
        simulationState = {
            devices: currentExecutionData.devices || [],
            connections: currentExecutionData.connections || []
        };
    }

    const result = currentExecutionData?.result;

    if (currentMode === simulationModes.GUIDED) {
        if (isGuidedSequenceComplete()) {
            setSystemStatus("Guided Complete");
            updateGuidedSceneDisplay("Guided sequence complete.");
        }
        else {
            setSystemStatus("Scene Complete");
            updateGuidedSceneDisplay("Scene complete · Press Play for the next scene.");
        }
    }
    else {
        setSystemStatus(result === false ? "Attack Blocked" : "System Ready");
    }

    updatePlaybackControls();
}

async function playNextEvent() {
    if (!hasPlaybackEvents() || playbackComplete() || isProcessingEvent) return false;

    const event = executionEvents[currentEventIndex];
    const token = playbackToken;

    isProcessingEvent = true;
    updatePlaybackControls();

    const completed = await playExecutionEvent(event, token);

    if (completed) {
        currentEventIndex += 1;
    }

    isProcessingEvent = false;
    updatePlaybackControls();

    if (completed && playbackComplete()) {
        finishPlayback();
    }

    return completed;
}

async function previousPlayback() {
    if (!hasPlaybackEvents() || currentEventIndex <= 0 || isPlaying || isProcessingEvent) return;

    const targetIndex = currentEventIndex - 1;

    terminalFollowLatest = true;
    stopEventPlayback();
    isProcessingEvent = true;
    setSystemStatus("Rewinding");
    updatePlaybackControls();

    await rebuildPlaybackTo(targetIndex);

    isProcessingEvent = false;
    setSystemStatus("Paused");
    updatePlaybackControls();
}

async function nextPlayback() {
    if (!hasPlaybackEvents() || playbackComplete() || isPlaying || isProcessingEvent) return;

    terminalFollowLatest = true;
    setSystemStatus("Running");
    const completed = await playNextEvent();

    if (completed && !playbackComplete()) {
        setSystemStatus("Paused");
    }
}

async function playPlayback() {
    if (isPlaying || isProcessingEvent || isResetting) return;

    if (currentMode === simulationModes.GUIDED) {
        if (isGuidedSequenceComplete()) return;

        if (!hasPlaybackEvents()) {
            await startGuidedScene();
            return;
        }

        if (playbackComplete()) {
            guidedSceneIndex += 1;
            updateGuidedSceneDisplay("Press Play to begin.");
            await startGuidedScene();
            return;
        }
    }

    if (!hasPlaybackEvents() || playbackComplete()) return;

    terminalFollowLatest = true;
    isPlaying = true;
    setSystemStatus(currentEventIndex === 0 ? "Executing" : "Playing");
    updatePlaybackControls();

    const token = playbackToken;

    while (isPlaying && token === playbackToken && !playbackComplete()) {
        const completed = await playNextEvent();
        if (!completed) break;
    }

    if (token !== playbackToken) return;

    if (playbackComplete()) {
        finishPlayback();
        return;
    }

    isPlaying = false;
    setSystemStatus("Paused");
    updatePlaybackControls();
}

function pausePlayback() {
    if (!isPlaying) return;

    isPlaying = false;
    setSystemStatus(isProcessingEvent ? "Pausing" : "Paused");
    updatePlaybackControls();
}

async function replayPlayback() {
    if (!hasPlaybackEvents() || isPlaying || isProcessingEvent) return;

    terminalFollowLatest = true;
    stopEventPlayback();
    resetPlaybackPosition();
    resetPlaybackVisuals();
    updatePlaybackControls();
    setSystemStatus("Replaying");
    await playPlayback();
}

function preparePlayback(rootButton, data) {
    terminalFollowLatest = true;
    stopEventPlayback();

    executionEvents = data.events || [];
    currentExecutionData = data;
    currentRootButton = rootButton;
    resetPlaybackPosition();
    resetPlaybackVisuals();
    updatePlaybackControls();
}

/* =========================
   Simulation Reset
   ========================= */

async function resetSimulation() {
    if (isResetting) return;

    terminalFollowLatest = true;
    stopEventPlayback();
    isResetting = true;
    setSystemStatus("Resetting");
    updatePlaybackControls();

    try {
        await resetBackendState();

        closeAllCodeDrawers();
        clearAllLineHighlights();
        clearActiveVisuals();
        clearStateChanges();
        clearPlaybackSession();
        window.setTimeout(redrawCircuitNetwork, 240);

        if (currentMode === simulationModes.GUIDED) {
            guidedSceneIndex = 0;
            showGuidedReady();
            setSystemStatus("Guided Ready");
        }
        else {
            updateGuidedSceneDisplay();
            setSystemStatus("System Ready");
        }
    }
    catch (error) {
        setSystemStatus("Connection Error");
        console.error("Unable to reset simulation:", error);
    }
    finally {
        isResetting = false;
        updatePlaybackControls();
        updateGuidedSceneDisplay();
    }
}

/* =========================
   Python Execution
   ========================= */

async function executeMethod(button, requestData = {}, fromGuided = false) {
    if (currentMode === simulationModes.GUIDED && !fromGuided) return;

    stopEventPlayback();
    clearPlaybackSession();
    clearAllLineHighlights();
    clearActiveVisuals();
    clearStateChanges();

    try {
        setSystemStatus("Running Python");
        showTerminalLoading(button);

        const response = await fetch(`/api/execute/${encodeURIComponent(button.id)}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(requestData)
        });
        const data = await response.json();

        if (!data.success) {
            setSystemStatus("Execution Error");
            console.error(data.message || "Unable to execute method.");
            return;
        }

        preparePlayback(button, data);

        if (!hasPlaybackEvents()) {
            finishPlayback();
            return;
        }

        await playPlayback();
    }
    catch (error) {
        setSystemStatus("Connection Error");
        console.error("Unable to execute Python method:", error);
    }
}

