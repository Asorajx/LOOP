class NetworkDevice:
    def __init__(self, device_id, name):
        self.__device_id = device_id
        self.__name = name
        self.__risk_level = 0
        self.__traffic_level = "NORMAL"
        self.__isolated = False
        self.__files_locked = False
        self.__blocked = False
        self.__tracer = None

    @property
    def device_id(self):
        return self.__device_id

    @property
    def name(self):
        return self.__name

    @property
    def risk_level(self):
        return self.__risk_level

    @property
    def compromised(self):
        return self.__risk_level >= 3

    @property
    def traffic_level(self):
        return self.__traffic_level

    @property
    def isolated(self):
        return self.__isolated

    @property
    def files_locked(self):
        return self.__files_locked

    @property
    def blocked(self):
        return self.__blocked

    def set_tracer(self, tracer):
        self.__tracer = tracer

    def increase_risk(self, amount=1):
        if self.__tracer is not None:
            self.__tracer.method_started(
                self.__device_id,
                "NetworkDevice",
                "increase_risk"
            )

        previous_value = self.__risk_level

        self.__risk_level += amount

        if self.__risk_level > 3:
            self.__risk_level = 3

        if self.__tracer is not None:
            self.__tracer.state_changed(
                self.__device_id,
                "NetworkDevice",
                "increase_risk",
                "risk_level",
                previous_value,
                self.__risk_level
            )

            self.__tracer.method_completed(
                self.__device_id,
                "NetworkDevice",
                "increase_risk"
            )

    def overload(self, traffic_level):
        if self.__tracer is not None:
            self.__tracer.method_started(
                self.__device_id,
                "NetworkDevice",
                "overload"
            )

        previous_value = self.__traffic_level
        self.__traffic_level = traffic_level

        if self.__tracer is not None:
            self.__tracer.state_changed(
                self.__device_id,
                "NetworkDevice",
                "overload",
                "traffic_level",
                previous_value,
                self.__traffic_level
            )

            self.__tracer.method_completed(
                self.__device_id,
                "NetworkDevice",
                "overload"
            )

    def isolate(self):
        if self.__tracer is not None:
            self.__tracer.method_started(
                self.__device_id,
                "NetworkDevice",
                "isolate"
            )

        previous_isolated = self.__isolated
        previous_blocked = self.__blocked

        self.__isolated = True
        self.__blocked = True

        if self.__tracer is not None:
            self.__tracer.state_changed(
                self.__device_id,
                "NetworkDevice",
                "isolate",
                "isolated",
                previous_isolated,
                self.__isolated
            )

            self.__tracer.state_changed(
                self.__device_id,
                "NetworkDevice",
                "isolate",
                "blocked",
                previous_blocked,
                self.__blocked
            )

            self.__tracer.method_completed(
                self.__device_id,
                "NetworkDevice",
                "isolate"
            )

    def block(self):
        if self.__tracer is not None:
            self.__tracer.method_started(
                self.__device_id,
                "NetworkDevice",
                "block"
            )

        previous_value = self.__blocked
        self.__blocked = True

        if self.__tracer is not None:
            self.__tracer.state_changed(
                self.__device_id,
                "NetworkDevice",
                "block",
                "blocked",
                previous_value,
                self.__blocked
            )

            self.__tracer.method_completed(
                self.__device_id,
                "NetworkDevice",
                "block"
            )

    def unblock(self):
        if self.__tracer is not None:
            self.__tracer.method_started(
                self.__device_id,
                "NetworkDevice",
                "unblock"
            )

        previous_value = self.__blocked
        self.__blocked = False

        if self.__tracer is not None:
            self.__tracer.state_changed(
                self.__device_id,
                "NetworkDevice",
                "unblock",
                "blocked",
                previous_value,
                self.__blocked
            )

            self.__tracer.method_completed(
                self.__device_id,
                "NetworkDevice",
                "unblock"
            )

    def lock_files(self):
        if self.__tracer is not None:
            self.__tracer.method_started(
                self.__device_id,
                "NetworkDevice",
                "lock_files"
            )

        previous_value = self.__files_locked
        self.__files_locked = True

        if self.__tracer is not None:
            self.__tracer.state_changed(
                self.__device_id,
                "NetworkDevice",
                "lock_files",
                "files_locked",
                previous_value,
                self.__files_locked
            )

            self.__tracer.method_completed(
                self.__device_id,
                "NetworkDevice",
                "lock_files"
            )

    def restore(self):
        if self.__tracer is not None:
            self.__tracer.method_started(
                self.__device_id,
                "NetworkDevice",
                "restore"
            )

        previous_risk = self.__risk_level
        previous_traffic = self.__traffic_level
        previous_isolated = self.__isolated
        previous_files_locked = self.__files_locked

        self.__risk_level = 0
        self.__traffic_level = "NORMAL"
        self.__isolated = False
        self.__files_locked = False

        if self.__tracer is not None:
            if previous_risk != self.__risk_level:
                self.__tracer.state_changed(
                    self.__device_id,
                    "NetworkDevice",
                    "restore",
                    "risk_level",
                    previous_risk,
                    self.__risk_level
                )

            if previous_traffic != self.__traffic_level:
                self.__tracer.state_changed(
                    self.__device_id,
                    "NetworkDevice",
                    "restore",
                    "traffic_level",
                    previous_traffic,
                    self.__traffic_level
                )

            if previous_isolated != self.__isolated:
                self.__tracer.state_changed(
                    self.__device_id,
                    "NetworkDevice",
                    "restore",
                    "isolated",
                    previous_isolated,
                    self.__isolated
                )

            if previous_files_locked != self.__files_locked:
                self.__tracer.state_changed(
                    self.__device_id,
                    "NetworkDevice",
                    "restore",
                    "files_locked",
                    previous_files_locked,
                    self.__files_locked
                )

            self.__tracer.method_completed(
                self.__device_id,
                "NetworkDevice",
                "restore"
            )

    def get_data(self):
        return {
            "device_id": self.__device_id,
            "name": self.__name,
            "risk_level": self.__risk_level,
            "compromised": self.compromised,
            "traffic_level": self.__traffic_level,
            "isolated": self.__isolated,
            "files_locked": self.__files_locked,
            "blocked": self.__blocked
        }

    def __str__(self):
        return (
            f"Device ID: {self.__device_id} \t "
            f"Name: {self.__name} \t "
            f"Risk Level: {self.__risk_level} \t "
            f"Compromised: {self.compromised}"
        )


class Connection:
    def __init__(self, connection_id, device1, device2):
        self.__connection_id = connection_id
        self.__device1 = device1
        self.__device2 = device2
        self.__intercepted = False
        self.__blocked = False
        self.__tracer = None

    @property
    def connection_id(self):
        return self.__connection_id

    @property
    def device1(self):
        return self.__device1

    @property
    def device2(self):
        return self.__device2

    @property
    def intercepted(self):
        return self.__intercepted

    @property
    def blocked(self):
        return self.__blocked

    def set_tracer(self, tracer):
        self.__tracer = tracer

    def intercept(self):
        if self.__tracer is not None:
            self.__tracer.method_started(
                self.__connection_id,
                "Connection",
                "intercept"
            )

        if not self.__intercepted:
            previous_value = self.__intercepted
            self.__intercepted = True

            if self.__tracer is not None:
                self.__tracer.state_changed(
                    self.__connection_id,
                    "Connection",
                    "intercept",
                    "intercepted",
                    previous_value,
                    self.__intercepted
                )

            self.__device1.increase_risk(1)
            self.__device2.increase_risk(1)

        if self.__tracer is not None:
            self.__tracer.method_completed(
                self.__connection_id,
                "Connection",
                "intercept"
            )

    def secure(self):
        if self.__tracer is not None:
            self.__tracer.method_started(
                self.__connection_id,
                "Connection",
                "secure"
            )

        previous_value = self.__intercepted
        self.__intercepted = False

        if self.__tracer is not None:
            self.__tracer.state_changed(
                self.__connection_id,
                "Connection",
                "secure",
                "intercepted",
                previous_value,
                self.__intercepted
            )

            self.__tracer.method_completed(
                self.__connection_id,
                "Connection",
                "secure"
            )

    def block(self):
        if self.__tracer is not None:
            self.__tracer.method_started(
                self.__connection_id,
                "Connection",
                "block"
            )

        previous_value = self.__blocked
        self.__blocked = True

        if self.__tracer is not None:
            self.__tracer.state_changed(
                self.__connection_id,
                "Connection",
                "block",
                "blocked",
                previous_value,
                self.__blocked
            )

            self.__tracer.method_completed(
                self.__connection_id,
                "Connection",
                "block"
            )

    def unblock(self):
        if self.__tracer is not None:
            self.__tracer.method_started(
                self.__connection_id,
                "Connection",
                "unblock"
            )

        previous_value = self.__blocked
        self.__blocked = False

        if self.__tracer is not None:
            self.__tracer.state_changed(
                self.__connection_id,
                "Connection",
                "unblock",
                "blocked",
                previous_value,
                self.__blocked
            )

            self.__tracer.method_completed(
                self.__connection_id,
                "Connection",
                "unblock"
            )

    def get_data(self):
        return {
            "connection_id": self.__connection_id,
            "device1": self.__device1.device_id,
            "device2": self.__device2.device_id,
            "intercepted": self.__intercepted,
            "blocked": self.__blocked
        }

    def __str__(self):
        return (
            f"Connection ID: {self.__connection_id} \t "
            f"Device 1: {self.__device1.name} \t "
            f"Device 2: {self.__device2.name} \t "
            f"Intercepted: {self.__intercepted}"
        )