from attacks import (
    CredentialAttack,
    MitMAttack,
    DoSAttack,
    DDoSAttack,
    MalwareAttack,
    RansomwareAttack
)

from actors import Attacker, Defender
from network import NetworkDevice, Connection
from simulation import CyberDefenseSimulation


def main():
    device1 = NetworkDevice("DEV001", "Web Server")
    device2 = NetworkDevice("DEV002", "Database Server")

    connection = Connection("CON001", device1, device2)

    credential = CredentialAttack()
    mitm = MitMAttack()
    dos = DoSAttack()
    ddos = DDoSAttack()
    malware = MalwareAttack()
    ransomware = RansomwareAttack()

    attacker = Attacker(
        "Attacker 1",
        [
            credential,
            mitm,
            dos,
            ddos,
            malware,
            ransomware
        ]
    )

    defender = Defender("Defender 1")

    simulation = CyberDefenseSimulation(
        attacker,
        defender,
        [device1, device2],
        [connection]
    )


    # =========================
    # Credential Attack
    # =========================

    simulation.reset()

    print("CREDENTIAL ATTACK")
    simulation.perform_attack(credential, device1)

    print(device1)
    print()
    print(simulation.tracer)


    # =========================
    # DoS Attack
    # =========================

    simulation.reset()

    print("DOS ATTACK")
    simulation.perform_attack(dos, device1)

    print(device1)
    print("Traffic Level:", device1.traffic_level)
    print()
    print(simulation.tracer)


    # =========================
    # DDoS Attack
    # =========================

    simulation.reset()

    print("DDOS ATTACK")
    simulation.perform_attack(ddos, device1)

    print(device1)
    print("Traffic Level:", device1.traffic_level)
    print()
    print(simulation.tracer)


    # =========================
    # Malware Attack
    # =========================

    simulation.reset()

    print("MALWARE ATTACK")
    simulation.perform_attack(malware, device1)

    print(device1)
    print()
    print(simulation.tracer)


    # =========================
    # Ransomware Attack
    # =========================

    simulation.reset()

    print("RANSOMWARE ATTACK")
    simulation.perform_attack(ransomware, device1)

    print(device1)
    print("Files Locked:", device1.files_locked)
    print()
    print(simulation.tracer)


    # =========================
    # MITM Attack
    # =========================

    simulation.reset()

    print("MITM ATTACK")
    simulation.perform_attack(mitm, connection)

    print(connection)
    print(device1)
    print(device2)
    print()
    print(simulation.tracer)


    # =========================
    # Secure Connection
    # =========================

    print("SECURE CONNECTION")
    simulation.secure_connection(connection)

    print(connection)
    print()
    print(simulation.tracer)


    # =========================
    # Block Attack
    # =========================

    simulation.reset()

    print("BLOCK ATTACK")
    simulation.block(device1)

    result = simulation.perform_attack(malware, device1)

    print("Attack successful:", result)
    print("Blocked:", device1.blocked)
    print(device1)
    print()
    print(simulation.tracer)


    # =========================
    # Unblock Attack
    # =========================

    print("UNBLOCK ATTACK")
    simulation.unblock(device1)

    result = simulation.perform_attack(malware, device1)

    print("Attack successful:", result)
    print("Blocked:", device1.blocked)
    print(device1)
    print()
    print(simulation.tracer)


    # =========================
    # Isolate Device
    # =========================

    simulation.reset()

    print("ISOLATE DEVICE")

    simulation.perform_attack(malware, device1)
    simulation.isolate(device1)

    print("Risk Level:", device1.risk_level)
    print("Isolated:", device1.isolated)
    print("Blocked:", device1.blocked)
    print()
    print(simulation.tracer)


    # =========================
    # Attack Isolated Device
    # =========================

    print("ATTACK ISOLATED DEVICE")

    result = simulation.perform_attack(credential, device1)

    print("Attack successful:", result)
    print("Risk Level:", device1.risk_level)
    print()
    print(simulation.tracer)


    # =========================
    # Restore Device
    # =========================

    print("RESTORE DEVICE")
    simulation.restore(device1)

    print("Risk Level:", device1.risk_level)
    print("Compromised:", device1.compromised)
    print("Traffic Level:", device1.traffic_level)
    print("Files Locked:", device1.files_locked)
    print("Isolated:", device1.isolated)
    print("Blocked:", device1.blocked)
    print()
    print(simulation.tracer)


    # =========================
    # Inspect Device
    # =========================

    simulation.reset()

    print("INSPECT DEVICE")

    simulation.perform_attack(credential, device1)

    result = simulation.inspect(device1)

    print(result)
    print()
    print(simulation.tracer)


if __name__ == "__main__":
    main()