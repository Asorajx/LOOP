/* =========================
   Shared State
   ========================= */

let simulationState = {
    devices: [],
    connections: []
};

let activeCircuit = null;
let playbackToken = 0;

const PLAYBACK_DELAY = 1000;

function wait(milliseconds) {
    return new Promise(resolve => window.setTimeout(resolve, milliseconds));
}

/* =========================
   Circuit Configuration
   ========================= */

const circuitNetworks = {
    attack: {
        sourcePanel: ".attacker",
        targetPanel: ".victim",
        direction: "left",
        actions: {
            "credential-execute": ["device-increase-risk"],
            "mitm-execute": ["connection-intercept"],
            "dos-execute": ["device-increase-risk", "device-overload"],
            "ddos-execute": ["device-increase-risk", "device-overload"],
            "malware-execute": ["device-increase-risk"],
            "ransomware-execute": ["device-increase-risk", "device-lock-files"]
        }
    },
    defender: {
        sourcePanel: ".defender",
        targetPanel: ".victim",
        direction: "right",
        actions: {
            "defender-inspect": ["network-device"],
            "defender-block": ["device-block"],
            "defender-unblock": ["device-unblock"],
            "defender-isolate": ["device-isolate"],
            "defender-restore": ["device-restore"],
            "defender-secure": ["connection-secure"]
        }
    }
};

/* =========================
   Event Configuration
   ========================= */

const stateLinePatterns = {
    "device-increase-risk": {
        risk_level: "self.__risk_level += amount"
    },
    "device-overload": {
        traffic_level: "self.__traffic_level = traffic_level"
    },
    "device-isolate": {
        isolated: "self.__isolated = True",
        blocked: "self.__blocked = True"
    },
    "device-block": {
        blocked: "self.__blocked = True"
    },
    "device-unblock": {
        blocked: "self.__blocked = False"
    },
    "device-lock-files": {
        files_locked: "self.__files_locked = True"
    },
    "device-restore": {
        risk_level: "self.__risk_level = 0",
        traffic_level: "self.__traffic_level = \"NORMAL\"",
        isolated: "self.__isolated = False",
        files_locked: "self.__files_locked = False"
    },
    "connection-intercept": {
        intercepted: "self.__intercepted = True"
    },
    "connection-secure": {
        intercepted: "self.__intercepted = False"
    },
    "connection-block": {
        blocked: "self.__blocked = True"
    },
    "connection-unblock": {
        blocked: "self.__blocked = False"
    }
};

const parentCallPatterns = {
    "attacker-perform": {
        "credential-execute": ["attack.execute(target)"],
        "mitm-execute": ["attack.execute(target)"],
        "dos-execute": ["attack.execute(target)"],
        "ddos-execute": ["attack.execute(target)"],
        "malware-execute": ["attack.execute(target)"],
        "ransomware-execute": ["attack.execute(target)"]
    },
    "credential-execute": {
        "device-increase-risk": ["target.increase_risk(1)"]
    },
    "mitm-execute": {
        "connection-intercept": ["target.intercept()"]
    },
    "dos-execute": {
        "device-increase-risk": ["target.increase_risk(1)"],
        "device-overload": ["target.overload(\"HIGH\")"]
    },
    "ddos-execute": {
        "dos-execute": ["super().execute(target)"],
        "device-increase-risk": ["target.increase_risk(1)"],
        "device-overload": ["target.overload(\"CRITICAL\")"]
    },
    "malware-execute": {
        "device-increase-risk": ["target.increase_risk(2)"]
    },
    "ransomware-execute": {
        "malware-execute": ["super().execute(target)"],
        "device-increase-risk": ["target.increase_risk(1)"],
        "device-lock-files": ["target.lock_files()"]
    },
    "connection-intercept": {
        "device-increase-risk": [
            "self.__device1.increase_risk(1)",
            "self.__device2.increase_risk(1)"
        ]
    },
    "defender-block": {
        "device-block": ["target.block()"]
    },
    "defender-unblock": {
        "device-unblock": ["target.unblock()"]
    },
    "defender-isolate": {
        "device-isolate": ["target.isolate()"]
    },
    "defender-restore": {
        "device-restore": ["target.restore()"]
    },
    "defender-secure": {
        "connection-secure": ["connection.secure()"]
    }
};

/* =========================
   Terminal Explanations
   ========================= */

const terminalExplanations = {
    "attacker-perform": {
        code: "Finds the target ID, checks whether the target is blocked, then calls execute() on the selected attack object.",
        description: "Coordinates an attack against a simulated device or connection and stops the attack if the target is blocked.",
        oopConcepts: "Composition · Polymorphism · Object Interaction"
    },
    "credential-execute": {
        code: "Calls increase_risk(1) on the target device instead of changing the device's private risk value directly.",
        description: "Simulates a credential attack making the target device more at risk.",
        oopConcepts: "Polymorphism · Encapsulation · Object Interaction"
    },
    "mitm-execute": {
        code: "Calls intercept() on the target Connection object. The Connection then handles its own state and connected devices.",
        description: "Simulates a man-in-the-middle attack intercepting communication between two devices.",
        oopConcepts: "Composition · Object Interaction · Polymorphism"
    },
    "dos-execute": {
        code: 'Calls increase_risk(1), then calls overload("HIGH") on the target device.',
        description: "Simulates a denial-of-service attack causing unusually high traffic on a device.",
        oopConcepts: "Abstraction · Polymorphism · Encapsulation"
    },
    "ddos-execute": {
        code: "Uses super().execute(target) to run the parent DoSAttack first, then adds another risk increase and changes traffic to CRITICAL.",
        description: "Simulates a stronger distributed denial-of-service attack by building on the normal DoS behaviour.",
        oopConcepts: "Inheritance · Method Overriding · super()"
    },
    "malware-execute": {
        code: "Calls increase_risk(2) on the target device through the device's public method.",
        description: "Simulates malware increasing the risk level of a device.",
        oopConcepts: "Polymorphism · Encapsulation · Object Interaction"
    },
    "ransomware-execute": {
        code: "Uses super() to run MalwareAttack first, then increases risk again and calls lock_files() on the device.",
        description: "Simulates ransomware building on malware behaviour and then locking the device's files.",
        oopConcepts: "Inheritance · Method Extension · super()"
    },
    "device-increase-risk": {
        code: "Saves the old risk level, adds the requested amount, limits the maximum to 3, then records the state change.",
        description: "Updates how at-risk or compromised the simulated device is.",
        oopConcepts: "Encapsulation · Object State"
    },
    "device-overload": {
        code: "Saves the old traffic level, replaces it with the new value, then records the state change.",
        description: "Updates the simulated traffic condition of the device, such as NORMAL, HIGH or CRITICAL.",
        oopConcepts: "Encapsulation · Object State"
    },
    "device-isolate": {
        code: "Sets isolated and blocked to True, then records both state changes.",
        description: "Marks the simulated device as isolated and blocked so it is separated from further activity.",
        oopConcepts: "Encapsulation · Multiple State Changes"
    },
    "device-block": {
        code: "Saves the old blocked value, changes blocked to True, then records the state change.",
        description: "Marks the device as blocked so attacks cannot continue against it.",
        oopConcepts: "Encapsulation · Object State"
    },
    "device-unblock": {
        code: "Saves the old blocked value, changes blocked to False, then records the state change.",
        description: "Removes the simulated block so the device can receive interactions again.",
        oopConcepts: "Encapsulation · Object State"
    },
    "device-lock-files": {
        code: "Saves the old files_locked value, changes it to True, then records the state change.",
        description: "Marks the simulated device's files as locked during the ransomware demonstration.",
        oopConcepts: "Encapsulation · Object State"
    },
    "device-restore": {
        code: "Resets changed device values such as risk, traffic, isolation and file locking back to their normal values.",
        description: "Restores the simulated device after an attack or defensive action.",
        oopConcepts: "Encapsulation · Object State Restoration"
    },
    "connection-intercept": {
        code: "Changes intercepted to True, then calls increase_risk(1) on both devices connected to this Connection.",
        description: "Simulates communication being intercepted between two connected devices.",
        oopConcepts: "Composition · Object Interaction · Encapsulation"
    },
    "connection-secure": {
        code: "Saves the old intercepted value, changes intercepted to False, then records the state change.",
        description: "Marks a previously intercepted simulated connection as secure again.",
        oopConcepts: "Encapsulation · Object State Restoration"
    },
    "connection-block": {
        code: "Saves the old blocked value, changes blocked to True, then records the state change.",
        description: "Blocks simulated activity across the connection.",
        oopConcepts: "Encapsulation · Object State"
    },
    "connection-unblock": {
        code: "Saves the old blocked value, changes blocked to False, then records the state change.",
        description: "Reopens the simulated connection for activity.",
        oopConcepts: "Encapsulation · Object State"
    },
    "defender-inspect": {
        code: "Calls str(target) and returns the target's readable string representation.",
        description: "Lets the defender inspect the current simulated condition of a device.",
        oopConcepts: "Object Interaction · Public Interface"
    },
    "defender-block": {
        code: "Calls block() on the target device instead of changing the device's private blocked value directly.",
        description: "Tells the target device to block further simulated attacks.",
        oopConcepts: "Encapsulation · Delegation · Object Interaction"
    },
    "defender-unblock": {
        code: "Calls unblock() on the target device so the device changes its own blocked state.",
        description: "Removes the simulated block from a device.",
        oopConcepts: "Encapsulation · Delegation · Object Interaction"
    },
    "defender-isolate": {
        code: "Calls isolate() on the target device so the device updates its own isolated and blocked values.",
        description: "Quarantines a simulated device after suspicious or harmful activity.",
        oopConcepts: "Encapsulation · Delegation · Object Interaction"
    },
    "defender-restore": {
        code: "Calls restore() on the target device so the device resets its own internal state.",
        description: "Recovers the simulated device after an attack.",
        oopConcepts: "Encapsulation · Delegation · Object Interaction"
    },
    "defender-secure": {
        code: "Calls secure() on the Connection so the Connection changes its own intercepted state.",
        description: "Secures a simulated connection that may have been intercepted.",
        oopConcepts: "Composition · Encapsulation · Delegation"
    }
};
