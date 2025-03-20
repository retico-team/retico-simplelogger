import time
import threading
import json
from collections import deque

import retico_core
from retico_core import UpdateType
from retico_core.abstract import IncrementalUnit
from retico_core.text import TextIU

class SimpleLoggerModule(retico_core.AbstractConsumingModule):
    @staticmethod
    def name():
        return "Simple Logger Module"

    @staticmethod
    def description():
        return "Logs incoming payloads as JSON"

    @staticmethod
    def input_ius():
        return [IncrementalUnit]

    @staticmethod
    def output_iu():
        return None

    def __init__(self, filename, types=None, units=None, **kwargs):
        super().__init__(**kwargs)
        self.queue = deque()
        self.iu_count = 0

        if filename.endswith(".json"):
            self.filename = filename
        else:
            self.filename = filename + ".json"

        self.types = types
        if self.types is None:
            self.types = [
                UpdateType.ADD,
                UpdateType.REVOKE,
                UpdateType.COMMIT
            ]

        self.units = units
        if self.units is None:
            self.units = [IncrementalUnit, TextIU]

        self._loop_active = True
        threading.Thread(target=self._loop).start()

    def process_update(self, update_message):
        for iu, ut in update_message:
            if type(iu) in self.units and ut in self.types:
                self.queue.append((iu, ut))

    def _loop(self):
        with open(self.filename, 'w') as file:
            file.write("[")
            while self._loop_active:
                if len(self.queue) == 0:
                    time.sleep(0.01)
                    continue

                input_iu, ut = self.queue.popleft()
                entry = {
                    "timestamp": input_iu.created_at,
                    "payload": input_iu.payload,
                    "unit_type": type(input_iu).__name__,
                    "update_type": str(ut),
                    "creator": input_iu.creator,
                    "iuid": input_iu.iuid,
                    "grounded_in": input_iu.grounded_in,
                }

                if input_iu.previous_iu is not None:
                    entry["previous_iu"] = type(input_iu.previous_iu).__name__
                else:
                    entry["previous_iu"] = None


                if self.iu_count != 0:
                    file.write(", ")
                json.dump(entry, file, indent=4)
                self.iu_count += 1

            file.write("]")

    def shutdown(self):
        self._loop_active = False
