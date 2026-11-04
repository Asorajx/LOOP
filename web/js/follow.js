/* =========================
   Auto-scroll State
   ========================= */

/* Scroll durations in milliseconds; all are shorter than one 1400ms playback step. */
const FOLLOW_DURATION = 650;
const ENTRANCE_MIN = 700;
const ENTRANCE_MAX = 1200;
const AUTO_SCROLL_KEY = "loop-auto-scroll";

/* enabled is the Auto-scroll setting. active turns off when the visitor scrolls, */
/* and back on when they start a run or press Play, Previous, Next or Follow. */
const follow = {
    enabled: true,
    active: true,
    animation: null,
    busyUntil: 0,
    card: null
};

const autoScrollToggle = document.getElementById("toggle-auto-scroll");
const terminalDock = document.getElementById("terminal-dock");
const terminalSection = document.querySelector(".terminal");

try {
    follow.enabled = localStorage.getItem(AUTO_SCROLL_KEY) !== "off";
} catch (error) {
    /* Storage can be blocked; auto-scroll stays on. */
}
autoScrollToggle.checked = follow.enabled;


/* =========================
   Page Scrolling
   ========================= */

function cancelPageScroll() {
    if (follow.animation !== null) window.cancelAnimationFrame(follow.animation);
    follow.animation = null;
    follow.busyUntil = 0;
}

/* Eased scroll with a fixed duration. Each frame jumps instantly, overriding scroll-behavior: smooth. */
function scrollPageBy(delta, duration) {
    cancelPageScroll();
    const start = window.scrollY;
    const end = Math.max(0, Math.min(start + delta, document.documentElement.scrollHeight - window.innerHeight));
    if (Math.abs(end - start) < 4) return;

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        window.scrollTo({ top: end, behavior: "instant" });
        return;
    }

    const began = performance.now();
    follow.busyUntil = began + duration;
    const frame = function(now) {
        const t = Math.min(1, (now - began) / duration);
        const eased = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
        window.scrollTo({ top: start + (end - start) * eased, behavior: "instant" });
        follow.animation = t < 1 ? window.requestAnimationFrame(frame) : null;
    };
    follow.animation = window.requestAnimationFrame(frame);
}

/* How far to scroll so a step's line is in view, below the compact Terminal. */
/* A class that fits is shown whole; in a longer class the line goes about a quarter of the */
/* way down, so the rest of its method shows below it, but never past the end of the class. */
function stepScrollDelta(step) {
    const key = `${step.file}:${step.line}`;
    const line = document.querySelector(`#actor-space .source-line[data-key="${CSS.escape(key)}"]`);
    if (!line || !line.getClientRects().length) return 0;

    const card = line.closest(".class-card") || line;
    const sameCard = card === follow.card;
    follow.card = card;

    const top = terminalDock.offsetHeight + 20;
    const bottom = window.innerHeight - 24;
    const view = bottom - top;
    if (view < 120) return 0;

    const lineRect = line.getBoundingClientRect();
    const cardRect = card.getBoundingClientRect();
    const lineVisible = lineRect.top >= top && lineRect.bottom <= bottom;

    if (cardRect.height <= view) {
        if (lineVisible && (sameCard || (cardRect.top >= top && cardRect.bottom <= bottom))) return 0;
        return cardRect.top < top ? cardRect.top - top : Math.max(0, cardRect.bottom - bottom);
    }

    if (lineVisible && lineRect.top <= top + view * 0.6) return 0;
    const delta = lineRect.top - (top + view * 0.25);
    return Math.min(delta, Math.max(cardRect.bottom - bottom, lineRect.bottom - bottom));
}

/* Called after each step shown by playback, Previous or Next (not by clicking a Terminal card). */
function followStep(step) {
    if (!step || !follow.enabled || !follow.active || performance.now() < follow.busyUntil) return;
    scrollPageBy(stepScrollDelta(step), FOLLOW_DURATION);
}

/* A new run scrolls slowly to its first line; longer distances take longer. */
function startFollowing(run) {
    follow.active = true;
    follow.card = null;
    terminalDock.hidden = false;
    updateDock();
    if (!follow.enabled || !run.steps.length) return;
    const delta = stepScrollDelta(run.steps[0]);
    scrollPageBy(delta, Math.min(ENTRANCE_MAX, Math.max(ENTRANCE_MIN, Math.abs(delta) * 0.8)));
}

function resumeFollowing() {
    follow.active = true;
    updateDock();
}

function pauseFollowing() {
    if (!follow.active) return;
    follow.active = false;
    cancelPageScroll();
    updateDock();
}


/* =========================
   Compact Terminal
   ========================= */

/* Mirrors the current step and the playback controls; shown once the Terminal scrolls out of view. */
function updateDock() {
    const run = playback.run;
    if (!run) {
        terminalDock.hidden = true;
        terminalDock.classList.remove("is-visible");
        return;
    }

    const position = playback.position;
    const step = run.steps[position];
    const last = position === run.steps.length - 1;
    const explain = step?.explain || {};
    const playing = playback.timer !== null;

    document.getElementById("dock-progress").textContent = `Step ${position + 1} / ${run.steps.length}`;
    document.getElementById("dock-story").textContent = !step ? run.story
        : last && run.summary?.story ? run.summary.story
        : explain.story || `${step.method}()`;
    document.getElementById("dock-code").textContent = step ? step.code : run.call;
    document.getElementById("dock-detail").textContent = step ? (explain.code || defaultExplanation(step)) : "is about to run.";

    const toggle = document.getElementById("dock-play");
    toggle.textContent = playing ? "Pause" : "Play";
    toggle.disabled = !playing && atEnd();
    document.getElementById("dock-previous").disabled = position <= -1;
    document.getElementById("dock-next").disabled = atEnd();
    document.getElementById("dock-follow").hidden = !follow.enabled || follow.active;
    syncDock();
}

/* Visible once the Terminal has scrolled up behind it, while the actor panels are still on screen. */
function syncDock() {
    if (terminalDock.hidden) return;
    const dockBottom = terminalDock.offsetHeight;
    const terminalGone = terminalSection.getBoundingClientRect().bottom < dockBottom;
    const actorsShown = document.getElementById("actor-space").getBoundingClientRect().bottom > dockBottom + 40;
    const visible = (terminalGone && actorsShown) || terminalDock.contains(document.activeElement);
    terminalDock.classList.toggle("is-visible", visible);
}


/* =========================
   Event Listeners
   ========================= */

/* Only real scrolling input pauses following: a tap, click or key that activates a control does not. */
const SCROLL_KEYS = ["ArrowDown", "ArrowUp", "PageDown", "PageUp", "Home", "End", " "];
const insideTerminalLog = target => target instanceof Element && Boolean(target.closest(".terminal-log"));

window.addEventListener("wheel", event => { if (!insideTerminalLog(event.target)) pauseFollowing(); }, { passive: true });
window.addEventListener("touchmove", event => { if (!insideTerminalLog(event.target)) pauseFollowing(); }, { passive: true });
window.addEventListener("keydown", function(event) {
    if (!SCROLL_KEYS.includes(event.key)) return;
    if (event.target instanceof Element && event.target.closest("button, a, input, select, textarea, [role='button'], [tabindex]")) return;
    pauseFollowing();
});
/* A press beyond the page's width is on the window scrollbar. */
window.addEventListener("pointerdown", event => { if (event.clientX >= document.documentElement.clientWidth) pauseFollowing(); });

let dockFrame = null;
const queueSyncDock = function() {
    if (dockFrame === null) dockFrame = window.requestAnimationFrame(() => { dockFrame = null; syncDock(); });
};
window.addEventListener("scroll", queueSyncDock, { passive: true });
window.addEventListener("resize", queueSyncDock, { passive: true });

autoScrollToggle.addEventListener("change", function() {
    follow.enabled = this.checked;
    if (follow.enabled) {
        follow.active = true;
        followStep(playback.run?.steps[playback.position]);
    }
    else {
        cancelPageScroll();
    }
    updateDock();
    try {
        localStorage.setItem(AUTO_SCROLL_KEY, follow.enabled ? "on" : "off");
    } catch (error) {
        /* The setting still applies for this visit. */
    }
});

document.getElementById("dock-play").addEventListener("click", () => (playback.timer !== null ? stopPlayback() : playPlayback()));
document.getElementById("dock-previous").addEventListener("click", previousStep);
document.getElementById("dock-next").addEventListener("click", nextStep);
document.getElementById("dock-follow").addEventListener("click", function() {
    follow.active = true;
    follow.card = null;
    followStep(playback.run?.steps[playback.position]);
    updateDock();
});
/* Returning to the Terminal pauses following, so playback doesn't scroll away from it. */
document.getElementById("dock-terminal").addEventListener("click", function() {
    pauseFollowing();
    scrollPageBy(terminalSection.getBoundingClientRect().top - 16, FOLLOW_DURATION);
    this.blur();
});
