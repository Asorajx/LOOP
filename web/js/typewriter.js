/* =========================
   Hero Typewriter
   ========================= */

const typewriterHeading = document.querySelector('[data-typewriter="heading"]');
const typewriterDescription = document.querySelector('[data-typewriter="description"]');
const typewriterReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

const TYPEWRITER_HEADING_SPEED_MS = 40;
const TYPEWRITER_DESCRIPTION_SPEED_MS = 10;
const TYPEWRITER_PAUSE_MS = 250;

/* Keep the full text accessible and its layout space reserved. */
function prepareTypewriter(element) {
    const fullText = element.textContent.trim();

    const accessibleText = document.createElement("span");
    accessibleText.className = "visually-hidden";
    accessibleText.textContent = fullText;

    const reserve = document.createElement("span");
    reserve.className = "hero-typewriter-reserve";
    reserve.textContent = fullText;
    reserve.setAttribute("aria-hidden", "true");

    const overlay = document.createElement("span");
    overlay.className = "hero-typewriter-overlay";
    overlay.setAttribute("aria-hidden", "true");

    const visibleText = document.createElement("span");
    visibleText.className = "hero-typewriter-text";
    overlay.appendChild(visibleText);

    element.replaceChildren(accessibleText, reserve, overlay);
    element.classList.add("hero-typewriter");

    return { element, fullText, visibleText };
}

/* Type one character at a time, then remove the caret. */
function typeHeroLine(line, speed) {
    return new Promise(function(resolve) {
        let index = 0;
        line.element.classList.add("is-typing");

        function typeNextCharacter() {
            if (typewriterReducedMotion.matches) {
                line.visibleText.textContent = line.fullText;
                line.element.classList.remove("is-typing");
                resolve();
                return;
            }

            index++;
            line.visibleText.textContent = line.fullText.slice(0, index);

            if (index < line.fullText.length) {
                window.setTimeout(typeNextCharacter, speed);
            } else {
                line.element.classList.remove("is-typing");
                resolve();
            }
        }

        typeNextCharacter();
    });
}

/* Play once: heading, brief pause, then the faster description. */
async function startHeroTypewriter() {
    if (!typewriterHeading || !typewriterDescription || typewriterReducedMotion.matches) {
        document.documentElement.classList.remove("typewriter-pending");
        return;
    }

    const heading = prepareTypewriter(typewriterHeading);
    const description = prepareTypewriter(typewriterDescription);
    document.documentElement.classList.remove("typewriter-pending");

    await typeHeroLine(heading, TYPEWRITER_HEADING_SPEED_MS);
    await new Promise(resolve => window.setTimeout(resolve, TYPEWRITER_PAUSE_MS));
    await typeHeroLine(description, TYPEWRITER_DESCRIPTION_SPEED_MS);
}

startHeroTypewriter();
