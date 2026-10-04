class ExecutionEvent:
    __event_id = 1 # Class Variable

    def __init__(self, event_type, object_id, class_name, method_name,
                 target_id=None, attribute=None,
                 previous_value=None, new_value=None, message=""):
        self.__event_id = ExecutionEvent.__event_id
        ExecutionEvent.__event_id += 1

        self.__event_type = event_type
        self.__object_id = object_id
        self.__class_name = class_name
        self.__method_name = method_name
        self.__target_id = target_id
        self.__attribute = attribute
        self.__previous_value = previous_value
        self.__new_value = new_value
        self.__message = message

    @classmethod
    def reset_event_id(cls):
        cls.__event_id = 1

    @property
    def event_id(self):
        return self.__event_id

    @property
    def event_type(self):
        return self.__event_type

    @property
    def object_id(self):
        return self.__object_id

    @property
    def class_name(self):
        return self.__class_name

    @property
    def method_name(self):
        return self.__method_name

    @property
    def target_id(self):
        return self.__target_id

    @property
    def attribute(self):
        return self.__attribute

    @property
    def previous_value(self):
        return self.__previous_value

    @property
    def new_value(self):
        return self.__new_value

    @property
    def message(self):
        return self.__message

    def get_data(self):
        return {
            "event_id": self.__event_id,
            "event_type": self.__event_type,
            "object_id": self.__object_id,
            "class_name": self.__class_name,
            "method_name": self.__method_name,
            "target_id": self.__target_id,
            "attribute": self.__attribute,
            "previous_value": self.__previous_value,
            "new_value": self.__new_value,
            "message": self.__message
        }

    def __str__(self):
        if self.__event_type == "STATE_CHANGED":
            return (
                f"Event ID: {self.__event_id} \t "
                f"Type: {self.__event_type} \t "
                f"Class: {self.__class_name} \t "
                f"Method: {self.__method_name} \t "
                f"{self.__attribute}: {self.__previous_value} -> {self.__new_value}"
            )

        return (
            f"Event ID: {self.__event_id} \t "
            f"Type: {self.__event_type} \t "
            f"Class: {self.__class_name} \t "
            f"Method: {self.__method_name}"
        )


class ExecutionTracer:
    def __init__(self):
        self.__events = []

    @property
    def events(self):
        return self.__events

    def add_event(self, event):
        self.__events.append(event)

    def method_started(self, object_id, class_name, method_name,
                       target_id=None, message=""):
        event = ExecutionEvent(
            "METHOD_STARTED",
            object_id,
            class_name,
            method_name,
            target_id,
            message=message
        )
        self.__events.append(event)

    def method_completed(self, object_id, class_name, method_name,
                         target_id=None, message=""):
        event = ExecutionEvent(
            "METHOD_COMPLETED",
            object_id,
            class_name,
            method_name,
            target_id,
            message=message
        )
        self.__events.append(event)

    def state_changed(self, object_id, class_name, method_name,
                      attribute, previous_value, new_value):
        event = ExecutionEvent(
            "STATE_CHANGED",
            object_id,
            class_name,
            method_name,
            attribute=attribute,
            previous_value=previous_value,
            new_value=new_value
        )
        self.__events.append(event)

    def clear(self):
        self.__events = []
        ExecutionEvent.reset_event_id()

    def __str__(self):
        result = ""

        for event in self.__events:
            result += str(event) + "\n"

        return result