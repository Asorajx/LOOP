/* =========================
   Method Interaction
   ========================= */

function setupMethodInteractions() {
    document.querySelectorAll(".method[data-source]").forEach(function(button) {
        createCodeDrawer(button);

        button.addEventListener("click", async function() {
            stopEventPlayback();
            await toggleCodeDrawer(button);
            await executeMethod(button);
        });
    });
}

/* =========================
   Playback Controls
   ========================= */

function setupPlaybackControls() {
    document.getElementById("playback-previous")?.addEventListener("click", previousPlayback);
    document.getElementById("playback-next")?.addEventListener("click", nextPlayback);
    document.getElementById("playback-play")?.addEventListener("click", playPlayback);
    document.getElementById("playback-pause")?.addEventListener("click", pausePlayback);
    document.getElementById("playback-replay")?.addEventListener("click", replayPlayback);
    document.getElementById("playback-reset")?.addEventListener("click", resetSimulation);
    updatePlaybackControls();
}

/* =========================
   Initialisation
   ========================= */

getSimulationState();
setupMethodInteractions();
setupPlaybackControls();
clearStateChanges();
window.addEventListener("load", redrawCircuitNetwork);
window.addEventListener("resize", redrawCircuitNetwork);