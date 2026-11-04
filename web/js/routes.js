/* =========================
   Route Data
   ========================= */

/* Routes from the server, plus any new ones found during live runs. */
let knownRoutes = [];
let currentRoute = null;

/* The hovered or focused def line, whose routes are previewed when not playing. */
let pointerMethod = null;
let focusMethod = null;
let previewAllowed = true;

function setKnownRoutes(routes) {
    knownRoutes = routes.map(route => ({ from: route.from, to: route.to, kind: route.kind }));
    /* Method ids can repeat across scenarios, so a preview never carries over. */
    pointerMethod = null;
    focusMethod = null;
}

/* Called by playback.js; turning previews off also clears the hovered method. */
function setPreviewAllowed(allowed) {
    if (allowed === previewAllowed) return;
    previewAllowed = allowed;
    if (!allowed) {
        window.clearTimeout(previewTimer);
        pointerMethod = null;
        focusMethod = null;
    }
    drawRoutes();
}

/* Add routes a live run used that the network didn't have yet. */
function addRoutesFromRun(run) {
    run.steps.forEach(function(step) {
        const route = step.route;
        if (route?.from && !knownRoutes.some(known => known.from === route.from && known.to === route.to)) {
            knownRoutes.push({ from: route.from, to: route.to, kind: route.kind });
        }
    });
}


/* =========================
   Circuit Geometry
   ========================= */

function svgElement(tag, attributes) {
    const element = document.createElementNS("http://www.w3.org/2000/svg", tag);
    Object.entries(attributes).forEach(([name, value]) => element.setAttribute(name, value));
    return element;
}

/* Find the method's def line, ignoring any copy that isn't currently displayed. */
function visibleMethod(space, methodId) {
    return Array.from(space.querySelectorAll(`.method[data-method="${CSS.escape(methodId)}"]`))
        .find(element => element.getClientRects().length > 0) || null;
}

/* Measure a route: caller's panel edge, bus in the gap, callee's panel edge. */
/* Calls within one panel use a short spine beside it. */
function routeGeometry(route, space, spaceRect) {
    const panels = Array.from(space.querySelectorAll(".space"));
    const from = visibleMethod(space, route.from);
    const to = visibleMethod(space, route.to);
    if (!from || !to) return null;

    const fromPanel = panels.indexOf(from.closest(".space"));
    const toPanel = panels.indexOf(to.closest(".space"));
    const panelRects = panels.map(panel => panel.getBoundingClientRect());
    const centreY = element => {
        const rect = element.getBoundingClientRect();
        return rect.top + rect.height / 2 - spaceRect.top;
    };
    const y1 = centreY(from);
    const y2 = centreY(to);
    const gapX = index => (panelRects[index].right + panelRects[index + 1].left) / 2 - spaceRect.left;
    /* Each relationship gets its own lane, so a dashed property route never lies on a call route. */
    const lane = { call: 0, property: 4, super: 9 }[route.kind] ?? 0;

    if (fromPanel === toPanel) {
        /* Same-panel spines step outwards by lane: calls nearest, then properties, then super(). */
        const onLeft = fromPanel < panels.length - 1;
        const edge = (onLeft ? panelRects[fromPanel].left : panelRects[fromPanel].right) - spaceRect.left;
        const reach = 11 + lane;
        return { startX: edge, endX: edge, busX: edge + (onLeft ? -reach : reach), y1, y2, panel: fromPanel };
    }

    /* Calls in each direction use a bus slightly off-centre, so two-way gaps stay readable. */
    if (toPanel > fromPanel) {
        return {
            startX: panelRects[fromPanel].right - spaceRect.left,
            endX: panelRects[toPanel].left - spaceRect.left,
            busX: gapX(fromPanel) - 5 - lane,
            y1, y2, panel: fromPanel
        };
    }

    return {
        startX: panelRects[fromPanel].left - spaceRect.left,
        endX: panelRects[toPanel].right - spaceRect.left,
        busX: gapX(fromPanel - 1) + 5 + lane,
        y1, y2, panel: fromPanel
    };
}


/* =========================
   Drawing Circuits
   ========================= */

function routeNetwork(route) {
    if (route.kind === "super") return "net-super";
    if (route.kind === "property") return "net-property";
    return "net-call";
}

function routePath(geometry) {
    return `M ${geometry.startX} ${geometry.y1} H ${geometry.busX} V ${geometry.y2} H ${geometry.endX}`;
}

/* Draw the faint network, then either the hover preview or the current step's route. */
function drawRoutes(route = currentRoute) {
    currentRoute = route;
    const space = document.getElementById("actor-space");
    const svg = document.getElementById("circuit-layer");
    if (!space || !svg) return;

    /* Panels stack on narrow screens, where circuits can't run between them. */
    svg.innerHTML = "";
    if (window.innerWidth <= 900) return;

    const spaceRect = space.getBoundingClientRect();
    svg.setAttribute("viewBox", `0 0 ${spaceRect.width} ${spaceRect.height}`);

    /* Faint network: one bus per gap and relationship type. */
    const buses = {};
    const drawn = new Set();
    const branch = function(x1, x2, y, network) {
        const key = `${Math.round(x1)}:${Math.round(x2)}:${Math.round(y)}:${network}`;
        if (drawn.has(key)) return;
        drawn.add(key);
        svg.appendChild(svgElement("path", { d: `M ${x1} ${y} H ${x2}`, class: `circuit-line ${network}` }));
    };

    knownRoutes.forEach(function(known) {
        const geometry = routeGeometry(known, space, spaceRect);
        if (!geometry) return;
        const network = routeNetwork(known);

        const bus = buses[`${Math.round(geometry.busX)}:${network}`] ||= { x: geometry.busX, network, top: Infinity, bottom: -Infinity };
        bus.top = Math.min(bus.top, geometry.y1, geometry.y2);
        bus.bottom = Math.max(bus.bottom, geometry.y1, geometry.y2);

        branch(geometry.startX, geometry.busX, geometry.y1, network);
        branch(geometry.endX, geometry.busX, geometry.y2, network);
    });

    Object.values(buses).forEach(function(bus) {
        svg.appendChild(svgElement("path", {
            d: `M ${bus.x} ${bus.top} V ${bus.bottom}`,
            class: `circuit-line circuit-bus ${bus.network}`
        }));
    });

    if (drawPreview(space, svg, spaceRect)) return;

    /* Current step: same as a preview, plus the travelling light. */
    const geometry = route?.from ? routeGeometry(route, space, spaceRect) : null;
    svg.classList.toggle("has-active", Boolean(geometry));
    if (!geometry) return;

    const network = routeNetwork(route);
    const pathData = routePath(geometry);
    drawStaticCircuit(svg, pathData, network, route.kind);
    svg.appendChild(svgElement("path", { d: pathData, class: `circuit-active ${network} route-${route.kind}` }));
}

/* Glow and solid route, shared by previews and the current step. */
function drawStaticCircuit(svg, pathData, network, kind) {
    svg.appendChild(svgElement("path", { d: pathData, class: `circuit-glow ${network} route-${kind}` }));
    svg.appendChild(svgElement("path", { d: pathData, class: `circuit-route ${network} route-${kind}` }));
}

/* Draw every route into or out of the hovered method. Returns false when there is none. */
function drawPreview(space, svg, spaceRect) {
    const methodId = previewAllowed ? pointerMethod || focusMethod : null;
    const connected = methodId ? knownRoutes.filter(route => route.from === methodId || route.to === methodId) : [];
    const paths = connected
        .map(route => ({ route, geometry: routeGeometry(route, space, spaceRect) }))
        .filter(item => item.geometry);

    svg.classList.toggle("has-preview", paths.length > 0);
    if (!paths.length) return false;
    svg.classList.remove("has-active");

    paths.forEach(function({ route, geometry }) {
        const network = routeNetwork(route);
        drawStaticCircuit(svg, routePath(geometry), network, route.kind);
    });
    return true;
}


/* =========================
   Event Listeners
   ========================= */

/* Redraw when the panels or window change size. */
new ResizeObserver(() => drawRoutes()).observe(document.getElementById("actor-space"));
window.addEventListener("resize", () => drawRoutes());

/* Hover previews after a short delay; focus previews at once; touch is ignored. */
const PREVIEW_DELAY = 100;
let previewTimer = null;
const methodRowAt = target => (target instanceof Element ? target.closest(".def-line[data-method]") : null);
const actorSpace = document.getElementById("actor-space");

actorSpace.addEventListener("pointerover", function(event) {
    const row = methodRowAt(event.target);
    if (event.pointerType === "touch" || !previewAllowed || !row || row.contains(event.relatedTarget)) return;
    window.clearTimeout(previewTimer);
    previewTimer = window.setTimeout(function() {
        pointerMethod = row.dataset.method;
        drawRoutes();
    }, PREVIEW_DELAY);
});

actorSpace.addEventListener("pointerout", function(event) {
    const row = methodRowAt(event.target);
    if (event.pointerType === "touch" || !row || row.contains(event.relatedTarget)) return;
    window.clearTimeout(previewTimer);
    if (pointerMethod) {
        pointerMethod = null;
        drawRoutes();
    }
});

actorSpace.addEventListener("focusin", function(event) {
    const row = methodRowAt(event.target);
    if (!row || !previewAllowed) return;
    focusMethod = row.dataset.method;
    drawRoutes();
});

actorSpace.addEventListener("focusout", function(event) {
    const row = methodRowAt(event.target);
    if (!row || !focusMethod) return;
    focusMethod = null;
    drawRoutes();
});
