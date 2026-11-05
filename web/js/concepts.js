/* =========================
   OOP Concepts
   ========================= */

/* Shared by the OOP Fundamentals section and the Terminal's concept tags. */
/* Scenario explanations refer to these by id, and tests check the ids match. */
const PYTHON_CLASSES_DOCS = "https://docs.python.org/3/tutorial/classes.html";

const CONCEPTS = {
    classes: {
        name: "Classes and objects",
        summary: "One blueprint, many independent objects.",
        detail: "Think of a class as a blueprint for making objects. Objects created from the same class share the same kinds of actions, but they each keep their own information.",
        example: "In Library, Book is a class. Book A and Book B are different objects. Borrowing Book A does not mean Book B is borrowed.",
        docs: `${PYTHON_CLASSES_DOCS}#a-first-look-at-classes`
    },
    attributes: {
        name: "Attributes",
        summary: "Information an object stores about itself.",
        detail: "Attributes hold information about an object. Two objects of the same class can store different values for the same attribute.",
        example: "In Cybersecurity, Device A can have infected = True while Device B has infected = False. Each device tracks its own infection status.",
        docs: `${PYTHON_CLASSES_DOCS}#class-and-instance-variables`
    },
    properties: {
        name: "Properties",
        summary: "Access a method like an attribute.",
        detail: "A property looks like an attribute when you read it, but Python runs a method to work out the value. It does not need to store a separate answer.",
        example: "In Library, Book A's available property checks whether borrowed_by is None. Its answer changes when the borrower changes.",
        docs: "https://docs.python.org/3/library/functions.html#property"
    },
    methods: {
        name: "Methods",
        summary: "Actions an object can perform.",
        detail: "A method is an action an object can perform. When a method runs, it works with the particular object that received the call.",
        example: "In Library, Member A asks City Library to lend Book A. The Book's borrow() method checks and records its own loan.",
        docs: `${PYTHON_CLASSES_DOCS}#method-objects`
    },
    inheritance: {
        name: "Inheritance",
        summary: "Reuse and customise parent-class behaviour.",
        detail: "A child class can reuse actions from a parent class, while adding or changing behaviour of its own.",
        example: "In Smart Home, Light inherits from SmartDevice. Its turn_on() calls the parent's version using super(), then sets brightness to 100.",
        docs: `${PYTHON_CLASSES_DOCS}#inheritance`
    },
    encapsulation: {
        name: "Encapsulation",
        summary: "Keep an object's data and methods together.",
        detail: "Encapsulation means keeping an object's information together with the actions that manage it. Other objects can ask it to do something instead of changing its details themselves.",
        example: "In Library, City Library asks Book A to handle the loan. Book A checks availability and sets its own borrowed_by attribute.",
        docs: `${PYTHON_CLASSES_DOCS}#private-variables`
    },
    polymorphism: {
        name: "Polymorphism",
        summary: "Same method call, different behaviour.",
        detail: "The same method call can work with different kinds of objects. Each type can carry out the action in its own way.",
        example: "In Smart Home, Main Hub calls turn_on() on a Light or a Fan. The Light sets brightness, while the Fan sets speed.",
        docs: "https://docs.python.org/3/glossary.html#term-duck-typing"
    },
    abstraction: {
        name: "Abstraction",
        summary: "Define methods subclasses must provide.",
        detail: "An abstract class defines methods that its subclasses must have, leaving each subclass to decide how they work.",
        example: "In Cybersecurity, the Attack class requires an execute() method. MalwareAttack provides its own execute() to infect the target.",
        docs: "https://docs.python.org/3/library/abc.html"
    },
    relationships: {
        name: "Object relationships",
        summary: "Objects interact and work together.",
        detail: "Objects can cooperate by calling each other's methods. They can also remember which other objects they are connected to.",
        example: "In Library, Member A asks City Library for Book A. Book A then stores a reference to Member A as its borrower.",
        docs: `${PYTHON_CLASSES_DOCS}#instance-objects`
    }
};


/* =========================
   OOP Fundamentals
   ========================= */

function createDocsLink(href) {
    const link = makeElement("a", "icon-link", "Python docs");
    link.href = href;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.append(makeElement("span", "visually-hidden", " (opens in a new tab)"), createIcon("external"));
    return link;
}

/* The arrow is decoration, so screen readers hear only "Previous" or "Next". */
function createStepButton(label, arrow, arrowFirst) {
    const button = makeElement("button", "concept-focus-nav-button", label);
    button.type = "button";
    const icon = makeElement("span", "", arrow);
    icon.setAttribute("aria-hidden", "true");
    arrowFirst ? button.prepend(icon) : button.append(icon);
    return button;
}

/* The flat grid shows every concept. Selecting one grows it into the full-width view. */
/* Both views stay in the page so the browser can animate between them. */
function renderFundamentals() {
    const grid = document.getElementById("concept-grid");
    const focus = document.getElementById("concept-focus");
    if (!grid || !focus) return;

    grid.replaceChildren();
    focus.replaceChildren();
    const concepts = Object.values(CONCEPTS);
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    let current = 0;
    let transitioning = false;

    /* The whole concept area is one button, so it is easy to click and to reach by keyboard. */
    const triggers = concepts.map(function(concept, index) {
        const trigger = makeElement("button", "concept-card-trigger");
        trigger.type = "button";
        trigger.setAttribute("aria-expanded", "false");
        trigger.setAttribute("aria-controls", "concept-focus");
        trigger.style.viewTransitionName = `loop-card-${index}`;
        trigger.append(
            makeElement("span", "concept-card-title", concept.name),
            makeElement("span", "concept-card-summary", concept.summary)
        );
        trigger.addEventListener("click", () => openConcept(index));
        const card = makeElement("article", "concept-card");
        card.appendChild(trigger);
        grid.appendChild(card);
        return trigger;
    });

    const count = makeElement("span", "concept-focus-count");
    const collapse = makeElement("button", "concept-focus-close", "Collapse");
    collapse.type = "button";
    const top = makeElement("div", "concept-focus-top");
    top.append(count, collapse);

    const title = makeElement("h3", "concept-focus-title");
    title.id = "concept-focus-title";
    title.tabIndex = -1;

    const body = makeElement("div", "concept-focus-body");
    const texts = ["Explanation", "Example from LOOP"].map(function(heading) {
        const block = makeElement("div", "concept-focus-block");
        const paragraph = makeElement("p");
        block.append(makeElement("h4", "", heading), paragraph);
        body.appendChild(block);
        return paragraph;
    });

    const docs = createDocsLink("");
    const previous = createStepButton("Previous", "\u2190", true);
    const next = createStepButton("Next", "\u2192", false);
    const nav = makeElement("div", "concept-focus-nav");
    nav.append(previous, next);
    const bottom = makeElement("div", "concept-focus-bottom");
    bottom.append(docs, nav);
    focus.append(top, title, body, bottom);

    function showConcept(index) {
        /* After Previous/Next, Collapse shrinks into the concept now shown, not the first one opened. */
        triggers[current].style.viewTransitionName = `loop-card-${current}`;
        current = index;
        triggers[current].style.viewTransitionName = "loop-concept";
        count.textContent = `Concept ${index + 1} of ${concepts.length}`;
        title.textContent = concepts[index].name;
        texts[0].textContent = concepts[index].detail;
        texts[1].textContent = concepts[index].example;
        docs.href = concepts[index].docs;
        previous.disabled = index === 0;
        next.disabled = index === concepts.length - 1;
    }

    /* A view transition animates the concept between its card and the full-width view. */
    /* Browsers without view transitions, or with reduced motion, switch instantly. */
    function changeView(update, finished) {
        transitioning = true;
        const supportsTransition = typeof document.startViewTransition === "function";
        if (reducedMotion.matches || !supportsTransition) {
            update();
            transitioning = false;
            finished();
            return;
        }
        const transition = document.startViewTransition(update);
        /* A transition cut short, for example by leaving the tab, isn't an error. */
        transition.ready.catch(() => {});
        transition.finished.catch(() => {}).then(function() {
            transitioning = false;
            finished();
        });
    }

    function openConcept(index) {
        if (transitioning || !focus.hidden) return;
        showConcept(index);
        changeView(function() {
            grid.hidden = true;
            focus.hidden = false;
            focus.style.viewTransitionName = "loop-concept";
            triggers[current].setAttribute("aria-expanded", "true");
            /* On a phone the last card sits far below the shorter view, which would start off-screen. */
            if (focus.getBoundingClientRect().top < 0) focus.scrollIntoView({ block: "start", behavior: "instant" });
        }, () => title.focus({ preventScroll: true }));
    }

    /* A click elsewhere on the page closes without returning to the card, so the page doesn't jump. */
    function closeConcept(returnToCard = true) {
        if (transitioning || focus.hidden) return;
        const trigger = triggers[current];
        changeView(function() {
            focus.hidden = true;
            grid.hidden = false;
            trigger.setAttribute("aria-expanded", "false");
            if (returnToCard) trigger.scrollIntoView({ block: "nearest", behavior: "instant" });
        }, function() {
            focus.style.viewTransitionName = "";
            trigger.style.viewTransitionName = `loop-card-${current}`;
            if (returnToCard) trigger.focus({ preventScroll: true });
        });
    }

    /* At the first or last concept the pressed button turns off, so focus moves to the other one. */
    function step(change, pressed, other) {
        const index = current + change;
        if (transitioning || index < 0 || index >= concepts.length) return;
        showConcept(index);
        if (pressed.disabled) other.focus();
    }

    previous.addEventListener("click", () => step(-1, previous, next));
    next.addEventListener("click", () => step(1, next, previous));
    collapse.addEventListener("click", () => closeConcept());

    /* Closing on click, not pointerdown, lets other controls finish their own action first. */
    document.addEventListener("click", function(event) {
        if (!focus.hidden && !focus.contains(event.target) && !grid.contains(event.target)) {
            closeConcept(false);
        }
    });
    /* Escape also closes the Playground's pickers, so only act when focus is in this section. */
    const section = grid.parentElement;
    document.addEventListener("keydown", function(event) {
        const here = section.contains(document.activeElement) || document.activeElement === document.body;
        if (event.key === "Escape" && !focus.hidden && here) closeConcept();
    });
}
