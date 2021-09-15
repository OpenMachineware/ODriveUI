# ODriveUI

A GUI for ODrive operation.

We currently work with odrive-0.5.2.post0, for the 0.5.3.post0 with a bug 
about timeout.

## Usage

- Setup python environment
```
virtualenv venv
```
- Activate python virtual environment
```
source venv/bin/activate
```

- Install requirements
```
pip install odrive==0.5.2.post0
pip install pyqtgraph
pip install PySide6
pip install pyinstaller
```

- Run

Power on and plug your ODrive board in, first.
```
python main.py
```

## Pack
- Pack a `release` version
```
pyinstaller -w -F main.py
```

- Pack a `debug` version
```
pyinstaller -c -F main.py
```
## TODO
- Disconnect support.
- Reconnect when the board rebooted.
- Record waves.
