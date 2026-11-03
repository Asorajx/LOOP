/*
 * LOOP Learning Studio
 * Educational content is intentionally kept separate from the Python engine.
 * Examples describe the actual classes in this repository; playback explanations
 * are derived from the events returned by FastAPI, not simulated in the browser.
 */

const pythonClassesDocs = "https://docs.python.org/3/tutorial/classes.html";
const learningConcepts = [
    {
        id: "classes", name: "Classes & objects", eyebrow: "Blueprint vs instance",
        question: "If DEV001 changes, does DEV002 have to change too?",
        definition: "A class defines how an object behaves. An instance is a particular object created from that class, with its own attribute values.",
        diagram: ["CLASS · NetworkDevice", "INSTANCE · DEV001", "INSTANCE · DEV002"],
        example: "NetworkDevice creates two separate devices. Both support increase_risk(), but the risk level belongs to each individual device. Run the example and notice which object's state changes.",
        code: 'device1 = NetworkDevice("DEV001", "Web Server")\ndevice2 = NetworkDevice("DEV002", "Database Server")\n\ndevice1.increase_risk(1)  # Only DEV001 changes',
        why: "Why this matters: classes let us reuse behaviour without accidentally sharing every instance's state.",
        docs: `${pythonClassesDocs}#class-and-instance-variables`,
        check: {
            question: "After device1.increase_risk(1), what happens to device2.risk_level?",
            choices: ["It also increases", "It stays at its previous value", "The class stops working"],
            answer: 1,
            explanation: "Each NetworkDevice instance stores its own __risk_level. Calling a method on DEV001 does not automatically change DEV002."
        },
        notes: {
            "device-increase-risk": "This method belongs to NetworkDevice, but it is currently running on a particular instance: DEV001."
        },
        start: "Compare the DEV001 and DEV002 labels below. Both are objects made from the NetworkDevice blueprint. Now run the example."
    },
    {
        id: "encapsulation", name: "Encapsulation", eyebrow: "Control state through methods",
        question: "Why call a method instead of editing an attribute directly?",
        definition: "Encapsulation bundles an object's state and behaviour. Other objects ask it to perform operations through its methods, so the object can enforce rules about updates.",
        diagram: ["CredentialAttack", "calls increase_risk(1)", "DEV001 owns risk_level"],
        example: "CredentialAttack.execute() calls target.increase_risk(1). Inside NetworkDevice, increase_risk() updates the risk value and caps it at 3.",
        code: 'def execute(self, target):\n    target.increase_risk(1)\n\n# Inside NetworkDevice:\ndef increase_risk(self, amount=1):\n    self.__risk_level += amount\n    if self.__risk_level > 3:\n        self.__risk_level = 3',
        why: "Why this matters: the device is responsible for its own rules. In Python, __name uses name mangling; it is not an absolute privacy or security boundary.",
        docs: `${pythonClassesDocs}#private-variables`,
        check: {
            question: "Who should apply the maximum risk limit of 3?",
            choices: ["Every attack class independently", "The NetworkDevice method that changes risk", "The browser's animation"],
            answer: 1,
            explanation: "Keeping the rule inside NetworkDevice.increase_risk() avoids duplicating it across all callers."
        },
        notes: {
            "credential-execute": "CredentialAttack does not reach inside the device to assign a risk value. It asks the target to do the update.",
            "device-increase-risk": "NetworkDevice handles its own state. This is where the risk cap is enforced."
        },
        start: "Watch the call move from CredentialAttack.execute() to NetworkDevice.increase_risk(). Who owns the risk data?"
    },
    {
        id: "relationships", name: "Object relationships", eyebrow: "Objects collaborate",
        question: "How can one object interact with two different objects?",
        definition: "Objects can keep references to other objects and call their methods. This is an object relationship; in this example, it is most precise to describe it as an association, rather than claiming strict lifecycle-owned composition.",
        diagram: ["CON001 · Connection", "reference → DEV001", "reference → DEV002"],
        example: "Connection receives two existing NetworkDevice instances in its constructor. Its intercept() method changes its own intercepted state and asks both devices to increase risk.",
        code: 'connection = Connection("CON001", device1, device2)\n\n# Inside Connection.intercept():\nself.__intercepted = True\nself.__device1.increase_risk(1)\nself.__device2.increase_risk(1)',
        why: "Why this matters: separating responsibilities allows Connection to model a link while NetworkDevice manages each endpoint's state. The devices are created independently of the connection.",
        docs: `${pythonClassesDocs}#a-first-look-at-classes`,
        check: {
            question: "Who stores the references to the two devices?",
            choices: ["The Connection instance", "The browser", "The abstract Attack base class"],
            answer: 0,
            explanation: "Connection stores device references as attributes; it does not need to recreate each device to call its methods."
        },
        notes: {
            "mitm-execute": "The attack calls the Connection object's intercept() method, rather than working on both devices itself.",
            "connection-intercept": "Connection uses its references to the two existing NetworkDevice objects and asks each to update its risk.",
            "device-increase-risk": "One of the referenced device objects is now executing its own state-changing method."
        },
        start: "Follow the order: MitMAttack → CON001 → DEV001 → DEV002. The objects collaborate through method calls."
    },
    {
        id: "inheritance", name: "Inheritance & super()", eyebrow: "Reuse and extend behaviour",
        question: "What executes when a child class calls super()?",
        definition: "A child class can inherit behaviour from a parent and override methods. In DDoSAttack.execute(), super().execute(target) invokes the inherited DoSAttack implementation on the same DDoSAttack instance before continuing.",
        diagram: ["Attack (abstract)", "DoSAttack (parent)", "DDoSAttack (child)"],
        example: "DDoSAttack extends DoSAttack. The parent first raises risk and sets HIGH traffic; the child then raises risk again and sets CRITICAL traffic.",
        code: 'class DDoSAttack(DoSAttack):\n    def execute(self, target):\n        super().execute(target)\n        target.increase_risk(1)\n        target.overload("CRITICAL")',
        why: "Why this matters: the child reuses common behaviour instead of copying all the parent code, while still adding something distinct.",
        docs: `${pythonClassesDocs}#inheritance`,
        check: {
            question: "Does super().execute(target) create a separate DoSAttack object?",
            choices: ["Yes, it creates a new parent object", "No, it runs the parent method using the current child instance", "It only draws an arrow in the browser"],
            answer: 1,
            explanation: "super() delegates method lookup; the inherited method runs with the current DDoSAttack instance as self."
        },
        notes: {
            "ddos-execute": "The child override runs first. Its super() call delegates to the parent's execute() implementation.",
            "dos-execute": "You are now inside DoSAttack.execute(), called by super(). The object is still the DDoSAttack instance.",
            "device-overload": "Notice the parent sets HIGH traffic, and the child later changes the same device to CRITICAL."
        },
        start: "The class diagram goes from Attack → DoSAttack → DDoSAttack. Watch the nested call into the parent method."
    },
    {
        id: "polymorphism", name: "Polymorphism", eyebrow: "One call, different implementations",
        question: "How can the same execute() call produce different results?",
        definition: "Polymorphism lets callers use a common method interface without hard-coding every subclass. Python decides which execute() implementation to run based on the actual attack object.",
        diagram: ["attack.execute(target)", "MalwareAttack.execute()", "CredentialAttack.execute()"],
        example: "Attacker.perform_attack(attack, target) calls attack.execute(target). This example passes MalwareAttack, while the next Abstraction example passes CredentialAttack through the same caller.",
        code: '# From Attacker.perform_attack():\nattack.execute(target)\n\n# Actual attack object determines the method:\nmalware.execute(device1)      # +2 risk\ncredential.execute(device1)   # +1 risk',
        why: "Why this matters: adding a new Attack subclass does not require rewriting Attacker.perform_attack() with a branch for each specific attack type.",
        docs: `${pythonClassesDocs}#inheritance`,
        check: {
            question: "When Attacker calls attack.execute(target), what chooses the implementation?",
            choices: ["The concrete class of the attack object", "The name of the target device", "The terminal text"],
            answer: 0,
            explanation: "The variable attack can reference different subclasses. Method lookup uses the runtime object type."
        },
        notes: {
            "attacker-perform": "The caller does not need to check whether the object is MalwareAttack or CredentialAttack. It simply calls execute().",
            "malware-execute": "The runtime attack object here is MalwareAttack, so its execute() implementation runs.",
            "device-increase-risk": "MalwareAttack chooses to increase risk by 2. Another subclass could implement the same execute() interface differently."
        },
        start: "Watch Attacker.perform_attack() call execute() on a MalwareAttack object. Later compare it with CredentialAttack."
    },
    {
        id: "abstraction", name: "Abstraction", eyebrow: "Define a common contract",
        question: "Why does the Attack base class declare execute() but not implement the attack?",
        definition: "Abstraction exposes the essential operation while leaving details to subclasses. In this project, Attack is an abstract base class (ABC); @abstractmethod requires concrete subclasses to implement execute() before they can be instantiated.",
        diagram: ["Attack · execute() contract", "CredentialAttack", "MalwareAttack"],
        example: "The abstract Attack class declares execute(). The actual CredentialAttack class provides one implementation. The Attacker object only needs to know that its attack has execute().",
        code: 'from abc import ABC, abstractmethod\n\nclass Attack(ABC):\n    @abstractmethod\n    def execute(self, target):\n        pass\n\nclass CredentialAttack(Attack):\n    def execute(self, target):\n        target.increase_risk(1)',
        why: "Why this matters: the ABC communicates a shared interface and prevents direct instantiation of incomplete Attack subclasses. In this project it is a design contract, not a complete security boundary.",
        docs: "https://docs.python.org/3/library/abc.html#abc.abstractmethod",
        check: {
            question: "Can Attack() be instantiated directly while execute() is abstract?",
            choices: ["Yes, always", "No, it is abstract until the method is implemented in a concrete subclass", "Only the browser decides"],
            answer: 1,
            explanation: "Python's ABC machinery prevents instantiating a class that still has unimplemented abstract methods."
        },
        notes: {
            "attacker-perform": "The caller relies on the execute() interface rather than implementing the attack itself.",
            "credential-execute": "CredentialAttack supplies the concrete behaviour required by the abstract Attack.execute() contract.",
            "device-increase-risk": "The concrete attack implementation delegates the device's own state update to NetworkDevice."
        },
        start: "The base class specifies WHAT operation is required; the subclass determines HOW that operation works."
    }
];

let selectedLearningConcept = "classes";
let lessonIsLaunching = false;

function learningSet(id, text) {
    const element = document.getElementById(id);
    if (element) element.textContent = text;
}

function renderLearningNavigation() {
    const container = document.getElementById("lesson-buttons");
    if (!container) return;
    container.replaceChildren();
    for (const [index, lesson] of learningConcepts.entries()) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "lesson-nav-button";
        button.dataset.lesson = lesson.id;
        button.textContent = `${String(index + 1).padStart(2, "0")}  ${lesson.name}`;
        button.addEventListener("click", () => selectLearningConcept(lesson.id));
        container.appendChild(button);
    }
}

function renderLearningDiagram(concept) {
    const diagram = document.getElementById("lesson-diagram");
    if (!diagram) return;
    diagram.replaceChildren();
    const branching = ["classes", "relationships", "polymorphism", "abstraction"].includes(concept.id);
    if (branching) {
        const parent = document.createElement("span");
        parent.className = "lesson-diagram-node";
        parent.textContent = concept.diagram[0];
        const children = document.createElement("div");
        children.className = "lesson-diagram-branches";
        concept.diagram.slice(1).forEach(label => {
            const branch = document.createElement("div");
            const arrow = document.createElement("span");
            arrow.className = "lesson-diagram-arrow";
            arrow.textContent = "↳";
            arrow.setAttribute("aria-hidden", "true");
            const item = document.createElement("span");
            item.className = "lesson-diagram-node";
            item.textContent = label;
            branch.append(arrow, item);
            children.appendChild(branch);
        });
        diagram.append(parent, children);
    } else {
        concept.diagram.forEach((label, index) => {
            if (index > 0) {
                const arrow = document.createElement("span");
                arrow.className = "lesson-diagram-arrow";
                arrow.textContent = "→";
                arrow.setAttribute("aria-hidden", "true");
                diagram.appendChild(arrow);
            }
            const item = document.createElement("span");
            item.className = "lesson-diagram-node";
            item.textContent = label;
            diagram.appendChild(item);
        });
    }
}

const lineAnnotations = {
    classes: [
        ["NetworkDevice(...) ", "Each constructor call makes a different instance from the same blueprint."],
        ["device1.increase_risk(1)", "The method uses device1 as self. device2 has its own risk value."]
    ],
    encapsulation: [
        ["target.increase_risk(1)", "A caller asks the device to update itself instead of assigning its state directly."],
        ["if self.__risk_level > 3", "The device keeps its own upper limit. Double underscores trigger name mangling in Python."]
    ],
    relationships: [
        ["Connection(..., device1, device2)", "The connection receives existing objects and stores references to them."],
        ["self.__device1.increase_risk(1)", "One object invokes a method on another object that it references."]
    ],
    inheritance: [
        ["class DDoSAttack(DoSAttack)", "DDoSAttack is a subclass; DoSAttack is a parent class."],
        ["super().execute(target)", "Python resolves the next implementation in the method resolution order. Here that is DoSAttack.execute()."]
    ],
    polymorphism: [
        ["attack.execute(target)", "Attacker uses the same method call for any compatible concrete attack object."],
        ["malware.execute(...) / credential.execute(...)", "The actual object determines which execute() implementation runs and what happens."]
    ],
    abstraction: [
        ["@abstractmethod", "This marks a method that a concrete subclass must implement before it can be instantiated."],
        ["def execute(self, target)", "The base class specifies a shared operation without prescribing each subclass's algorithm."]
    ]
};

function renderLineAnnotations(conceptId) {
    const container = document.getElementById("lesson-annotations");
    if (!container) return;
    container.replaceChildren();
    for (const [code, explanation] of lineAnnotations[conceptId] || []) {
        const row = document.createElement("div");
        row.className = "lesson-annotation-row";
        const line = document.createElement("code");
        line.textContent = code;
        const reason = document.createElement("p");
        reason.textContent = explanation;
        row.append(line, reason);
        container.appendChild(row);
    }
}

function renderLearningCheck(concept) {
    learningSet("lesson-check-question", concept.check.question);
    learningSet("lesson-check-feedback", "Choose an answer to check your understanding.");
    const container = document.getElementById("lesson-check-options");
    if (!container) return;
    container.replaceChildren();
    concept.check.choices.forEach((choice, index) => {
        const option = document.createElement("button");
        option.type = "button";
        option.className = "lesson-check-option";
        option.textContent = choice;
        option.addEventListener("click", () => {
            for (const other of container.querySelectorAll("button")) {
                other.classList.remove("correct", "incorrect");
                other.setAttribute("aria-pressed", "false");
            }
            option.classList.add(index === concept.check.answer ? "correct" : "incorrect");
            option.setAttribute("aria-pressed", "true");
            learningSet("lesson-check-feedback", `${index === concept.check.answer ? "Correct." : "Not quite."} ${concept.check.explanation}`);
        });
        option.setAttribute("aria-pressed", "false");
        container.appendChild(option);
    });
}

function selectLearningConcept(id, fromGuide = false) {
    const concept = learningConcepts.find(lesson => lesson.id === id);
    if (!concept) return;
    if (currentMode === simulationModes.GUIDED && !fromGuide) return;
    if (isPlaying && !fromGuide) return;
    const changed = selectedLearningConcept !== id;
    selectedLearningConcept = id;
    const index = learningConcepts.indexOf(concept);
    learningSet("lesson-number", `LESSON ${String(index + 1).padStart(2, "0")} / ${String(learningConcepts.length).padStart(2, "0")} · ${concept.eyebrow}`);
    learningSet("lesson-title", concept.name);
    learningSet("lesson-question", concept.question);
    learningSet("lesson-definition", concept.definition);
    learningSet("lesson-example", concept.example);
    learningSet("lesson-code", concept.code);
    learningSet("lesson-why", concept.why);
    renderLearningDiagram(concept);
    renderLineAnnotations(concept.id);
    const docs = document.getElementById("lesson-docs");
    if (docs) docs.href = concept.docs;
    document.querySelectorAll(".lesson-nav-button").forEach(button => {
        const active = button.dataset.lesson === id;
        button.classList.toggle("active", active);
        button.setAttribute("aria-current", active ? "step" : "false");
        button.disabled = currentMode === simulationModes.GUIDED || isPlaying;
    });
    const run = document.getElementById("lesson-run");
    if (run) run.textContent = currentMode === simulationModes.GUIDED ? "Play this guided lesson" : "Run this example";
    if (changed || !document.getElementById("lesson-check-options")?.children.length) renderLearningCheck(concept);
    // Don't present old events as a demonstration of a newly selected concept.
    if (changed || !executionEvents.length) updateLearningPlayback(0, true);
}

function renderLearningInstanceState(position = 0, preferCurrentState = false) {
    const container = document.getElementById("learning-instance-cards");
    if (!container) return;
    // The snapshot before execution comes from Python via /api/state or /api/reset.
    // The intermediate state is reconstructed ONLY by applying recorded Python events.
    const baseline = preferCurrentState ? simulationState : (executionInitialState || simulationState);
    const snapshot = JSON.parse(JSON.stringify(baseline));
    for (const event of executionEvents.slice(0, position)) {
        if (event.event_type !== "STATE_CHANGED") continue;
        const item = [...snapshot.devices, ...snapshot.connections]
            .find(record => (record.device_id || record.connection_id) === event.object_id);
        if (item && Object.hasOwn(item, event.attribute)) {
            item[event.attribute] = event.new_value;
        }
    }
    container.replaceChildren();
    for (const record of snapshot.devices) {
        const card = document.createElement("div");
        card.className = "instance-state-card";
        const label = document.createElement("strong");
        label.textContent = `${record.device_id} · ${record.name}`;
        const details = document.createElement("span");
        details.textContent = `risk: ${record.risk_level} · traffic: ${record.traffic_level}`;
        card.append(label, details);
        container.appendChild(card);
    }
    for (const record of snapshot.connections) {
        const card = document.createElement("div");
        card.className = "instance-state-card";
        const label = document.createElement("strong");
        label.textContent = `${record.connection_id} · Connection`;
        const details = document.createElement("span");
        details.textContent = `intercepted: ${formatStateValue(record.intercepted)} · ${record.device1} ↔ ${record.device2}`;
        card.append(label, details);
        container.appendChild(card);
    }
}

function updateLearningPlayback(position = 0, showIntro = false) {
    const concept = learningConcepts.find(lesson => lesson.id === selectedLearningConcept);
    if (!concept) return;
    const state = document.getElementById("learning-state");
    renderLearningInstanceState(position, showIntro);
    if (state) state.hidden = true;

    const hasEvents = executionEvents.length > 0 && currentRootButton;
    if (showIntro || !hasEvents || position === 0) {
        learningSet("learning-step-count", hasEvents ? `READY · ${executionEvents.length} PYTHON EVENTS` : "BEFORE RUNNING");
        learningSet("learning-step-title", "What should you look for?");
        learningSet("learning-step-copy", concept.start);
        return;
    }

    const safePosition = Math.max(0, Math.min(position, executionEvents.length));
    const event = executionEvents[safePosition - 1];
    if (!event) return;
    learningSet("learning-step-count", `EVENT ${safePosition} / ${executionEvents.length} · ${event.event_type.replaceAll("_", " ")}`);

    const object = event.object_id || "an object";
    const method = `${event.class_name}.${event.method_name}()`;
    const contextNote = concept.notes[event.source_id];
    if (event.event_type === "STATE_CHANGED") {
        const name = event.attribute.replaceAll("_", " ");
        learningSet("learning-step-title", `${object} updated its ${name}`);
        const unchanged = event.previous_value === event.new_value;
        learningSet("learning-step-copy", `${object} owns this attribute. ${unchanged ? "The method ran, but this value stayed the same (possibly because a limit was already reached)." : "The Python method changed this object's state."} ${contextNote || "Notice which instance was affected."}`);
        learningSet("learning-state-label", `${object} · ${event.attribute}`);
        learningSet("learning-state-before", formatStateValue(event.previous_value));
        learningSet("learning-state-after", formatStateValue(event.new_value));
        if (state) state.hidden = false;
    }
    else if (event.event_type === "METHOD_STARTED") {
        learningSet("learning-step-title", `${object} is running ${event.method_name}()`);
        learningSet("learning-step-copy", `${method} started${event.target_id ? ` with target ${event.target_id}` : ""}. ${contextNote || "A method is behaviour defined on a class and executed by an object."}`);
    }
    else {
        learningSet("learning-step-title", `${event.method_name}() returned`);
        learningSet("learning-step-copy", `${object} finished ${method}. ${event.message ? `${event.message}. ` : ""}${contextNote || "Control returns to the calling method, if any."}`);
    }
    if (safePosition === executionEvents.length && !isProcessingEvent && !isPlaying) {
        learningSet("learning-step-count", `COMPLETE · ${executionEvents.length} PYTHON EVENTS`);
    }
}

async function runLearningExample() {
    if (lessonIsLaunching || isPlaying || isProcessingEvent || isResetting || isGuidedPreparing) return;
    if (currentMode === simulationModes.GUIDED) {
        await playPlayback();
        return;
    }
    const lesson = guidedScenes.find(scene => scene.concept === selectedLearningConcept);
    if (!lesson) return;
    const button = document.getElementById(lesson.action);
    const runButton = document.getElementById("lesson-run");
    if (!button) return;
    lessonIsLaunching = true;
    if (runButton) {
        runButton.disabled = true;
        runButton.textContent = "Preparing example...";
    }
    try {
        // Each example starts with the same predictable Python state.
        await resetSimulation();
        await openCodeDrawer(button);
        await executeMethod(button, lesson.request);
    }
    catch (error) {
        learningSet("learning-step-title", "Could not start the example");
        learningSet("learning-step-copy", "Check that the FastAPI server is running, then try again.");
        console.error("Learning example failed:", error);
    }
    finally {
        lessonIsLaunching = false;
        if (runButton) {
            runButton.disabled = false;
            runButton.textContent = "Run this example again";
        }
    }
}

renderLearningNavigation();
selectLearningConcept("classes", true);
document.getElementById("lesson-run")?.addEventListener("click", runLearningExample);
