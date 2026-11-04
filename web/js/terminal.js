/* =========================
   Terminal
   ========================= */

/* Before anything runs, the Terminal suggests the scenario's first action as a starting point. */
let terminalHint = null;

function setTerminalHint(action) {
    terminalHint = action ? action.method.split(".") : null;
}

/* One card per step: Story, Code and Concept. Earlier cards collapse; a summary card ends the action. */
function renderTerminal(run, position, onSelect) {
    const log = document.getElementById("terminal-log");
    document.getElementById("terminal-call").textContent = run ? run.call : "";
    log.innerHTML = "";

    if (!run) {
        const empty = makeElement("div", "terminal-empty");
        const [className, methodName] = terminalHint || [];
        const tryFirst = className ? `Try ${methodName} in ${className}. ` : "";
        empty.append(
            makeElement("strong", "", "Click a method name in the code below to run it."),
            makeElement("span", "", `${tryFirst}Each step of the real Python code will be explained here.`)
        );
        log.appendChild(empty);
        return;
    }

    /* Remember where each explanation first appeared, so a repeat can refer back instead. */
    const firstConcept = {};
    for (let index = 0; index < position; index += 1) {
        const key = conceptKey(run.steps[index].explain);
        if (key && !(key in firstConcept)) firstConcept[key] = index;
    }

    log.appendChild(createIntroCard(run, position, onSelect));
    for (let index = 0; index <= position; index += 1) {
        log.appendChild(createStepCard(run.steps[index], index === position, firstConcept, onSelect));
    }
    if (position === run.steps.length - 1) {
        log.appendChild(createFinishCard(run));
    }

    const current = log.querySelector(".terminal-entry.finish") || log.querySelector(".terminal-entry.current");
    if (current) scrollWithin(log, current);
}

/* Scroll inside the Terminal only, so the page itself doesn't jump. */
function scrollWithin(container, element) {
    const containerRect = container.getBoundingClientRect();
    const elementRect = element.getBoundingClientRect();
    const target = container.scrollTop + elementRect.top - containerRect.top
        - container.clientHeight / 2 + elementRect.height / 2;
    container.scrollTo({ top: Math.max(0, target), behavior: "smooth" });
}


/* =========================
   Terminal Cards
   ========================= */

function createIntroCard(run, position, onSelect) {
    const card = makeElement("article", "terminal-entry intro");
    card.classList.toggle("current", position === -1);
    card.addEventListener("click", () => onSelect(-1));

    const head = makeElement("div", "terminal-entry-head");
    head.append(makeElement("span", "terminal-entry-number", "00"), makeElement("span", "terminal-entry-title", "Action"));
    card.append(head, makeElement("p", "terminal-story", run.story));

    if (position === -1) {
        const code = createRow("Code", "");
        code.querySelector(".terminal-row-text").append(
            makeElement("code", "terminal-code", run.call),
            document.createTextNode(" is about to run."));
        card.appendChild(code);
    }
    return card;
}

function createStepCard(step, isCurrent, firstConcept, onSelect) {
    const card = makeElement("article", "terminal-entry");
    card.classList.toggle("current", isCurrent);
    card.addEventListener("click", () => onSelect(step.index));

    const explain = step.explain || {};
    const head = makeElement("div", "terminal-entry-head");
    head.append(
        makeElement("span", "terminal-entry-number", String(step.index + 1).padStart(2, "0")),
        makeElement("span", "terminal-entry-title", step.kind === "call" ? `→ ${step.method}()` : `${step.method}()`),
        makeElement("span", "terminal-entry-meta line-ref", `line ${step.line}`)
    );
    card.appendChild(head);

    /* Earlier steps show just their story, or their code if they have no story. */
    if (!isCurrent) {
        card.appendChild(makeElement("p", explain.story ? "terminal-story" : "terminal-summary", explain.story || step.code));
        return card;
    }

    if (explain.story) card.appendChild(createRow("Story", explain.story, "story"));

    const code = createRow("Code", "");
    const text = code.querySelector(".terminal-row-text");
    text.append(makeElement("code", "terminal-code", step.code));
    const meaning = explain.code || defaultExplanation(step);
    if (meaning) text.append(document.createTextNode(` ${meaning}`));
    card.appendChild(code);

    if (step.changes.length) {
        card.appendChild(createRow("Changed", step.changes
            .map(change => `${capitalise(loop.data.names[change.object] || change.object)}: ${change.attribute} ${formatValue(change.old)} → ${formatValue(change.new)}`)
            .join("\n"), "state"));
    }

    const concept = CONCEPTS[explain.concept];
    if (concept) {
        const earlier = firstConcept[conceptKey(explain)];
        card.appendChild(createConceptRow(concept, earlier === undefined
            ? (explain.detail || concept.summary)
            : `Same idea as step ${earlier + 1}.`));
    }

    return card;
}

function createFinishCard(run) {
    const card = makeElement("article", "terminal-entry finish");
    const summary = run.summary || {};
    const head = makeElement("div", "terminal-entry-head");
    head.append(makeElement("span", "terminal-entry-title", "Summary"));
    card.appendChild(head);

    if (summary.story) card.appendChild(makeElement("p", "terminal-story", summary.story));

    const concept = CONCEPTS[summary.concept];
    if (concept && summary.lesson) card.appendChild(createConceptRow(concept, summary.lesson));

    card.appendChild(makeElement("p", "terminal-note", "The objects keep this state for your next action."));
    return card;
}

function createRow(label, text, className = "") {
    const row = makeElement("div", `terminal-row ${className}`.trim());
    row.append(makeElement("span", "terminal-label", label), makeElement("span", "terminal-row-text", text));
    return row;
}

/* The concept name links to the Python docs without also selecting the card. */
function createConceptRow(concept, text) {
    const row = makeElement("div", "terminal-concept");
    const tag = makeElement("a", "concept-tag", concept.name);
    tag.href = concept.docs;
    tag.target = "_blank";
    tag.rel = "noopener noreferrer";
    tag.title = "Open the Python documentation";
    tag.addEventListener("click", event => event.stopPropagation());
    row.append(tag, makeElement("span", "", text));
    return row;
}


/* =========================
   Text Helpers
   ========================= */

function capitalise(text) {
    return text.charAt(0).toUpperCase() + text.slice(1);
}

/* Two steps repeat an explanation only if both the concept and its detail match. */
function conceptKey(explain) {
    return explain?.concept ? `${explain.concept}:${explain.detail || ""}` : null;
}

/* Used when a step has no hand-written explanation. */
function defaultExplanation(step) {
    if (step.kind === "call") {
        const kind = step.route?.kind;
        if (kind === "super") return `super() runs ${step.method}() on the same ${step.object} object.`;
        if (kind === "property") return `Reading this property runs ${step.method}.`;
        return `Python enters ${step.method}()${step.object ? ` on ${step.object}` : ""}.`;
    }
    if ("returns" in step) return `Sends ${formatValue(step.returns)} back to the code that called ${step.method.split(".")[1]}().`;
    return "";
}
