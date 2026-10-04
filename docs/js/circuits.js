/* ========================= Circuit Helpers ========================= */

function createCircuitPath(svg, pathData, className) {
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", pathData);
    path.setAttribute("class", className);
    svg.appendChild(path);
}

function addCircuitNode(svg, x, y, type) {
    const node = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    node.setAttribute("x", x - 2);
    node.setAttribute("y", y - 2);
    node.setAttribute("width", 4);
    node.setAttribute("height", 4);
    node.setAttribute("class", `circuit-node ${type}-node`);
    svg.appendChild(node);
}

function getAnchorElement(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return null;
    return element.classList.contains("class-card")
        ? element.querySelector(".class-header") || element
        : element;
}

function getCenterY(element, spaceRect) {
    const rect = element.getBoundingClientRect();
    return rect.top + rect.height / 2 - spaceRect.top;
}

function getBusX(network, spaceRect) {
    const sourceRect = document.querySelector(network.sourcePanel)?.getBoundingClientRect();
    const targetRect = document.querySelector(network.targetPanel)?.getBoundingClientRect();
    if (!sourceRect || !targetRect) return null;

    const sourceEdge = network.direction === "left"
        ? sourceRect.right - spaceRect.left
        : sourceRect.left - spaceRect.left;
    const targetEdge = network.direction === "left"
        ? targetRect.left - spaceRect.left
        : targetRect.right - spaceRect.left;

    return sourceEdge + (targetEdge - sourceEdge) / 2;
}

/* ========================= Static Circuit Network ========================= */

function drawCircuitLines() {
    const space = document.getElementById("cyber-space");
    const svg = document.getElementById("circuit-layer");
    if (!space || !svg) return;

    if (window.innerWidth <= 900) {
        svg.innerHTML = "";
        return;
    }

    svg.innerHTML = "";
    const spaceRect = space.getBoundingClientRect();
    svg.setAttribute("viewBox", `0 0 ${spaceRect.width} ${spaceRect.height}`);
    svg.setAttribute("preserveAspectRatio", "none");

    Object.entries(circuitNetworks).forEach(([type, network]) => {
        drawNetwork(type, network, spaceRect, svg);
    });
}

function drawNetwork(type, network, spaceRect, svg) {
    const busX = getBusX(network, spaceRect);
    if (busX === null) return;

    const sourceIds = Object.keys(network.actions);
    const targetIds = [...new Set(Object.values(network.actions).flat())];
    const yPositions = sourceIds.concat(targetIds)
        .map(function(id) {
            const element = getAnchorElement(id);
            return element ? getCenterY(element, spaceRect) : null;
        })
        .filter(y => y !== null);

    if (!yPositions.length) return;

    createCircuitPath(
        svg,
        `M ${busX} ${Math.min(...yPositions)} V ${Math.max(...yPositions)}`,
        `circuit-line ${type}-line circuit-bus`
    );

    sourceIds.forEach(id => drawBranch(id, type, true, network, busX, spaceRect, svg));
    targetIds.forEach(id => drawBranch(id, type, false, network, busX, spaceRect, svg));
}

function drawBranch(id, type, isSource, network, busX, spaceRect, svg) {
    const element = getAnchorElement(id);
    if (!element) return;

    const rect = element.getBoundingClientRect();
    const y = getCenterY(element, spaceRect);
    const useRightEdge = network.direction === "left" ? isSource : !isSource;
    const x = (useRightEdge ? rect.right : rect.left) - spaceRect.left;

    createCircuitPath(svg, `M ${x} ${y} H ${busX}`, `circuit-line ${type}-line`);
    addCircuitNode(svg, busX, y, type);
}

/* =========================
   Active Circuit Interaction
   ========================= */

function getInstanceChip(objectId) {
    if (!objectId) return null;

    return Array.from(document.querySelectorAll(".instance-chip"))
        .find(chip => chip.dataset.objectId === String(objectId)) || null;
}

function clearInstanceHighlights() {
    document
        .querySelectorAll(
            ".instance-chip.active-instance, " +
            ".instance-chip.target-instance, " +
            ".instance-chip.under-attack, " +
            ".instance-chip.under-defense"
        )
        .forEach(function(chip) {
            chip.classList.remove(
                "active-instance",
                "target-instance",
                "under-attack",
                "under-defense"
            );
        });
}

function getInteractionType() {
    const rootSourceId = currentRootButton?.id;
    if (!rootSourceId) return null;

    if (rootSourceId === "attacker-perform") return "attack";
    if (rootSourceId.startsWith("defender-")) return "defender";

    return findCircuitType(rootSourceId) || null;
}

function getInteractionTargetId() {
    const rootEvent = executionEvents.find(function(event) {
        return event.event_type === "METHOD_STARTED" && event.target_id;
    });

    return rootEvent?.target_id || null;
}

function highlightEventInstances(event) {
    clearInstanceHighlights();
    if (!event) return;

    const activeInstance = getInstanceChip(event.object_id);
    const directTarget = getInstanceChip(event.target_id);
    const interactionTarget = getInstanceChip(getInteractionTargetId());
    const interactionType = getInteractionType();

    activeInstance?.classList.add("active-instance");

    if (directTarget && directTarget !== activeInstance) {
        directTarget.classList.add("target-instance");
    }

    if (interactionTarget && interactionType === "attack") {
        interactionTarget.classList.add("under-attack");
    }

    if (interactionTarget && interactionType === "defender") {
        interactionTarget.classList.add("under-defense");
    }
}

function clearActiveVisuals() {
    document.querySelectorAll(".circuit-active").forEach(path => path.remove());
    document
        .querySelectorAll(".method.active, .method.active-source, .under-attack, .under-defense")
        .forEach(function(element) {
            element.classList.remove("active", "active-source", "under-attack", "under-defense");
        });
    clearInstanceHighlights();
    activeCircuit = null;
}

function animateRoute(type, network, sourceId, targetId) {
    const space = document.getElementById("cyber-space");
    const svg = document.getElementById("circuit-layer");
    const source = getAnchorElement(sourceId);
    const target = getAnchorElement(targetId);
    if (!space || !svg || !source || !target) return;

    const spaceRect = space.getBoundingClientRect();
    const sourceRect = source.getBoundingClientRect();
    const targetRect = target.getBoundingClientRect();
    const busX = getBusX(network, spaceRect);
    if (busX === null) return;

    const startX = (network.direction === "left" ? sourceRect.right : sourceRect.left) - spaceRect.left;
    const endX = (network.direction === "left" ? targetRect.left : targetRect.right) - spaceRect.left;
    const pathData = `M ${startX} ${getCenterY(source, spaceRect)} H ${busX} V ${getCenterY(target, spaceRect)} H ${endX}`;
    createCircuitPath(svg, pathData, `circuit-active ${type}-active`);
}

function activateTarget(type, sourceId, targetId) {
    const network = circuitNetworks[type];
    if (!network?.actions[sourceId]?.includes(targetId)) return;

    document.querySelectorAll(".circuit-active").forEach(path => path.remove());

    const target = getAnchorElement(targetId);
    if (target?.classList.contains("method")) {
        target.classList.add("active");
    }

    activeCircuit = { type, sourceId, targetId };
    animateRoute(type, network, sourceId, targetId);
}

function redrawCircuitNetwork() {
    drawCircuitLines();

    if (activeCircuit) {
        const network = circuitNetworks[activeCircuit.type];
        animateRoute(
            activeCircuit.type,
            network,
            activeCircuit.sourceId,
            activeCircuit.targetId
        );
    }
}

function findCircuitType(methodId) {
    return Object.keys(circuitNetworks).find(type => circuitNetworks[type].actions[methodId]);
}
