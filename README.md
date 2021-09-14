# ODriveUI

A GUI for ODrive operation.

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
pip install odrive
pip install pyqtgraph
pip install PySide6
pip install Pillow
```

- Run

Power on and plug your ODrive board in, first.
```
python main.py
```

## TODO
- Offline mode when the board can not be connected.
- Reconnect when the board rebooted.
- Record waves.
