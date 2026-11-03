/* =========================
   Route Data
   ========================= */

/* The circuit network is drawn from routes found by running real Python. */
/* The server discovers routes on fresh objects, and each live run adds any new ones it finds. */
/* Those additions stay in this browser only. Nothing here is configured per scenario. */
let knownRoutes = [];
let currentRoute = null;

function setKnownRoutes(routes) {
    knownRoutes = routes.map(route => ({ from: route.from, to: route.to, kind: route.kind }));
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

/* A route runs out of the caller's panel, along a bus in the gap, into the callee's panel. */
/* Calls inside one panel loop out along a short spine beside that panel instead. */
/* All positions are measured from the page, so they must be recalculated whenever the layout moves. */
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

    if (fromPanel === toPanel) {
        /* super() calls sit further out than ordinary calls, so the two spines don't overlap. */
        const onLeft = fromPanel < panels.length - 1;
        const edge = (onLeft ? panelRects[fromPanel].left : panelRects[fromPanel].right) - spaceRect.left;
        const reach = route.kind === "super" ? 20 : 11;
        return { startX: edge, endX: edge, busX: edge + (onLeft ? -reach : reach), y1, y2, panel: fromPanel };
    }

    /* Calls in each direction use a bus slightly off-centre, so two-way gaps stay readable. */
    if (toPanel > fromPanel) {
        return {
            startX: panelRects[fromPanel].right - spaceRect.left,
            endX: panelRects[toPanel].left - spaceRect.left,
            busX: gapX(fromPanel) - 5,
            y1, y2, panel: fromPanel
        };
    }

    return {
        startX: panelRects[fromPanel].left - spaceRect.left,
        endX: panelRects[toPanel].right - spaceRect.left,
        busX: gapX(fromPanel - 1) + 5,
        y1, y2, panel: fromPanel
    };
}


/* =========================
   Drawing Circuits
   ========================= */

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

    /* Quiet network: one bus per side of each gap, with branches and junction nodes. */
    /* Branches shared by several routes are drawn only once. */
    const buses = {};
    const drawn = new Set();
    const branch = function(x1, x2, y, network) {
        const key = `${Math.round(x1)}:${Math.round(x2)}:${Math.round(y)}`;
        if (drawn.has(key)) return;
        drawn.add(key);
        svg.appendChild(svgElement("path", { d: `M ${x1} ${y} H ${x2}`, class: `circuit-line ${network}` }));
        svg.appendChild(svgElement("rect", { x: x2 - 2, y: y - 2, width: 4, height: 4, class: `circuit-node ${network}` }));
    };

    knownRoutes.forEach(function(known) {
        const geometry = routeGeometry(known, space, spaceRect);
        if (!geometry) return;
        const network = known.kind === "super" ? "net-super" : `net-${(geometry.panel % 3) + 1}`;

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

    /* The live call: a solid lit path with the travelling light from the original LOOP. */
    /* While it shows, the quiet network fades so the live route stands out. */
    const geometry = route?.from ? routeGeometry(route, space, spaceRect) : null;
    svg.classList.toggle("has-active", Boolean(geometry));
    if (!geometry) return;

    const network = route.kind === "super" ? "net-super" : `net-${(geometry.panel % 3) + 1}`;
    const pathData = `M ${geometry.startX} ${geometry.y1} H ${geometry.busX} V ${geometry.y2} H ${geometry.endX}`;
    svg.appendChild(svgElement("path", { d: pathData, class: `circuit-route ${network} route-${route.kind}` }));
    svg.appendChild(svgElement("path", { d: pathData, class: `circuit-active ${network} route-${route.kind}` }));
    [[geometry.busX, geometry.y1], [geometry.busX, geometry.y2]].forEach(function([x, y]) {
        svg.appendChild(svgElement("rect", { x: x - 3.5, y: y - 3.5, width: 7, height: 7, class: `circuit-node-active ${network}` }));
    });
}


/* =========================
   Event Listeners
   ========================= */

/* Circuit positions depend on where the method rows sit. */
/* Redraw when the panels change size (fonts loading, status rows, wrapping) or the window resizes. */
new ResizeObserver(() => drawRoutes()).observe(document.getElementById("actor-space"));
window.addEventListener("resize", () => drawRoutes());
