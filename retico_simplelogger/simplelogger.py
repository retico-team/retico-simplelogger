import time
import threading
from collections import deque
import orjson
import retico_core

def _default(obj):
    """
    Default function for orjson.dumps().

    :param obj: The object to serialize.
    :return: The name of the object being serialized.
    """
    try:
        return type(obj).__name__
    except Exception:
        raise AttributeError(f"Can't call __name__ off of {type(obj)}. Failed to serialize {obj}.")


class SimpleLoggerModule(retico_core.AbstractConsumingModule):
    """A simple module for logging incremental units."""

    @staticmethod
    def name():
        return "Simple Logger Module"

    @staticmethod
    def description():
        return "Logs incoming IUs as JSON"

    @staticmethod
    def input_ius():
        return [retico_core.IncrementalUnit]

    @staticmethod
    def output_iu():
        return None

    def __init__(self, filename: str, update_types: list=None, unit_types: list=None, **kwargs):
        """
        Constructor for a SimpleLoggerModule.

        :param filename: The name of the file to write to.
        :param update_types: Optional filtering argument. A list that specifies what update types are required for a unit to be logged.
        :param unit_types: Optional filtering argument. A list that specifies what unit types should be logged.
        """
        super().__init__(**kwargs)
        self.queue = deque()
        self.iu_count = 0
        self.types_filter_on = False
        self.units_filter_on = False

        if filename.endswith(".json"):
            self.filename = filename
        else:
            self.filename = filename + ".json"

        self.types = update_types
        self.units = unit_types

        if update_types is not None:
            self.types_filter_on = True

        if unit_types is not None:
            self.units_filter_on = True

        self._loop_active = True
        threading.Thread(target=self._loop).start()

    def process_update(self, update_message):
        for iu, ut in update_message:
            if self.units_filter_on and self.types_filter_on:
                if type(iu) in self.units and ut in self.types:
                    self.queue.append((iu, ut))
            elif self.units_filter_on:
                if type(iu) in self.units:
                    self.queue.append((iu, ut))
            elif self.types_filter_on:
                if ut in self.types:
                    self.queue.append((iu, ut))
            else:
                self.queue.append((iu, ut))

    def _loop(self):
        """Threaded loop for dumping IUs to JSON file."""

        with open(self.filename, 'wb') as file:
            file.write("[".encode("utf-8"))
            while self._loop_active or len(self.queue) > 0:
                if len(self.queue) == 0:
                    time.sleep(0.01)
                    continue

                iu, ut = self.queue.popleft()
                entry = {
                    "timestamp": iu.created_at,
                    "payload": iu.payload,
                    "unit_type": iu,
                    "update_type": ut,
                    "iuid": iu.iuid,
                    "creator": iu.creator,
                    "previous_iu": iu.previous_iu,
                    "grounded_in": iu.grounded_in,
                }

                if self.iu_count != 0:
                    file.write(", ".encode("utf-8"))
                file.write(orjson.dumps(entry, option=orjson.OPT_INDENT_2, default=_default))
                self.iu_count += 1

            file.write("]".encode("utf-8"))

    def shutdown(self):
        self._loop_active = False
