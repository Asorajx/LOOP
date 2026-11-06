/* =========================
   Scroll Reveal
   ========================= */

/* Sections below the fold fade in and rise a little, once, as they scroll into view. */
/* Nothing is hidden unless this script runs, so the page stays readable without it. */
(function() {
    if (!("IntersectionObserver" in window)) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const DURATION = 500;
    const STAGGER = 70;

    /* Elements already on screen are left alone, so nothing flashes at load. */
    function belowFold(element) {
        return element.getBoundingClientRect().top > window.innerHeight;
    }

    /* Once revealed, the classes are removed so the element ends exactly as it was styled. */
    function finish(element) {
        element.classList.remove("reveal", "is-revealed");
        element.style.removeProperty("--reveal-delay");
    }

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (!entry.isIntersecting) return;
            const element = entry.target;
            observer.unobserve(element);
            element.classList.add("is-revealed");
            const delay = parseInt(element.style.getPropertyValue("--reveal-delay"), 10) || 0;
            window.setTimeout(() => finish(element), delay + DURATION + 150);
        });
    }, { rootMargin: "0px 0px -6% 0px" });

    function watch(element, delay) {
        if (!element || !belowFold(element)) return;
        element.style.setProperty("--reveal-delay", `${delay}ms`);
        element.classList.add("reveal");
        observer.observe(element);
    }

    /* The heading, then the concepts in a short stagger across each row. */
    watch(document.querySelector(".fundamentals h2"), 0);
    const grid = document.getElementById("concept-grid");
    const columns = grid ? getComputedStyle(grid).gridTemplateColumns.split(" ").length : 1;
    document.querySelectorAll(".concept-card").forEach(function(card, index) {
        watch(card, (index % columns) * STAGGER);
    });

    /* The Playground's toolbar, Terminal and code panels, each as it arrives. */
    /* The tab strip, the Playground itself and the compact Terminal are not moved: their layout depends on staying put. */
    watch(document.querySelector(".controls"), 0);
    watch(document.querySelector(".terminal"), 0);
    watch(document.getElementById("actor-space"), 0);
})();
