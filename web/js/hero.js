/* =========================
   Hero Diagram
   ========================= */

/* A fixed picture of two Cybersecurity actions, so it shows even while the server wakes up. */
/* The routes match the calls the real code makes (launch -> execute -> infect, isolate -> disconnect). */
/* It plays once, then rests; hovering a method lights its routes again. */
const HERO_ROUTES = [
    { from: "Attacker.launch", to: "MalwareAttack.execute" },
    { from: "MalwareAttack.execute", to: "Device.infect" },
    { from: "Victim.isolate", to: "Device.disconnect" }
];

const HERO_STEPS = [
    { call: "attacker.launch(malware, device_a)", routes: [0, 1], state: "infected", value: "True", tone: "danger" },
    { call: "victim.isolate(device_a)", routes: [2], state: "online", value: "False", tone: "warning" }
];

const HERO_START_MS = 900;
const HERO_DRAW_MS = 450;
const HERO_HOLD_MS = 1100;
const HERO_GAP_MS = 450;

const heroDiagram = document.getElementById("hero-diagram");
const heroLit = new Set();
let heroPlaying = true;

const heroWait = ms => new Promise(resolve => window.setTimeout(resolve, ms));

function heroMethod(id) {
    return heroDiagram.querySelector(`[data-method="${id}"]`);
}


/* =========================
   Route Geometry
   ========================= */

/* Like routes.js: calls between side-by-side columns run along a bus in the gap. */
/* Calls within a column, and every call once the columns stack, run along a spine on the left. */
function heroRouteGeometry(route, box) {
    const measure = function(element) {
        const rect = element.getBoundingClientRect();
        return { left: rect.left - box.left, right: rect.right - box.left, y: rect.top + rect.height / 2 - box.top };
    };
    const from = heroMethod(route.from);
    const to = heroMethod(route.to);
    const a = measure(from);
    const b = measure(to);
    const columnA = measure(from.closest(".hero-actor"));
    const columnB = measure(to.closest(".hero-actor"));

    let path;
    let bus;
    if (Math.abs(columnA.left - columnB.left) < 1) {
        /* Upward calls run on an inner spine, so calls in each direction stay apart. */
        bus = columnA.left - (b.y < a.y ? 6 : 12);
        path = `M ${a.left - 6} ${a.y} H ${bus} V ${b.y} H ${b.left - 6}`;
    } else if (columnA.left < columnB.left) {
        bus = (columnA.right + columnB.left) / 2;
        path = `M ${a.right + 6} ${a.y} H ${bus} V ${b.y} H ${b.left - 6}`;
    } else {
        bus = (columnB.right + columnA.left) / 2;
        path = `M ${a.left - 6} ${a.y} H ${bus} V ${b.y} H ${b.right + 6}`;
    }
    return { path, nodes: [[bus, a.y], [bus, b.y]] };
}


/* =========================
   Drawing
   ========================= */

/* Positions are measured from the page, so this runs again whenever the layout changes. */
function drawHeroLines() {
    const svg = document.getElementById("hero-lines");
    const box = heroDiagram.getBoundingClientRect();
    svg.setAttribute("viewBox", `0 0 ${box.width} ${box.height}`);
    svg.innerHTML = "";

    HERO_ROUTES.forEach(function(route, index) {
        const geometry = heroRouteGeometry(route, box);
        const network = `net-${heroMethod(route.from).closest(".hero-actor").dataset.panel}`;
        svg.appendChild(svgElement("path", { d: geometry.path, class: `hero-line ${network}` }));
        geometry.nodes.forEach(function([x, y]) {
            svg.appendChild(svgElement("rect", { x: x - 2, y: y - 2, width: 4, height: 4, class: `hero-node ${network}` }));
        });
        svg.appendChild(svgElement("path", {
            d: geometry.path,
            pathLength: 1,
            class: `hero-route ${network}${heroLit.has(index) ? " lit" : ""}`,
            "data-route": index
        }));
    });
}

function setHeroRoute(index, lit) {
    if (lit) heroLit.add(index);
    else heroLit.delete(index);
    heroDiagram.querySelector(`.hero-route[data-route="${index}"]`)?.classList.toggle("lit", lit);
}

function setHeroState(step) {
    const value = heroDiagram.querySelector(`[data-state="${step.state}"]`);
    value.textContent = step.value;
    value.dataset.tone = step.tone;
    value.classList.add("changed");
}

async function setHeroCall(text) {
    const call = document.getElementById("hero-call");
    if (call.textContent === text) return;
    call.classList.add("swapping");
    await heroWait(150);
    call.textContent = text;
    call.classList.remove("swapping");
}


/* =========================
   Playing
   ========================= */

/* Each step: show the call, light its routes in order, change the state, then let the routes rest. */
async function playHeroDiagram() {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        HERO_STEPS.forEach(setHeroState);
        heroPlaying = false;
        return;
    }

    await heroWait(HERO_START_MS);
    for (const step of HERO_STEPS) {
        await setHeroCall(step.call);
        for (const index of step.routes) {
            setHeroRoute(index, true);
            await heroWait(HERO_DRAW_MS);
        }
        setHeroState(step);
        await heroWait(HERO_HOLD_MS);
        step.routes.forEach(index => setHeroRoute(index, false));
        await heroWait(HERO_GAP_MS);
    }
    heroPlaying = false;
}

/* Hovering a method lights every route that starts or ends at it. */
heroDiagram?.querySelectorAll("[data-method]").forEach(function(method) {
    const routes = HERO_ROUTES
        .map((route, index) => (route.from === method.dataset.method || route.to === method.dataset.method ? index : -1))
        .filter(index => index >= 0);
    method.addEventListener("pointerenter", () => !heroPlaying && routes.forEach(index => setHeroRoute(index, true)));
    method.addEventListener("pointerleave", () => !heroPlaying && routes.forEach(index => setHeroRoute(index, false)));
});

if (heroDiagram) {
    new ResizeObserver(drawHeroLines).observe(heroDiagram);
    document.fonts.ready.then(drawHeroLines);
    playHeroDiagram();
}
