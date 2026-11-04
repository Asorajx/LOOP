/* =========================
   App State and Helpers
   ========================= */

/* Loads scenarios from the API and starts actions from the code itself. */
/* Clicking an actionable def line asks for a target (when there's a choice) and runs it. */
const loop = {
    scenarioId: null,
    data: null,
    state: {},
    busy: false
};

async function requestJson(url, options = {}) {
    const response = await fetch(url, options);
    if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
    return response.json();
}

function setStatus(text) {
    document.getElementById("system-status").textContent = text;
}


/* =========================
   Scenario Tabs
   ========================= */

/* Tabs are generated from the scenarios the server finds, so a new scenario folder adds a tab. */
async function loadScenarioTabs() {
    const scenarios = await requestJson("/api/scenarios");
    const tabs = document.getElementById("scenario-tabs");
    tabs.innerHTML = "";

    scenarios.forEach(function(scenario) {
        const tab = makeElement("button", "scenario-tab", scenario.title);
        tab.type = "button";
        tab.setAttribute("role", "tab");
        tab.dataset.scenario = scenario.id;
        tab.addEventListener("click", () => selectScenario(scenario.id));
        tabs.appendChild(tab);
    });

    if (scenarios.length) await selectScenario(scenarios[0].id);
}

async function selectScenario(scenarioId) {
    document.querySelectorAll(".scenario-tab").forEach(function(tab) {
        const selected = tab.dataset.scenario === scenarioId;
        tab.classList.toggle("active", selected);
        tab.setAttribute("aria-selected", String(selected));
    });

    setStatus("Loading scenario…");
    const data = await requestJson(`/api/scenarios/${encodeURIComponent(scenarioId)}`);
    loop.scenarioId = scenarioId;
    loop.data = data;
    loop.state = data.state;

    closeTargetPicker();
    setKnownRoutes(data.routes);
    renderPanels(data, chooseTarget);
    clearRun();
    updateObjectStates(loop.state, data);
    setStatus("");
}


/* =========================
   Target Picker
   ========================= */

/* Actions with only one possible target run straight away. */
function chooseTarget(action, line) {
    if (loop.busy) return;
    if (action.targets.length === 1) {
        closeTargetPicker();
        runAction(action, action.targets[0]);
        return;
    }
    openTargetPicker(action, line);
}

/* The picker floats under the clicked line, so opening it never moves the code. */
function openTargetPicker(action, line) {
    const picker = document.getElementById("target-picker");
    const space = document.getElementById("actor-space");
    const lineRect = line.getBoundingClientRect();
    const spaceRect = space.getBoundingClientRect();

    picker.innerHTML = "";
    picker.appendChild(makeElement("span", "target-picker-label", "Run on"));
    action.targets.forEach(function(target) {
        const button = makeElement("button", "target-option", loop.data.names[target] || target);
        button.type = "button";
        button.title = target;
        button.addEventListener("click", function() {
            closeTargetPicker();
            runAction(action, target);
        });
        picker.appendChild(button);
    });

    picker.style.left = `${lineRect.left - spaceRect.left + 24}px`;
    picker.style.top = `${lineRect.bottom - spaceRect.top + 4}px`;
    picker.hidden = false;
    document.querySelectorAll(".def-line.choosing").forEach(item => item.classList.remove("choosing"));
    line.classList.add("choosing");
    picker.querySelector("button").focus();
}

function closeTargetPicker() {
    document.getElementById("target-picker").hidden = true;
    document.querySelectorAll(".def-line.choosing").forEach(item => item.classList.remove("choosing"));
}


/* =========================
   Running and Resetting
   ========================= */

/* The server runs the real Python; the browser then plays back the recorded steps. */
async function runAction(action, target) {
    if (loop.busy) return;
    loop.busy = true;
    setStatus("Running Python…");

    try {
        const run = await requestJson(
            `/api/scenarios/${encodeURIComponent(loop.scenarioId)}/actions/${encodeURIComponent(action.id)}`,
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ target })
            }
        );
        loop.state = run.after;
        addRoutesFromRun(run);
        loadRun(run, target);
        playPlayback();
        setStatus("");
    }
    catch (error) {
        setStatus("The action could not run. Is the LOOP server running?");
        console.error(error);
    }
    finally {
        loop.busy = false;
    }
}

async function resetScenario() {
    if (!loop.scenarioId) return;
    try {
        loop.state = await requestJson(`/api/scenarios/${encodeURIComponent(loop.scenarioId)}/reset`, { method: "POST" });
        clearRun();
        updateObjectStates(loop.state, loop.data);
        setStatus("Every object is back to its starting values");
    }
    catch (error) {
        setStatus("Reset failed. Is the LOOP server running?");
        console.error(error);
    }
}


/* =========================
   Theme Switch
   ========================= */

/* The <head> script has already set data-theme before the page was drawn. */
/* This keeps the switch in step with it, saves the visitor's choice, and */
/* follows the system setting until the visitor picks a theme themselves. */
const THEME_KEY = "loop-theme";
const themeToggle = document.getElementById("theme-toggle");
const systemDark = window.matchMedia("(prefers-color-scheme: dark)");

/* localStorage can be missing or blocked (private windows, strict settings), so every access is guarded. */
function savedTheme() {
    try {
        const theme = localStorage.getItem(THEME_KEY);
        return theme === "dark" || theme === "light" ? theme : null;
    } catch (error) {
        return null;
    }
}

/* Screen readers hear a "Dark mode" switch and its state; the tooltip names what pressing it will do. */
function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    themeToggle.checked = theme === "dark";
    themeToggle.closest("label").title = theme === "dark" ? "Switch to light mode" : "Switch to dark mode";
}

function chooseTheme() {
    const theme = themeToggle.checked ? "dark" : "light";
    applyTheme(theme);
    try {
        localStorage.setItem(THEME_KEY, theme);
    } catch (error) {
        /* The choice still applies for this visit; it just won't be remembered. */
    }
}


/* =========================
   Event Listeners
   ========================= */

/* Close the target picker when clicking anywhere else, or with Escape. */
document.addEventListener("click", function(event) {
    if (!event.target.closest("#target-picker, .def-line.actionable")) closeTargetPicker();
});
document.addEventListener("keydown", event => { if (event.key === "Escape") closeTargetPicker(); });

document.getElementById("playback-reset").addEventListener("click", resetScenario);

/* Line numbers are hidden by default. The gutter keeps its width either way, so the code never shifts. */
document.getElementById("toggle-lines").addEventListener("click", function() {
    const show = document.body.classList.toggle("show-line-numbers");
    this.setAttribute("aria-pressed", String(show));
    this.textContent = show ? "Hide line numbers" : "Show line numbers";
});

themeToggle.addEventListener("change", chooseTheme);
systemDark.addEventListener("change", event => { if (!savedTheme()) applyTheme(event.matches ? "dark" : "light"); });


/* =========================
   Start
   ========================= */

applyTheme(savedTheme() || (systemDark.matches ? "dark" : "light"));
renderFundamentals();
loadScenarioTabs().catch(function(error) {
    setStatus("Could not reach the LOOP server. Start it with: python -m uvicorn api:app");
    console.error(error);
});
