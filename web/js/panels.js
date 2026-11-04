/* =========================
   Shared Helpers
   ========================= */

/* Used by every script that builds part of the page. */
function makeElement(tag, className = "", text = "") {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text) element.textContent = text;
    return element;
}

/* Show values the way Python writes them: True, False, None, and quoted strings. */
function formatValue(value) {
    if (typeof value === "string") return `"${value}"`;
    if (value === true) return "True";
    if (value === false) return "False";
    if (value === null || value === undefined) return "None";
    return String(value);
}


/* =========================
   Actor Panels
   ========================= */

/* Render each class's source, with object labels and status icons above it. */
function renderPanels(data, onAction) {
    const space = document.getElementById("actor-space");
    space.querySelectorAll(".space").forEach(panel => panel.remove());
    space.style.setProperty("--panel-count", data.panels.length);

    const actions = {};
    data.actions.forEach(action => { actions[action.method] = action; });

    data.panels.forEach(function(panel, index) {
        const section = makeElement("section", `space panel-${(index % 3) + 1}`);
        section.appendChild(makeElement("h3", "space-title", panel.title));
        panel.classes.forEach(cls => section.appendChild(renderClass(cls, data, actions, onAction)));
        space.appendChild(section);
    });
}

function renderClass(cls, data, actions, onAction) {
    const card = makeElement("div", "class-card");
    card.dataset.class = cls.name;

    /* Objects with state get a status row; other objects get a small label. */
    const meta = makeElement("div", "class-meta");
    cls.objects.forEach(function(label) {
        if (hasVisibleState(data.state[label], data)) {
            const row = makeElement("div", "object-state");
            row.dataset.object = label;
            meta.appendChild(row);
        }
        else {
            const chip = makeElement("span", "instance-chip", label);
            chip.dataset.object = label;
            meta.appendChild(chip);
        }
    });
    if (meta.childElementCount) card.appendChild(meta);

    /* Find each method's def line, skipping decorators such as @property above it. */
    const lines = data.files[cls.file];
    const defLines = {};
    cls.methods.forEach(function(method) {
        let line = method.start;
        while (line < method.end && !lines[line - 1].trim().startsWith("def ")) line += 1;
        defLines[line] = method;
    });

    const code = makeElement("div", "code-block");
    for (let number = cls.start; number <= cls.end; number += 1) {
        const method = defLines[number];
        const line = createSourceLine(cls.file, number, lines[number - 1], method);
        /* The method this line belongs to, used by highlightCallStack. */
        const owner = cls.methods.find(item => number >= item.start && number <= item.end);
        if (owner) line.dataset.ownerMethod = owner.id;
        if (method && actions[method.id]) makeActionable(line, actions[method.id], onAction);
        code.appendChild(line);
    }
    card.appendChild(code);
    return card;
}

/* Each line keeps its real file line number in data-key, which the trace highlights by. */
function createSourceLine(file, number, text, method = null) {
    const line = makeElement("div", "source-line");
    line.dataset.key = `${file}:${number}`;
    line.appendChild(makeElement("span", "line-number", String(number)));

    const content = makeElement("span", "line-text");
    const match = method && text.match(/^(\s*def )(\w+)(.*)$/);
    if (match) {
        /* Same characters as the source; only the method name is wrapped so it can be styled. */
        content.append(document.createTextNode(match[1]), makeElement("span", "def-name", match[2]),
            document.createTextNode(match[3]));
        line.classList.add("method", "def-line");
        line.dataset.method = method.id;
    }
    else {
        content.textContent = text || " ";
    }
    line.appendChild(content);
    return line;
}

/* A clickable def line has no added buttons or icons, so the code never shifts. */
function makeActionable(line, action, onAction) {
    line.classList.add("actionable");
    line.setAttribute("role", "button");
    line.tabIndex = 0;
    line.setAttribute("aria-label", `Run ${action.method}`);
    line.addEventListener("click", () => onAction(action, line));
    line.addEventListener("keydown", function(event) {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            onAction(action, line);
        }
    });
}

function hasVisibleState(attributes, data) {
    return Object.keys(attributes || {}).some(name => name in data.status);
}


/* =========================
   Object State (status icons)
   ========================= */

/* Status labels opened by a touch tap. Hover and keyboard focus reveal labels without this. */
const tappedStatus = new Set();

/* Rebuilt on every playback step, so the icons always match the traced state at that step. */
function updateObjectStates(state, data, changed = []) {
    const changedKeys = new Set(changed.map(change => `${change.object}.${change.attribute}`));

    document.querySelectorAll(".object-state").forEach(function(row) {
        const label = row.dataset.object;
        const attributes = state[label] || {};
        row.innerHTML = "";

        const title = makeElement("div", "object-title");
        title.append(makeElement("span", "object-name", data.names[label] || label),
            makeElement("span", "instance-chip", label));
        title.lastChild.dataset.object = label;
        row.appendChild(title);

        const icons = makeElement("div", "status-list");
        Object.entries(data.status).forEach(function([attribute, settings]) {
            if (!(attribute in attributes)) return;
            icons.appendChild(createStatusIcon(label, attribute, attributes[attribute], settings,
                changedKeys.has(`${label}.${attribute}`)));
        });
        row.appendChild(icons);
    });
}

/* Icon for one attribute: coloured when not normal, labelled on hover, focus or tap. */
function createStatusIcon(label, attribute, value, settings, changed) {
    const key = `${label}.${attribute}`;
    const active = value !== settings.normal;
    const text = active ? settings.label : `${attribute} = ${formatValue(value)}`;

    const status = makeElement("button", "status");
    status.type = "button";
    status.dataset.tone = active ? settings.tone : "normal";
    status.setAttribute("aria-label", active ? `${text}. ${settings.about}` : text);
    status.classList.toggle("changed", changed);
    status.classList.toggle("revealed", tappedStatus.has(key));
    status.append(createIcon(settings.icon), makeElement("span", "status-label", text));

    /* A touch tap toggles the label; blur hides it. */
    status.addEventListener("pointerup", function(event) {
        if (event.pointerType !== "touch") return;
        tappedStatus.has(key) ? tappedStatus.delete(key) : tappedStatus.add(key);
        status.classList.toggle("revealed");
    });
    status.addEventListener("blur", function() {
        tappedStatus.delete(key);
        status.classList.remove("revealed");
    });
    return status;
}


/* =========================
   Code and Object Highlighting
   ========================= */

/* Lines are matched by their real file and line number, never by searching for text. */
function highlightCode({ current = null, waiting = [], executed = [] } = {}) {
    document.querySelectorAll(".source-line.executing, .source-line.waiting-line, .source-line.executed")
        .forEach(line => line.classList.remove("executing", "waiting-line", "executed"));

    const mark = (key, className) => document
        .querySelectorAll(`.source-line[data-key="${CSS.escape(key)}"]`)
        .forEach(line => line.classList.add(className));

    executed.forEach(key => mark(key, "executed"));
    waiting.forEach(key => mark(key, "waiting-line"));
    if (current) mark(current, "executing");
}

/* Mark lines in the call stack; with no methods, nothing is dimmed. */
function highlightCallStack(methods = []) {
    const space = document.getElementById("actor-space");
    const active = new Set(methods);
    space.classList.toggle("has-execution-focus", active.size > 0);
    space.querySelectorAll(".source-line").forEach(line => {
        line.classList.toggle("in-call-stack", active.has(line.dataset.ownerMethod));
    });
}

function highlightObjects(activeObject = null, targetObject = null) {
    document.querySelectorAll(".instance-chip").forEach(function(chip) {
        chip.classList.toggle("active-instance", chip.dataset.object === activeObject);
        chip.classList.toggle("target-instance",
            chip.dataset.object === targetObject && chip.dataset.object !== activeObject);
    });
}
