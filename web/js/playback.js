/* =========================
   Playback State
   ========================= */

/* Milliseconds between steps. The travelling light lasts slightly less than one step. */
const PLAYBACK_DELAY = 1400;
document.documentElement.style.setProperty("--circuit-travel", `${(PLAYBACK_DELAY - 100) / 1000}s`);

const playback = {
    run: null,
    target: null,
    position: -1,
    timer: null
};

/* Record the call stack and each frame's current line at every step. */
function analyseRun(run) {
    const frames = [];

    run.steps.forEach(function(step) {
        if (step.kind === "call") {
            frames.length = step.stack.length - 1;
            frames.push({ method: step.method, entry: step.route, key: `${step.file}:${step.line}` });
        }
        else {
            frames.length = step.stack.length;
            frames[frames.length - 1].key = `${step.file}:${step.line}`;
        }
        step.frames = frames.map(frame => ({ ...frame }));
    });
}

function loadRun(run, target) {
    stopPlayback();
    analyseRun(run);
    playback.run = run;
    playback.target = target;
    showPosition(-1);
}

function clearRun() {
    stopPlayback();
    playback.run = null;
    playback.position = -1;
    renderTerminal(null);
    highlightCallStack();
    highlightObjects();
    highlightCode();
    drawRoutes(null);
    updatePlaybackControls();
}

/* Rebuild object state at a step from the starting state plus every change up to it. */
function stateAt(run, position) {
    const state = JSON.parse(JSON.stringify(run.before));
    for (let index = 0; index <= position; index += 1) {
        run.steps[index].changes.forEach(change => { state[change.object][change.attribute] = change.new; });
    }
    return state;
}


/* =========================
   Showing a Step
   ========================= */

/* Draw one step: status icons, Terminal, code highlighting and circuit. */
function showPosition(position) {
    const run = playback.run;
    if (!run) return;

    playback.position = Math.max(-1, Math.min(position, run.steps.length - 1));
    const step = run.steps[playback.position];

    updateObjectStates(stateAt(run, playback.position), loop.data, step?.changes);
    renderTerminal(run, playback.position, selectPosition);

    if (!step) {
        highlightCallStack();
        highlightObjects(null, playback.target);
        highlightCode();
        drawRoutes(null);
        updatePlaybackControls();
        return;
    }

    const frames = step.frames;
    const top = frames[frames.length - 1];
    const below = frames.slice(0, -1);

    /* Focus on the entire active stack while steps remain, not just the yellow line. */
    highlightCallStack(playback.position < run.steps.length - 1 ? frames.map(frame => frame.method) : []);
    highlightObjects(step.object, playback.target);

    /* Light the route that led into the running method; the very first call has none. */
    drawRoutes(top.entry.kind === "start" ? null : top.entry);

    const executed = new Set();
    for (let index = 0; index < playback.position; index += 1) {
        executed.add(`${run.steps[index].file}:${run.steps[index].line}`);
    }
    highlightCode({
        current: `${step.file}:${step.line}`,
        waiting: below.map(frame => frame.key),
        executed: Array.from(executed)
    });

    updatePlaybackControls();
}

/* Clicking a Terminal card jumps to that step. */
function selectPosition(position) {
    stopPlayback();
    showPosition(position);
}


/* =========================
   Playback Controls
   ========================= */

function atEnd() {
    return !playback.run || playback.position >= playback.run.steps.length - 1;
}

/* The first step comes a little sooner, so playback feels responsive after a click. */
function playPlayback() {
    if (!playback.run || atEnd()) return;
    stopPlayback();

    const tick = function() {
        showPosition(playback.position + 1);
        playback.timer = atEnd() ? null : window.setTimeout(tick, PLAYBACK_DELAY);
        updatePlaybackControls();
    };
    playback.timer = window.setTimeout(tick, playback.position === -1 ? 600 : PLAYBACK_DELAY);
    updatePlaybackControls();
}

function stopPlayback() {
    window.clearTimeout(playback.timer);
    playback.timer = null;
    updatePlaybackControls();
}

function previousStep() {
    stopPlayback();
    showPosition(playback.position - 1);
}

function nextStep() {
    stopPlayback();
    showPosition(playback.position + 1);
}

/* Replay shows the recorded steps again. It never runs the Python a second time. */
function replayPlayback() {
    if (!playback.run) return;
    stopPlayback();
    showPosition(-1);
    playPlayback();
}

function updatePlaybackControls() {
    const hasRun = Boolean(playback.run);
    const playing = playback.timer !== null;
    const total = hasRun ? playback.run.steps.length : 0;

    document.getElementById("playback-play").disabled = !hasRun || playing || atEnd();
    document.getElementById("playback-pause").disabled = !playing;
    document.getElementById("playback-previous").disabled = !hasRun || playback.position <= -1;
    document.getElementById("playback-next").disabled = !hasRun || atEnd();
    document.getElementById("playback-replay").disabled = !hasRun;
    document.getElementById("playback-progress").textContent =
        `Step ${hasRun ? playback.position + 1 : 0} / ${total}`;

    /* Method previews pause while playback plays, and return when it's paused or finished. */
    setPreviewAllowed(!playing);
}


/* =========================
   Event Listeners
   ========================= */

document.getElementById("playback-play").addEventListener("click", playPlayback);
document.getElementById("playback-pause").addEventListener("click", stopPlayback);
document.getElementById("playback-previous").addEventListener("click", previousStep);
document.getElementById("playback-next").addEventListener("click", nextStep);
document.getElementById("playback-replay").addEventListener("click", replayPlayback);
