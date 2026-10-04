/* =========================
   Method Interaction
   ========================= */

function setupMethodInteractions() {
    document.querySelectorAll(".method[data-source]").forEach(function(button) {
        createCodeDrawer(button);

        button.addEventListener("click", async function() {
            if (currentMode === simulationModes.GUIDED) {
                if (isPlaying || isProcessingEvent || isResetting) return;

                await toggleCodeDrawer(button);
                setSystemStatus("Guided Mode");
                return;
            }

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
   Mode Controls
   ========================= */

function setupModeControls() {
    document.getElementById("mode-manual")?.addEventListener("click", function() {
        setSimulationMode(simulationModes.MANUAL);
    });

    document.getElementById("mode-guided")?.addEventListener("click", function() {
        setSimulationMode(simulationModes.GUIDED);
    });

    updateModeControls();
    updateGuidedSceneDisplay();
}


/* =========================
   Initialisation
   ========================= */

getSimulationState();
setupMethodInteractions();
setupPlaybackControls();
setupModeControls();
clearStateChanges();
window.addEventListener("load", redrawCircuitNetwork);
window.addEventListener("resize", redrawCircuitNetwork);