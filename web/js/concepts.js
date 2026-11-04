/* =========================
   OOP Concepts
   ========================= */

/* Shared by the OOP Fundamentals section and the Terminal's concept tags. */
/* Scenario explanations refer to these by id, and tests check the ids match. */
const PYTHON_CLASSES_DOCS = "https://docs.python.org/3/tutorial/classes.html";

const CONCEPTS = {
    classes: {
        name: "Classes and objects",
        summary: "A class is a blueprint. Each object made from it keeps its own attribute values.",
        docs: `${PYTHON_CLASSES_DOCS}#a-first-look-at-classes`
    },
    attributes: {
        name: "Attributes",
        summary: "Values stored on an object, such as device.infected.",
        docs: `${PYTHON_CLASSES_DOCS}#class-and-instance-variables`
    },
    methods: {
        name: "Methods",
        summary: "Functions defined in a class. Each call runs on one object, which the method receives as self.",
        docs: `${PYTHON_CLASSES_DOCS}#method-objects`
    },
    inheritance: {
        name: "Inheritance",
        summary: "A child class reuses a parent class. It can override a method and call the parent's version with super().",
        docs: `${PYTHON_CLASSES_DOCS}#inheritance`
    },
    encapsulation: {
        name: "Encapsulation",
        summary: "An object manages its own state through its methods. A leading underscore marks an attribute as internal by convention; Python has no truly private attributes.",
        docs: `${PYTHON_CLASSES_DOCS}#private-variables`
    },
    polymorphism: {
        name: "Polymorphism",
        summary: "Code calls the same method on different objects, and each object's class decides what happens.",
        docs: "https://docs.python.org/3/glossary.html#term-duck-typing"
    },
    abstraction: {
        name: "Abstraction",
        summary: "An abstract base class declares methods that every subclass must provide, without saying how.",
        docs: "https://docs.python.org/3/library/abc.html"
    },
    relationships: {
        name: "Object relationships",
        summary: "Objects can hold references to other objects and call their methods.",
        docs: `${PYTHON_CLASSES_DOCS}#instance-objects`
    }
};


/* =========================
   OOP Fundamentals
   ========================= */

function renderFundamentals() {
    const grid = document.getElementById("concept-grid");
    if (!grid) return;

    grid.innerHTML = "";
    Object.values(CONCEPTS).forEach(function(concept) {
        const card = document.createElement("article");
        card.className = "concept-card";
        card.innerHTML = `<h3></h3><p></p><a class="icon-link" target="_blank" rel="noopener noreferrer">Python docs<span class="visually-hidden"> (opens in a new tab)</span></a>`;
        card.querySelector("h3").textContent = concept.name;
        card.querySelector("p").textContent = concept.summary;
        card.querySelector("a").href = concept.docs;
        card.querySelector("a").appendChild(createIcon("external"));
        grid.appendChild(card);
    });
}
