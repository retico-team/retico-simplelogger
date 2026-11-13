# retico-simplelogger
A simple module for logging incremental units to a JSON file.

## Installation and Requirements

To use the simple logger module you first need to install the retico-simplelogger package:
* Install retico-simplelogger:
```pip install retico-simplelogger```

  or, for the latest development version from GitHub:
```pip install git+https://github.com/retico-team/retico-simplelogger.git```

## Modules

### `SimpleLoggerModule`
Subscribes to any IU and writes each incoming IU to a JSON file, with its timestamp, payload, unit type, update type, IU id, creator, previous IU and grounded-in IU. It doesn't output any IUs.

#### Arguments:
* `filename` (str): the name of the file to write to; `.json` is added if missing
* `update_types` (list): only log IUs with one of these update types; defaults to `None` (all update types)
* `unit_types` (list): only log IUs of one of these types; defaults to `None` (all unit types)

### Example
**Note:** The example uses `MicrophoneModule` and `DebugModule` from `retico_core` and `WhisperASRModule` from [retico-whisperasr](https://github.com/retico-team/retico-whisperasr) (`pip install retico-whisperasr`).

```python
from retico_core.abstract import UpdateType
from retico_core.text import SpeechRecognitionIU
from retico_core.audio import MicrophoneModule
from retico_core.debug import DebugModule
from retico_whisperasr import WhisperASRModule
from retico_simplelogger import SimpleLoggerModule


mic = MicrophoneModule()
debug = DebugModule(print_payload_only=True)
asr = WhisperASRModule(language="english")
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
