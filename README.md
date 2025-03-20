# retico-simplelogger
A simple logger module for logging incremental units to JSON.

---

### Required Packages  
- orjson  
 
Run `pip install orjson` to install the required dependency.

---

### Example Runner
```python
import os, sys

PREFIX = "<path-to-retico-repositories>"
os.environ["RETICO"] = PREFIX + "retico-core"
os.environ["WASR"] = PREFIX + "retico-whisperasr"
os.environ["SLGR"] = PREFIX + "retico-simplelogger"
sys.path.append(os.environ["RETICO"])
sys.path.append(os.environ["WASR"])
sys.path.append(os.environ["SLGR"])

from retico_core.abstract import UpdateType
from retico_core.text import SpeechRecognitionIU
from retico_core.audio import MicrophoneModule
from retico_core.debug import DebugModule
from retico_whisperasr.whisperasr import WhisperASRModule
from retico_simplelogger.simplelogger import SimpleLoggerModule


mic = MicrophoneModule()
debug = DebugModule(print_payload_only=True)
asr = WhisperASRModule(lang="en")
logger = SimpleLoggerModule(filename='log', unit_types=[SpeechRecognitionIU], update_types=[UpdateType.ADD])

mic.subscribe(asr)
asr.subscribe(debug)
asr.subscribe(logger)

mic.run()
asr.run()
logger.run()
debug.run()

input()

mic.stop()
asr.stop()
logger.stop()
debug.stop()
```
---
