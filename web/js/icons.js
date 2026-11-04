/* =========================
   Icons
   ========================= */

/* Small line icons for status indicators and links, drawn on a 24×24 grid in the current text colour. */
/* Scenarios refer to them by name in their STATUS settings. */
const ICONS = {
    arrowDown: ["M12 5v14", "M6 13l6 6 6-6"],
    external: ["M7 17L17 7", "M8 7h9v9"],
    bug: [
        "M9 7a3 3 0 0 1 6 0",
        "M8 11a4 4 0 0 1 8 0v4a4 4 0 0 1-8 0z",
        "M12 11v8",
        "M4 12h4", "M16 12h4", "M5 18l3-2", "M19 18l-3-2", "M5 7l3 2", "M19 7l-3 2"
    ],
    lock: [
        "M6 11h12a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1v-8a1 1 0 0 1 1-1z",
        "M8 11V7a4 4 0 0 1 8 0v4"
    ],
    offline: [
        "M3 3l18 18",
        "M5 12.5a10 10 0 0 1 5-2.6",
        "M19 12.5a10 10 0 0 0-2.3-1.6",
        "M8.5 16a5 5 0 0 1 7 0",
        "M12 20h.01"
    ],
    eye: [
        "M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z",
        "M12 9a3 3 0 1 1 0 6 3 3 0 0 1 0-6z"
    ],
    book: [
        "M5 4.5A1.5 1.5 0 0 1 6.5 3H19v15H6.5A1.5 1.5 0 0 0 5 19.5z",
        "M5 19.5A1.5 1.5 0 0 0 6.5 21H19v-3"
    ],
    power: [
        "M12 3v8",
        "M6.4 7.2a7 7 0 1 0 11.2 0"
    ]
};

/* Icons are inline SVG, so they need no image files or icon library. */
function createIcon(name) {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("aria-hidden", "true");
    svg.setAttribute("class", "icon");
    (ICONS[name] || []).forEach(function(data) {
        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        path.setAttribute("d", data);
        svg.appendChild(path);
    });
    return svg;
}
