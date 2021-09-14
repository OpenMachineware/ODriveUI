import pyqtgraph as pg

from odrive.enums import *
from pyqtgraph import PlotWidget
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from conf.conf import BUTTON_CHANGED_COLOR, SAMPLING_PERIOD, \
    STATE_UPDATING_PERIOD
from utils.config import load_conf
from utils.connection_thread import ODriveConnector
from utils.error_check import check_axis_encoder_errors, check_axis_errors, \
    check_axis_motor_errors
from widgets.config import ODriveConfig
from widgets.select_drive import SelectDrive


class Dashboard(QWidget):
    def __init__(self, conf, drive, drive_index, parent=None):
        super(Dashboard, self).__init__(parent)
        if drive is None or drive_index is None:
            self.setWindowTitle('Dashboard: ' + 'offline')
            self.online = False
        else:
            self.online = True
            self.setWindowTitle('Dashboard: ' + 'odrv' + str(drive_index))
        self.resize(1280, 768)

        self.conf = conf
        self.odrive_worker = None
        self.drive_list = None
        self.drive = drive
        self.drive_index = drive_index
        self.select_dialog = None
        self.config_window = None
        self.play = False
        self.record = False
        self.timer_state = None
        self.timer_graph = None
        pen_sp_axis0 = pg.mkPen(color=(0, 128, 255), width=1)
        pen_est_axis0 = pg.mkPen(color=(135, 0, 191), width=1)
        pen_sp_axis1 = pg.mkPen(color=(255, 78, 0), width=1)
        pen_est_axis1 = pg.mkPen(color=(255, 212, 0), width=1)
        self.axis_dict = {}
        self.axis0_state = None
        self.axis1_state = None
        self.axis0_current_input_mode = None
        self.axis1_current_input_mode = None
        self.sampling_period = self.get_sampling_period()

        state_btn_size_width = 50
        state_btn_size_height = 55

        self.pixmap_forward = QPixmap('resources/right.png')
        self.pixmap_backward = QPixmap('resources/left.png')
        self.pixmap_stop = QPixmap('resources/stop.png')
        self.icon_forward = QIcon()
        self.icon_forward.addPixmap(self.pixmap_forward,
                                    QIcon.Normal, QIcon.Off)
        self.icon_backward = QIcon()
        self.icon_backward.addPixmap(self.pixmap_backward,
                                     QIcon.Normal, QIcon.Off)
        self.icon_stop = QIcon()
        self.icon_stop.addPixmap(self.pixmap_stop, QIcon.Normal, QIcon.Off)

        self.pixmap_start = QPixmap('resources/start.png')
        self.pixmap_pause = QPixmap('resources/pause.png')
        self.pixmap_record = QPixmap('resources/record.png')
        self.pixmap_record_stop = QPixmap('resources/stop_record.png')
        self.pixmap_clean = QPixmap('resources/clean.png')
        self.icon_start = QIcon()
        self.icon_start.addPixmap(self.pixmap_start, QIcon.Normal, QIcon.Off)
        self.icon_pause = QIcon()
        self.icon_pause.addPixmap(self.pixmap_pause, QIcon.Normal, QIcon.Off)
        self.icon_record = QIcon()
        self.icon_record.addPixmap(self.pixmap_record, QIcon.Normal, QIcon.Off)
        self.icon_record_stop = QIcon()
        self.icon_record_stop.addPixmap(self.pixmap_record_stop,
                                        QIcon.Normal, QIcon.Off)
        self.icon_clean = QIcon()
        self.icon_clean.addPixmap(self.pixmap_clean, QIcon.Normal, QIcon.Off)

        self.pixmap_up = QPixmap('resources/up.png')
        self.pixmap_down = QPixmap('resources/down.png')
        self.icon_up = QIcon()
        self.icon_up.addPixmap(self.pixmap_up, QIcon.Normal, QIcon.Off)
        self.icon_down = QIcon()
        self.icon_down.addPixmap(self.pixmap_down, QIcon.Normal, QIcon.Off)

        self.pixmap_disconnect = QPixmap('resources/disconnect.png')
        self.pixmap_connect = QPixmap('resources/connect.png')
        self.pixmap_set = QPixmap('resources/set.png')
        self.pixmap_english = QPixmap('resources/english.png')
        self.pixmap_chinese = QPixmap('resources/chinese.png')
        self.icon_disconnect = QIcon()
        self.icon_disconnect.addPixmap(self.pixmap_disconnect,
                                       QIcon.Normal, QIcon.Off)
        self.icon_connect = QIcon()
        self.icon_connect.addPixmap(self.pixmap_connect,
                                    QIcon.Normal, QIcon.Off)
        self.icon_setup = QIcon()
        self.icon_setup.addPixmap(self.pixmap_set, QIcon.Normal, QIcon.Off)
        self.icon_chinese = QIcon()
        self.icon_chinese.addPixmap(self.pixmap_chinese,
                                    QIcon.Normal, QIcon.Off)
        self.icon_english = QIcon()
        self.icon_english.addPixmap(self.pixmap_english,
                                    QIcon.Normal, QIcon.Off)

        axis0_state_gird = QGridLayout()
        self.axis0_btn_state_idle = QPushButton('Idle')
        self.axis0_btn_state_idle.setMinimumSize(state_btn_size_width,
                                                 state_btn_size_height)
        self.axis0_btn_state_idle.clicked.connect(
            self.axis0_state_idle_clicked)
        self.axis0_btn_state_startup_sequence = QPushButton('Startup\nSequence')
        self.axis0_btn_state_startup_sequence.setMinimumSize(
            state_btn_size_width, state_btn_size_height)
        self.axis0_btn_state_startup_sequence.clicked.connect(
            self.axis0_state_startup_sequence_clicked)
        self.axis0_btn_state_full_calibration_sequence = \
            QPushButton('Full\nCalibration\nSequence')
        self.axis0_btn_state_full_calibration_sequence.setMinimumSize(
            state_btn_size_width, state_btn_size_height)
        self.axis0_btn_state_full_calibration_sequence.clicked.connect(
            self.axis0_state_full_calibration_sequence_clicked)
        self.axis0_btn_state_motor_calibration = QPushButton(
            'Motor\nCalibration')
        self.axis0_btn_state_motor_calibration.setMinimumSize(
            state_btn_size_width, state_btn_size_height)
        self.axis0_btn_state_motor_calibration.clicked.connect(
            self.axis0_state_motor_calibration_clicked)
        self.axis0_btn_state_encoder_index_search = \
            QPushButton('Encoder\nIndex\nSearch')
        self.axis0_btn_state_encoder_index_search.setMinimumSize(
            state_btn_size_width, state_btn_size_height)
        self.axis0_btn_state_encoder_index_search.clicked.connect(
            self.axis0_state_encoder_index_search_clicked)
        self.axis0_btn_state_encoder_offset_calibration = \
            QPushButton('Encoder\nOffset\nCalibration')
        self.axis0_btn_state_encoder_offset_calibration.setMinimumSize(
            state_btn_size_width, state_btn_size_height)
        self.axis0_btn_state_encoder_offset_calibration.clicked.connect(
            self.axis0_state_encoder_offset_calibration_clicked)
        self.axis0_btn_state_closed_loop_control = \
            QPushButton('Closed\nLoop\nControl')
        self.axis0_btn_state_closed_loop_control.setMinimumSize(
            state_btn_size_width, state_btn_size_height)
        self.axis0_btn_state_closed_loop_control.clicked.connect(
            self.axis0_state_closed_loop_control_clicked)
        self.axis0_btn_state_lockin_spin = QPushButton('Lockin\nSpin')
        self.axis0_btn_state_lockin_spin.setMinimumSize(state_btn_size_width,
                                                        state_btn_size_height)
        self.axis0_btn_state_lockin_spin.clicked.connect(
            self.axis0_state_lockin_spin_clicked)
        self.axis0_btn_state_encoder_dir_find = QPushButton(
            'Encoder\nDir\nFind')
        self.axis0_btn_state_encoder_dir_find.setMinimumSize(
            state_btn_size_width, state_btn_size_height)
        self.axis0_btn_state_encoder_dir_find.clicked.connect(
            self.axis0_state_encoder_dir_find_clicked)
        self.axis0_btn_state_homing = QPushButton('Homing')
        self.axis0_btn_state_homing.setMinimumSize(state_btn_size_width,
                                                   state_btn_size_height)
        self.axis0_btn_state_homing.clicked.connect(
            self.axis0_state_homing_clicked)
        self.axis0_btn_state_encoder_hall_polarity_calibration = \
            QPushButton('Encoder\nHall Polarity\nCalibration')
        self.axis0_btn_state_encoder_hall_polarity_calibration.setMinimumSize(
            state_btn_size_width, state_btn_size_height)
        self.axis0_btn_state_encoder_hall_polarity_calibration.clicked.connect(
            self.axis0_state_encoder_hall_polarity_calibration_clicked)
        self.axis0_btn_state_encoder_hall_phase_calibration = \
            QPushButton('Encoder\nHall Phase\nCalibration')
        self.axis0_btn_state_encoder_hall_phase_calibration.setMinimumSize(
            state_btn_size_width, state_btn_size_height)
        self.axis0_btn_state_encoder_hall_phase_calibration.clicked.connect(
            self.axis0_state_encoder_hall_phase_calibration_clicked)
        axis0_state_gird.addWidget(self.axis0_btn_state_idle, 0, 0)
        axis0_state_gird.addWidget(self.axis0_btn_state_startup_sequence, 0, 1)
        axis0_state_gird.addWidget(
            self.axis0_btn_state_full_calibration_sequence, 0, 2)
        axis0_state_gird.addWidget(self.axis0_btn_state_motor_calibration, 0, 3)
        axis0_state_gird.addWidget(
            self.axis0_btn_state_encoder_index_search, 1, 0)
        axis0_state_gird.addWidget(
            self.axis0_btn_state_encoder_offset_calibration, 1, 1)
        axis0_state_gird.addWidget(
            self.axis0_btn_state_closed_loop_control, 1, 2)
        axis0_state_gird.addWidget(self.axis0_btn_state_lockin_spin, 1, 3)
        axis0_state_gird.addWidget(self.axis0_btn_state_encoder_dir_find, 2, 0)
        axis0_state_gird.addWidget(self.axis0_btn_state_homing, 2, 1)
        axis0_state_gird.addWidget(
            self.axis0_btn_state_encoder_hall_polarity_calibration, 2, 2)
        axis0_state_gird.addWidget(
            self.axis0_btn_state_encoder_hall_phase_calibration, 2, 3)
        self.axis0_state_group = QGroupBox('Axis0 State')
        self.axis0_state_group.setLayout(axis0_state_gird)

        axis0_input_mode_gird = QGridLayout()
        self.axis0_btn_input_mode_pass_through = QPushButton('Passthrough')
        self.axis0_btn_input_mode_pass_through.clicked.connect(
            self.axis0_input_mode_pass_through_clicked)
        self.axis0_btn_input_mode_vel_ramp = QPushButton('Vel Ramp')
        self.axis0_btn_input_mode_vel_ramp.clicked.connect(
            self.axis0_input_mode_vel_ramp_clicked)
        self.axis0_btn_input_mode_pos_filter = QPushButton('Pos Filter')
        self.axis0_btn_input_mode_pos_filter.clicked.connect(
            self.axis0_input_mode_pos_filter_clicked)
        self.axis0_btn_input_mode_mix_channels = QPushButton('Mix Channels')
        self.axis0_btn_input_mode_mix_channels.clicked.connect(
            self.axis0_input_mode_mix_channels_clicked)
        self.axis0_btn_input_mode_trap_traj = QPushButton('Trap Traj')
        self.axis0_btn_input_mode_trap_traj.clicked.connect(
            self.axis0_input_mode_trap_traj_clicked)
        self.axis0_btn_input_mode_troque_ramp = QPushButton('Troque Ramp')
        self.axis0_btn_input_mode_troque_ramp.clicked.connect(
            self.axis0_input_mode_troque_ramp_clicked)
        self.axis0_btn_input_mode_mirror = QPushButton('Mirror')
        self.axis0_btn_input_mode_mirror.clicked.connect(
            self.axis0_input_mode_mirror_clicked)
        self.axis0_btn_input_mode_tuning = QPushButton('Tuning')
        self.axis0_btn_input_mode_tuning.clicked.connect(
            self.axis0_input_mode_tuning_clicked)
        axis0_input_mode_gird.addWidget(
            self.axis0_btn_input_mode_pass_through, 0, 0)
        axis0_input_mode_gird.addWidget(
            self.axis0_btn_input_mode_vel_ramp, 0, 1)
        axis0_input_mode_gird.addWidget(
            self.axis0_btn_input_mode_pos_filter, 0, 2)
        axis0_input_mode_gird.addWidget(
            self.axis0_btn_input_mode_mix_channels, 0, 3)
        axis0_input_mode_gird.addWidget(
            self.axis0_btn_input_mode_trap_traj, 1, 0)
        axis0_input_mode_gird.addWidget(
            self.axis0_btn_input_mode_troque_ramp, 1, 1)
        axis0_input_mode_gird.addWidget(self.axis0_btn_input_mode_mirror, 1, 2)
        axis0_input_mode_gird.addWidget(self.axis0_btn_input_mode_tuning, 1, 3)
        self.axis0_input_mode_group = QGroupBox('Axis0 Input Mode')
        self.axis0_input_mode_group.setLayout(axis0_input_mode_gird)

        axis0_input_gird = QGridLayout()
        self.axis0_radio_input_torque = QRadioButton('Torque (Nm)')
        self.axis0_spin_input_torque = QSpinBox()
        self.axis0_spin_input_torque.setMaximum(100)
        self.axis0_btn_input_torque_clock_wise = QPushButton()
        self.axis0_btn_input_torque_clock_wise.setDisabled(True)
        self.axis0_btn_input_torque_clock_wise.pressed.connect(
            self.axis0_input_torque_clock_wise_pressed)
        self.axis0_btn_input_torque_counter_clock_wise = QPushButton()
        self.axis0_btn_input_torque_counter_clock_wise.setDisabled(True)
        self.axis0_btn_input_torque_counter_clock_wise.pressed.connect(
            self.axis0_input_torque_counter_clock_wise_pressed)
        self.axis0_btn_input_torque_stop = QPushButton()
        self.axis0_btn_input_torque_stop.setDisabled(True)
        self.axis0_btn_input_torque_stop.pressed.connect(
            self.axis0_input_torque_stop_pressed)
        self.axis0_btn_input_torque_clock_wise.setIcon(self.icon_forward)
        self.axis0_btn_input_torque_counter_clock_wise.setIcon(
            self.icon_backward)
        self.axis0_btn_input_torque_stop.setIcon(self.icon_stop)
        self.axis0_radio_input_velocity = QRadioButton('Velocity (Turns/s)')
        self.axis0_spin_input_velocity = QSpinBox()
        self.axis0_spin_input_velocity.setMaximum(1000)
        self.axis0_btn_input_velocity_clock_wise = QPushButton()
        self.axis0_btn_input_velocity_clock_wise.setDisabled(True)
        self.axis0_btn_input_velocity_clock_wise.pressed.connect(
            self.axis0_input_velocity_clock_wise_pressed)
        self.axis0_btn_input_velocity_counter_clock_wise = QPushButton()
        self.axis0_btn_input_velocity_counter_clock_wise.setDisabled(True)
        self.axis0_btn_input_velocity_counter_clock_wise.pressed.connect(
            self.axis0_input_velocity_counter_clock_wise_pressed)
        self.axis0_btn_input_velocity_stop = QPushButton()
        self.axis0_btn_input_velocity_stop.setDisabled(True)
        self.axis0_btn_input_velocity_stop.pressed.connect(
            self.axis0_input_velocity_stop_pressed)
        self.axis0_btn_input_velocity_clock_wise.setIcon(self.icon_forward)
        self.axis0_btn_input_velocity_counter_clock_wise.setIcon(
            self.icon_backward)
        self.axis0_btn_input_velocity_stop.setIcon(self.icon_stop)
        self.axis0_radio_input_position = QRadioButton('Position (Turns)')
        self.axis0_radio_input_position.setChecked(True)
        self.axis0_spin_input_position = QSpinBox()
        self.axis0_spin_input_position.setMinimum(-10000)
        self.axis0_spin_input_position.setMaximum(10000)
        self.axis0_spin_input_position.setValue(0)
        self.axis0_btn_input_position = QPushButton('GO')
        self.axis0_btn_input_position.pressed.connect(
            self.axis0_input_position_pressed)
        self.axis0_radio_input_group = QButtonGroup()
        self.axis0_radio_input_group.addButton(self.axis0_radio_input_torque)
        self.axis0_radio_input_group.addButton(self.axis0_radio_input_velocity)
        self.axis0_radio_input_group.addButton(self.axis0_radio_input_position)
        self.axis0_radio_input_group.buttonClicked.connect(
            self.axis0_controller_mode_changed)

        axis0_input_gird.addWidget(self.axis0_radio_input_torque, 0, 0)
        axis0_input_gird.addWidget(self.axis0_spin_input_torque, 0, 1)
        axis0_input_gird.addWidget(
            self.axis0_btn_input_torque_counter_clock_wise, 0, 2)
        axis0_input_gird.addWidget(self.axis0_btn_input_torque_stop, 0, 3)
        axis0_input_gird.addWidget(self.axis0_btn_input_torque_clock_wise, 0, 4)
        axis0_input_gird.addWidget(self.axis0_radio_input_velocity, 1, 0)
        axis0_input_gird.addWidget(self.axis0_spin_input_velocity, 1, 1)
        axis0_input_gird.addWidget(
            self.axis0_btn_input_velocity_counter_clock_wise, 1, 2)
        axis0_input_gird.addWidget(self.axis0_btn_input_velocity_stop, 1, 3)
        axis0_input_gird.addWidget(
            self.axis0_btn_input_velocity_clock_wise, 1, 4)
        axis0_input_gird.addWidget(self.axis0_radio_input_position, 2, 0)
        axis0_input_gird.addWidget(self.axis0_spin_input_position, 2, 1)
        axis0_input_gird.addWidget(self.axis0_btn_input_position, 2, 2, 1, 3)

        self.axis0_group = QGroupBox('Axis0')
        axis0_v_box = QVBoxLayout()
        axis0_v_box.addWidget(self.axis0_state_group)
        axis0_v_box.addWidget(self.axis0_input_mode_group)
        axis0_v_box.addLayout(axis0_input_gird)
        self.axis0_group.setLayout(axis0_v_box)

        axis1_state_gird = QGridLayout()
        self.axis1_btn_state_idle = QPushButton('Idle')
        self.axis1_btn_state_idle.setMinimumSize(state_btn_size_width,
                                                 state_btn_size_height)
        self.axis1_btn_state_idle.clicked.connect(
            self.axis1_state_idle_clicked)
        self.axis1_btn_state_startup_sequence = QPushButton('Startup\nSequence')
        self.axis1_btn_state_startup_sequence.setMinimumSize(
            state_btn_size_width, state_btn_size_height)
        self.axis1_btn_state_startup_sequence.clicked.connect(
            self.axis1_state_startup_sequence_clicked)
        self.axis1_btn_state_full_calibration_sequence = \
            QPushButton('Full\nCalibration\nSequence')
        self.axis1_btn_state_full_calibration_sequence.setMinimumSize(
            state_btn_size_width, state_btn_size_height)
        self.axis1_btn_state_full_calibration_sequence.clicked.connect(
            self.axis1_state_full_calibration_sequence_clicked)
        self.axis1_btn_state_motor_calibration = QPushButton(
            'Motor\nCalibration')
        self.axis1_btn_state_motor_calibration.setMinimumSize(
            state_btn_size_width, state_btn_size_height)
        self.axis1_btn_state_motor_calibration.clicked.connect(
            self.axis1_state_motor_calibration_clicked)
        self.axis1_btn_state_encoder_index_search = \
            QPushButton('Encoder\nIndex\nSearch')
        self.axis1_btn_state_encoder_index_search.setMinimumSize(
            state_btn_size_width, state_btn_size_height)
        self.axis1_btn_state_encoder_index_search.clicked.connect(
            self.axis1_state_encoder_index_search_clicked)
        self.axis1_btn_state_encoder_offset_calibration = \
            QPushButton('Encoder\nOffset\nCalibration')
        self.axis1_btn_state_encoder_offset_calibration.setMinimumSize(
            state_btn_size_width, state_btn_size_height)
        self.axis1_btn_state_encoder_offset_calibration.clicked.connect(
            self.axis1_state_encoder_offset_calibration_clicked)
        self.axis1_btn_state_closed_loop_control = \
            QPushButton('Closed\nLoop\nControl')
        self.axis1_btn_state_closed_loop_control.setMinimumSize(
            state_btn_size_width, state_btn_size_height)
        self.axis1_btn_state_closed_loop_control.clicked.connect(
            self.axis1_state_closed_loop_control_clicked)
        self.axis1_btn_state_lockin_spin = QPushButton('Lockin\nSpin')
        self.axis1_btn_state_lockin_spin.setMinimumSize(state_btn_size_width,
                                                        state_btn_size_height)
        self.axis1_btn_state_lockin_spin.clicked.connect(
            self.axis1_state_lockin_spin_clicked)
        self.axis1_btn_state_encoder_dir_find = QPushButton(
            'Encoder\nDir\nFind')
        self.axis1_btn_state_encoder_dir_find.setMinimumSize(
            state_btn_size_width, state_btn_size_height)
        self.axis1_btn_state_encoder_dir_find.clicked.connect(
            self.axis1_state_encoder_dir_find_clicked)
        self.axis1_btn_state_homing = QPushButton('Homing')
        self.axis1_btn_state_homing.setMinimumSize(state_btn_size_width,
                                                   state_btn_size_height)
        self.axis1_btn_state_homing.clicked.connect(
            self.axis1_state_homing_clicked)
        self.axis1_btn_state_encoder_hall_polarity_calibration = \
            QPushButton('Encoder\nHall Polarity\nCalibration')
        self.axis1_btn_state_encoder_hall_polarity_calibration.setMinimumSize(
            state_btn_size_width, state_btn_size_height)
        self.axis1_btn_state_encoder_hall_polarity_calibration.clicked.connect(
            self.axis1_state_encoder_hall_polarity_calibration_clicked)
        self.axis1_btn_state_encoder_hall_phase_calibration = \
            QPushButton('Encoder\nHall Phase\nCalibration')
        self.axis1_btn_state_encoder_hall_phase_calibration.setMinimumSize(
            state_btn_size_width, state_btn_size_height)
        self.axis1_btn_state_encoder_hall_phase_calibration.clicked.connect(
            self.axis1_state_encoder_hall_phase_calibration_clicked)
        axis1_state_gird.addWidget(self.axis1_btn_state_idle, 0, 0)
        axis1_state_gird.addWidget(self.axis1_btn_state_startup_sequence, 0, 1)
        axis1_state_gird.addWidget(
            self.axis1_btn_state_full_calibration_sequence, 0, 2)
        axis1_state_gird.addWidget(self.axis1_btn_state_motor_calibration, 0, 3)
        axis1_state_gird.addWidget(
            self.axis1_btn_state_encoder_index_search, 1, 0)
        axis1_state_gird.addWidget(
            self.axis1_btn_state_encoder_offset_calibration, 1, 1)
        axis1_state_gird.addWidget(
            self.axis1_btn_state_closed_loop_control, 1, 2)
        axis1_state_gird.addWidget(self.axis1_btn_state_lockin_spin, 1, 3)
        axis1_state_gird.addWidget(self.axis1_btn_state_encoder_dir_find, 2, 0)
        axis1_state_gird.addWidget(self.axis1_btn_state_homing, 2, 1)
        axis1_state_gird.addWidget(
            self.axis1_btn_state_encoder_hall_polarity_calibration, 2, 2)
        axis1_state_gird.addWidget(
            self.axis1_btn_state_encoder_hall_phase_calibration, 2, 3)
        self.axis1_state_group = QGroupBox('Axis1 State')
        self.axis1_state_group.setLayout(axis1_state_gird)

        axis1_input_mode_gird = QGridLayout()
        self.axis1_btn_input_mode_pass_through = QPushButton('Passthrough')
        self.axis1_btn_input_mode_pass_through.clicked.connect(
            self.axis1_input_mode_pass_through_clicked)
        self.axis1_btn_input_mode_vel_ramp = QPushButton('Vel Ramp')
        self.axis1_btn_input_mode_vel_ramp.clicked.connect(
            self.axis1_input_mode_vel_ramp_clicked)
        self.axis1_btn_input_mode_pos_filter = QPushButton('Pos Filter')
        self.axis1_btn_input_mode_pos_filter.clicked.connect(
            self.axis1_input_mode_pos_filter_clicked)
        self.axis1_btn_input_mode_mix_channels = QPushButton('Mix Channels')
        self.axis1_btn_input_mode_mix_channels.clicked.connect(
            self.axis1_input_mode_mix_channels_clicked)
        self.axis1_btn_input_mode_trap_traj = QPushButton('Trap Traj')
        self.axis1_btn_input_mode_trap_traj.clicked.connect(
            self.axis1_input_mode_trap_traj_clicked)
        self.axis1_btn_input_mode_troque_ramp = QPushButton('Troque Ramp')
        self.axis1_btn_input_mode_troque_ramp.clicked.connect(
            self.axis1_input_mode_troque_ramp_clicked)
        self.axis1_btn_input_mode_mirror = QPushButton('Mirror')
        self.axis1_btn_input_mode_mirror.clicked.connect(
            self.axis1_input_mode_mirror_clicked)
        self.axis1_btn_input_mode_tuning = QPushButton('Tuning')
        self.axis1_btn_input_mode_tuning.clicked.connect(
            self.axis1_input_mode_tuning_clicked)
        axis1_input_mode_gird.addWidget(
            self.axis1_btn_input_mode_pass_through, 0, 0)
        axis1_input_mode_gird.addWidget(
            self.axis1_btn_input_mode_vel_ramp, 0, 1)
        axis1_input_mode_gird.addWidget(
            self.axis1_btn_input_mode_pos_filter, 0, 2)
        axis1_input_mode_gird.addWidget(
            self.axis1_btn_input_mode_mix_channels, 0, 3)
        axis1_input_mode_gird.addWidget(
            self.axis1_btn_input_mode_trap_traj, 1, 0)
        axis1_input_mode_gird.addWidget(
            self.axis1_btn_input_mode_troque_ramp, 1, 1)
        axis1_input_mode_gird.addWidget(self.axis1_btn_input_mode_mirror, 1, 2)
        axis1_input_mode_gird.addWidget(self.axis1_btn_input_mode_tuning, 1, 3)
        self.axis1_input_mode_group = QGroupBox('Axis1 Input Mode')
        self.axis1_input_mode_group.setLayout(axis1_input_mode_gird)

        axis1_input_gird = QGridLayout()
        self.axis1_radio_input_torque = QRadioButton('Torque (Nm)')
        self.axis1_spin_input_torque = QSpinBox()
        self.axis1_spin_input_torque.setMaximum(100)
        self.axis1_btn_input_torque_clock_wise = QPushButton()
        self.axis1_btn_input_torque_clock_wise.setDisabled(True)
        self.axis1_btn_input_torque_clock_wise.pressed.connect(
            self.axis1_input_torque_clock_wise_pressed)
        self.axis1_btn_input_torque_counter_clock_wise = QPushButton()
        self.axis1_btn_input_torque_counter_clock_wise.setDisabled(True)
        self.axis1_btn_input_torque_counter_clock_wise.pressed.connect(
            self.axis1_input_torque_counter_clock_wise_pressed)
        self.axis1_btn_input_torque_stop = QPushButton()
        self.axis1_btn_input_torque_stop.setDisabled(True)
        self.axis1_btn_input_torque_stop.pressed.connect(
            self.axis1_input_torque_stop_pressed)
        self.axis1_btn_input_torque_clock_wise.setIcon(self.icon_forward)
        self.axis1_btn_input_torque_counter_clock_wise.setIcon(
            self.icon_backward)
        self.axis1_btn_input_torque_stop.setIcon(self.icon_stop)
        self.axis1_radio_input_velocity = QRadioButton('Velocity (Turns/s)')
        self.axis1_spin_input_velocity = QSpinBox()
        self.axis1_spin_input_velocity.setMaximum(1000)
        self.axis1_btn_input_velocity_clock_wise = QPushButton()
        self.axis1_btn_input_velocity_clock_wise.setDisabled(True)
        self.axis1_btn_input_velocity_clock_wise.pressed.connect(
            self.axis1_input_velocity_clock_wise_pressed)
        self.axis1_btn_input_velocity_counter_clock_wise = QPushButton()
        self.axis1_btn_input_velocity_counter_clock_wise.setDisabled(True)
        self.axis1_btn_input_velocity_counter_clock_wise.pressed.connect(
            self.axis1_input_velocity_counter_clock_wise_pressed)
        self.axis1_btn_input_velocity_stop = QPushButton()
        self.axis1_btn_input_velocity_stop.setDisabled(True)
        self.axis1_btn_input_velocity_stop.pressed.connect(
            self.axis1_input_velocity_stop_pressed)
        self.axis1_btn_input_velocity_clock_wise.setIcon(self.icon_forward)
        self.axis1_btn_input_velocity_counter_clock_wise.setIcon(
            self.icon_backward)
        self.axis1_btn_input_velocity_stop.setIcon(self.icon_stop)
        self.axis1_radio_input_position = QRadioButton('Position (Turns)')
        self.axis1_radio_input_position.setChecked(True)
        self.axis1_spin_input_position = QSpinBox()
        self.axis1_spin_input_position.setMinimum(-10000)
        self.axis1_spin_input_position.setMaximum(10000)
        self.axis1_spin_input_position.setValue(0)
        self.axis1_btn_input_position = QPushButton('GO')
        self.axis1_btn_input_position.pressed.connect(
            self.axis1_input_position_pressed)
        self.axis1_radio_input_group = QButtonGroup()
        self.axis1_radio_input_group.addButton(self.axis1_radio_input_torque)
        self.axis1_radio_input_group.addButton(self.axis1_radio_input_velocity)
        self.axis1_radio_input_group.addButton(self.axis1_radio_input_position)
        self.axis1_radio_input_group.buttonClicked.connect(
            self.axis1_controller_mode_changed)

        axis1_input_gird.addWidget(self.axis1_radio_input_torque, 0, 0)
        axis1_input_gird.addWidget(self.axis1_spin_input_torque, 0, 1)
        axis1_input_gird.addWidget(
            self.axis1_btn_input_torque_counter_clock_wise, 0, 2)
        axis1_input_gird.addWidget(self.axis1_btn_input_torque_stop, 0, 3)
        axis1_input_gird.addWidget(self.axis1_btn_input_torque_clock_wise, 0, 4)
        axis1_input_gird.addWidget(self.axis1_radio_input_velocity, 1, 0)
        axis1_input_gird.addWidget(self.axis1_spin_input_velocity, 1, 1)
        axis1_input_gird.addWidget(
            self.axis1_btn_input_velocity_counter_clock_wise, 1, 2)
        axis1_input_gird.addWidget(self.axis1_btn_input_velocity_stop, 1, 3)
        axis1_input_gird.addWidget(
            self.axis1_btn_input_velocity_clock_wise, 1, 4)
        axis1_input_gird.addWidget(self.axis1_radio_input_position, 2, 0)
        axis1_input_gird.addWidget(self.axis1_spin_input_position, 2, 1)
        axis1_input_gird.addWidget(self.axis1_btn_input_position, 2, 2, 1, 3)

        self.axis1_group = QGroupBox('Axis1')
        axis1_v_box = QVBoxLayout()
        axis1_v_box.addWidget(self.axis1_state_group)
        axis1_v_box.addWidget(self.axis1_input_mode_group)
        axis1_v_box.addLayout(axis1_input_gird)
        self.axis1_group.setLayout(axis1_v_box)

        input_v_box = QVBoxLayout()
        input_v_box.addWidget(self.axis0_group)
        input_v_box.addWidget(self.axis1_group)

        self.legend = QGroupBox()
        legend_h_box = QHBoxLayout()
        self.axis0_legend_check = QCheckBox('Axis0:')
        self.axis0_legend_check.setChecked(True)
        self.axis0_legend_check.stateChanged.connect(
            self.axis0_graph_state_changed)
        self.axis0_set_point_label = QLabel('Setpoint')
        self.axis0_set_point_color = QLabel()
        self.axis0_set_point_color.setPixmap(QPixmap('resources/line_blue.png'))
        self.axis0_estimate_label = QLabel('Estimate')
        self.axis0_estimate_color = QLabel()
        self.axis0_estimate_color.setPixmap(QPixmap(
            'resources/line_purple.png'))
        spacer = QSpacerItem(30, 1)
        self.axis1_legend_check = QCheckBox('Axis1:')
        self.axis1_legend_check.setChecked(True)
        self.axis1_legend_check.stateChanged.connect(
            self.axis1_graph_state_changed)
        self.axis1_set_point_label = QLabel('Setpoint')
        self.axis1_set_point_color = QLabel()
        self.axis1_set_point_color.setPixmap(QPixmap(
            'resources/line_orange.png'))
        self.axis1_estimate_label = QLabel('Estimate')
        self.axis1_estimate_color = QLabel()
        self.axis1_estimate_color.setPixmap(QPixmap(
            'resources/line_yellow.png'))
        legend_h_box.addWidget(self.axis0_legend_check)
        legend_h_box.addWidget(self.axis0_set_point_label)
        legend_h_box.addWidget(self.axis0_set_point_color)
        legend_h_box.addWidget(self.axis0_estimate_label)
        legend_h_box.addWidget(self.axis0_estimate_color)
        legend_h_box.addSpacerItem(spacer)
        legend_h_box.addWidget(self.axis1_legend_check)
        legend_h_box.addWidget(self.axis1_set_point_label)
        legend_h_box.addWidget(self.axis1_set_point_color)
        legend_h_box.addWidget(self.axis1_estimate_label)
        legend_h_box.addWidget(self.axis1_estimate_color)
        self.legend.setLayout(legend_h_box)

        self.config = QGroupBox()
        config_h_box = QHBoxLayout()
        self.config_btn_connect = QPushButton()
        self.config_btn_connect.setMaximumWidth(30)
        if self.online:
            self.config_btn_connect.setIcon(self.icon_connect)
        else:
            self.config_btn_connect.setIcon(self.icon_disconnect)
        self.config_btn_connect.clicked.connect(self.odrive_connect)
        self.config_btn_language = QPushButton()
        self.config_btn_language.setMaximumWidth(30)
        self.config_btn_language.setIcon(self.icon_chinese)
        self.config_btn_setup = QPushButton()
        self.config_btn_setup.setMaximumWidth(30)
        self.config_btn_setup.setIcon(self.icon_setup)
        self.config_btn_setup.clicked.connect(self.config_clicked)
        config_h_box.addWidget(self.config_btn_connect)
        config_h_box.addWidget(self.config_btn_language)
        config_h_box.addWidget(self.config_btn_setup)
        self.config.setLayout(config_h_box)

        self.op = QGroupBox()
        op_h_box = QHBoxLayout()
        self.op_btn_start = QPushButton()
        self.op_btn_start.setMaximumWidth(30)
        self.op_btn_start.setIcon(self.icon_start)
        self.op_btn_start.clicked.connect(self.op_start_clicked)
        self.op_btn_record = QPushButton()
        self.op_btn_record.setMaximumWidth(30)
        self.op_btn_record.setIcon(self.icon_record)
        self.op_btn_record.clicked.connect(self.op_record_clicked)
        self.op_btn_clean = QPushButton()
        self.op_btn_clean.setMaximumWidth(30)
        self.op_btn_clean.setIcon(self.icon_clean)
        self.op_btn_clean.clicked.connect(self.op_clean_clicked)
        op_h_box.addWidget(self.op_btn_start)
        op_h_box.addWidget(self.op_btn_record)
        op_h_box.addWidget(self.op_btn_clean)
        self.op.setLayout(op_h_box)

        header_h_box = QHBoxLayout()
        header_h_box.addWidget(self.legend)
        header_h_box.addWidget(self.op)
        header_h_box.addWidget(self.config)

        plot_v_box = QVBoxLayout()
        self.plot_velocity = PlotWidget()
        self.plot_velocity.setStyleSheet('')
        self.plot_velocity.setLabel('bottom', 'Time', 's')
        self.plot_velocity.setLabel('left', 'Velocity', 'rpm')
        self.plot_velocity.setTitle('Velocity')

        self.plot_current = PlotWidget()
        self.plot_current.setMinimumSize(QSize(900, 0))
        self.plot_current.setLabel('bottom', 'Time', 's')
        self.plot_current.setLabel('left', 'Current', 'Iq')
        self.plot_current.setTitle('Current')

        self.plot_position = PlotWidget()
        self.plot_position.setLabel('bottom', 'Time', 's')
        self.plot_position.setLabel('left', 'Position', 'counts')
        self.plot_position.setTitle('Position')

        plot_v_box.addWidget(self.plot_velocity)
        plot_v_box.addWidget(self.plot_current)
        plot_v_box.addWidget(self.plot_position)

        process_op_v_box = QVBoxLayout()
        self.process_btn_up = QPushButton()
        self.process_btn_up.setMaximumWidth(20)
        self.process_btn_up.setMaximumHeight(20)
        self.process_btn_up.setIcon(self.icon_up)
        self.process_btn_up.clicked.connect(self.process_msg_up)
        self.process_btn_down = QPushButton()
        self.process_btn_down.setMaximumWidth(20)
        self.process_btn_down.setMaximumHeight(20)
        self.process_btn_down.setIcon(self.icon_down)
        self.process_btn_down.clicked.connect(self.process_msg_down)
        self.process_btn_clear = QPushButton()
        self.process_btn_clear.setMaximumWidth(20)
        self.process_btn_clear.setMaximumHeight(20)
        self.process_btn_clear.setIcon(self.icon_clean)
        self.process_btn_clear.clicked.connect(self.process_msg_clear)
        process_op_v_box.addWidget(self.process_btn_up)
        process_op_v_box.addWidget(self.process_btn_down)
        process_op_v_box.addWidget(self.process_btn_clear)
        process_op_v_box.addStretch()

        process_h_box = QHBoxLayout()
        self.process = QTextEdit(self, readOnly=True)
        self.process.ensureCursorVisible()
        process_h_box.addLayout(process_op_v_box)
        process_h_box.addWidget(self.process)

        graph_v_box = QVBoxLayout()
        graph_v_box.addLayout(header_h_box)
        graph_v_box.addLayout(plot_v_box)
        graph_v_box.addLayout(process_h_box)

        main_h_box = QHBoxLayout()
        main_h_box.addLayout(input_v_box)
        main_h_box.addLayout(graph_v_box)
        self.setLayout(main_h_box)

        self.axis_dict['axis0'] = {}
        self.axis_dict['axis0']['time_array'] = []
        self.axis_dict['axis0']['position'] = {}
        self.axis_dict['axis0']['position']['estimate'] = []
        self.axis_dict['axis0']['position']['set_point'] = []
        self.axis_dict['axis0']['velocity'] = {}
        self.axis_dict['axis0']['velocity']['estimate'] = []
        self.axis_dict['axis0']['velocity']['set_point'] = []
        self.axis_dict['axis0']['current'] = {}
        self.axis_dict['axis0']['current']['estimate'] = []
        self.axis_dict['axis0']['current']['set_point'] = []
        self.axis_dict['axis0']['vel_sp_curve'] = self.plot_velocity.plot(
            name='Setpoint', pen=pen_sp_axis0)
        self.axis_dict['axis0']['vel_est_curve'] = self.plot_velocity.plot(
            name='Estimate', pen=pen_est_axis0)
        self.axis_dict['axis0']['pos_sp_curve'] = self.plot_position.plot(
            name='Setpoint', pen=pen_sp_axis0)
        self.axis_dict['axis0']['pos_est_curve'] = self.plot_position.plot(
            name='Estimate', pen=pen_est_axis0)
        self.axis_dict['axis0']['current_sp_curve'] = self.plot_current.plot(
            name='Setpoint', pen=pen_sp_axis0)
        self.axis_dict['axis0']['current_est_curve'] = self.plot_current.plot(
            name='Estimate', pen=pen_est_axis0)
        self.axis_dict['axis1'] = {}
        self.axis_dict['axis1']['time_array'] = []
        self.axis_dict['axis1']['position'] = {}
        self.axis_dict['axis1']['position']['estimate'] = []
        self.axis_dict['axis1']['position']['set_point'] = []
        self.axis_dict['axis1']['velocity'] = {}
        self.axis_dict['axis1']['velocity']['estimate'] = []
        self.axis_dict['axis1']['velocity']['set_point'] = []
        self.axis_dict['axis1']['current'] = {}
        self.axis_dict['axis1']['current']['estimate'] = []
        self.axis_dict['axis1']['current']['set_point'] = []
        self.axis_dict['axis1']['vel_sp_curve'] = self.plot_velocity.plot(
            name='Setpoint', pen=pen_sp_axis1)
        self.axis_dict['axis1']['vel_est_curve'] = self.plot_velocity.plot(
            name='Estimate', pen=pen_est_axis1)
        self.axis_dict['axis1']['pos_sp_curve'] = self.plot_position.plot(
            name='Setpoint', pen=pen_sp_axis1)
        self.axis_dict['axis1']['pos_est_curve'] = self.plot_position.plot(
            name='Estimate', pen=pen_est_axis1)
        self.axis_dict['axis1']['current_sp_curve'] = self.plot_current.plot(
            name='Setpoint', pen=pen_sp_axis1)
        self.axis_dict['axis1']['current_est_curve'] = self.plot_current.plot(
            name='Estimate', pen=pen_est_axis1)

    def axis0_state_idle_clicked(self):
        self.drive.axis0.requested_state = AXIS_STATE_IDLE

    def axis0_state_startup_sequence_clicked(self):
        self.drive.axis0.requested_state = AXIS_STATE_STARTUP_SEQUENCE

    def axis0_state_full_calibration_sequence_clicked(self):
        self.drive.axis0.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE

    def axis0_state_motor_calibration_clicked(self):
        self.drive.axis0.requested_state = AXIS_STATE_MOTOR_CALIBRATION

    def axis0_state_encoder_index_search_clicked(self):
        self.drive.axis0.requested_state = AXIS_STATE_ENCODER_INDEX_SEARCH

    def axis0_state_encoder_offset_calibration_clicked(self):
        self.drive.axis0.requested_state = AXIS_STATE_ENCODER_OFFSET_CALIBRATION

    def axis0_state_closed_loop_control_clicked(self):
        self.drive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

    def axis0_state_lockin_spin_clicked(self):
        self.drive.axis0.requested_state = AXIS_STATE_LOCKIN_SPIN

    def axis0_state_encoder_dir_find_clicked(self):
        self.drive.axis0.requested_state = AXIS_STATE_ENCODER_DIR_FIND

    def axis0_state_homing_clicked(self):
        self.drive.axis0.requested_state = AXIS_STATE_HOMING

    def axis0_state_encoder_hall_polarity_calibration_clicked(self):
        self.drive.axis0.requested_state = \
            AXIS_STATE_ENCODER_HALL_POLARITY_CALIBRATION

    def axis0_state_encoder_hall_phase_calibration_clicked(self):
        self.drive.axis0.requested_state = \
            AXIS_STATE_ENCODER_HALL_PHASE_CALIBRATION

    def axis1_state_idle_clicked(self):
        self.drive.axis1.requested_state = AXIS_STATE_IDLE

    def axis1_state_startup_sequence_clicked(self):
        self.drive.axis1.requested_state = AXIS_STATE_STARTUP_SEQUENCE

    def axis1_state_full_calibration_sequence_clicked(self):
        self.drive.axis1.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE

    def axis1_state_motor_calibration_clicked(self):
        self.drive.axis1.requested_state = AXIS_STATE_MOTOR_CALIBRATION

    def axis1_state_encoder_index_search_clicked(self):
        self.drive.axis1.requested_state = AXIS_STATE_ENCODER_INDEX_SEARCH

    def axis1_state_encoder_offset_calibration_clicked(self):
        self.drive.axis1.requested_state = AXIS_STATE_ENCODER_OFFSET_CALIBRATION

    def axis1_state_closed_loop_control_clicked(self):
        self.drive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

    def axis1_state_lockin_spin_clicked(self):
        self.drive.axis1.requested_state = AXIS_STATE_LOCKIN_SPIN

    def axis1_state_encoder_dir_find_clicked(self):
        self.drive.axis1.requested_state = AXIS_STATE_ENCODER_DIR_FIND

    def axis1_state_homing_clicked(self):
        self.drive.axis1.requested_state = AXIS_STATE_HOMING

    def axis1_state_encoder_hall_polarity_calibration_clicked(self):
        self.drive.axis1.requested_state = \
            AXIS_STATE_ENCODER_HALL_POLARITY_CALIBRATION

    def axis1_state_encoder_hall_phase_calibration_clicked(self):
        self.drive.axis1.requested_state = \
            AXIS_STATE_ENCODER_HALL_PHASE_CALIBRATION

    def axis0_input_mode_pass_through_clicked(self):
        self.drive.axis0.controller.config.input_mode = INPUT_MODE_PASSTHROUGH

    def axis0_input_mode_vel_ramp_clicked(self):
        self.drive.axis0.controller.config.input_mode = INPUT_MODE_VEL_RAMP

    def axis0_input_mode_pos_filter_clicked(self):
        self.drive.axis0.controller.config.input_mode = INPUT_MODE_POS_FILTER

    def axis0_input_mode_mix_channels_clicked(self):
        self.drive.axis0.controller.config.input_mode = INPUT_MODE_MIX_CHANNELS

    def axis0_input_mode_trap_traj_clicked(self):
        self.drive.axis0.controller.config.input_mode = INPUT_MODE_TRAP_TRAJ

    def axis0_input_mode_troque_ramp_clicked(self):
        self.drive.axis0.controller.config.input_mode = INPUT_MODE_TORQUE_RAMP

    def axis0_input_mode_mirror_clicked(self):
        self.drive.axis0.controller.config.input_mode = INPUT_MODE_MIRROR

    def axis0_input_mode_tuning_clicked(self):
        self.drive.axis0.controller.config.input_mode = INPUT_MODE_TUNING

    def axis1_input_mode_pass_through_clicked(self):
        self.drive.axis1.controller.config.input_mode = INPUT_MODE_PASSTHROUGH

    def axis1_input_mode_vel_ramp_clicked(self):
        self.drive.axis1.controller.config.input_mode = INPUT_MODE_VEL_RAMP

    def axis1_input_mode_pos_filter_clicked(self):
        self.drive.axis1.controller.config.input_mode = INPUT_MODE_POS_FILTER

    def axis1_input_mode_mix_channels_clicked(self):
        self.drive.axis1.controller.config.input_mode = INPUT_MODE_MIX_CHANNELS

    def axis1_input_mode_trap_traj_clicked(self):
        self.drive.axis1.controller.config.input_mode = INPUT_MODE_TRAP_TRAJ

    def axis1_input_mode_troque_ramp_clicked(self):
        self.drive.axis1.controller.config.input_mode = INPUT_MODE_TORQUE_RAMP

    def axis1_input_mode_mirror_clicked(self):
        self.drive.axis1.controller.config.input_mode = INPUT_MODE_MIRROR

    def axis1_input_mode_tuning_clicked(self):
        self.drive.axis1.controller.config.input_mode = INPUT_MODE_TUNING

    def axis0_input_torque_clock_wise_pressed(self):
        value = self.axis0_spin_input_torque.value()
        exec_string = 'self.drive.axis0.controller.input_torque = {}'.format(
            value)
        exec(exec_string)

    def axis0_input_torque_counter_clock_wise_pressed(self):
        value = self.axis0_spin_input_torque.value() * -1
        exec_string = 'self.drive.axis0.controller.input_torque = {}'.format(
            value)
        exec(exec_string)

    def axis0_input_torque_stop_pressed(self):
        exec_string = 'self.drive.axis0.controller.input_torque = 0'
        exec(exec_string)

    def axis1_input_torque_clock_wise_pressed(self):
        value = self.axis1_spin_input_torque.value()
        exec_string = 'self.drive.axis1.controller.input_torque = {}'.format(
            value)
        exec(exec_string)

    def axis1_input_torque_counter_clock_wise_pressed(self):
        value = self.axis1_spin_input_torque.value() * -1
        exec_string = 'self.drive.axis1.controller.input_torque = {}'.format(
            value)
        exec(exec_string)

    def axis1_input_torque_stop_pressed(self):
        exec_string = 'self.drive.axis1.controller.input_torque = 0'
        exec(exec_string)

    def axis0_input_velocity_clock_wise_pressed(self):
        value = self.axis0_spin_input_velocity.value()
        exec_string = 'self.drive.axis0.controller.input_vel = {}'.format(value)
        exec(exec_string)

    def axis0_input_velocity_counter_clock_wise_pressed(self):
        value = self.axis0_spin_input_velocity.value() * -1
        exec_string = 'self.drive.axis0.controller.input_vel = {}'.format(value)
        exec(exec_string)

    def axis0_input_velocity_stop_pressed(self):
        exec_string = 'self.drive.axis0.controller.input_vel = 0'
        exec(exec_string)

    def axis1_input_velocity_clock_wise_pressed(self):
        value = self.axis1_spin_input_velocity.value()
        exec_string = 'self.drive.axis1.controller.input_vel = {}'.format(value)
        exec(exec_string)

    def axis1_input_velocity_counter_clock_wise_pressed(self):
        value = self.axis1_spin_input_velocity.value() * -1
        exec_string = 'self.drive.axis1.controller.input_vel = {}'.format(value)
        exec(exec_string)

    def axis1_input_velocity_stop_pressed(self):
        exec_string = 'self.drive.axis1.controller.input_vel = 0'
        exec(exec_string)

    def axis0_input_position_pressed(self):
        value = self.axis0_spin_input_position.value()
        exec_string = 'self.drive.axis0.controller.input_pos = {}'.format(value)
        exec(exec_string)

    def axis1_input_position_pressed(self):
        value = self.axis1_spin_input_position.value()
        exec_string = 'self.drive.axis1.controller.input_pos = {}'.format(value)
        exec(exec_string)

    def axis0_controller_mode_changed(self):
        self.disable_axis0_input_buttons()
        if self.axis0_radio_input_torque.isChecked():
            self.axis0_btn_input_torque_clock_wise.setEnabled(True)
            self.axis0_btn_input_torque_counter_clock_wise.setEnabled(True)
            self.axis0_btn_input_torque_stop.setEnabled(True)
            self.drive.axis0.controller.config.control_mode = \
                CONTROL_MODE_TORQUE_CONTROL
        elif self.axis0_radio_input_velocity.isChecked():
            self.axis0_btn_input_velocity_clock_wise.setEnabled(True)
            self.axis0_btn_input_velocity_counter_clock_wise.setEnabled(True)
            self.axis0_btn_input_velocity_stop.setEnabled(True)
            self.drive.axis0.controller.config.control_mode = \
                CONTROL_MODE_VELOCITY_CONTROL
        elif self.axis0_radio_input_position.isChecked():
            self.axis0_btn_input_position.setEnabled(True)
            self.drive.axis0.controller.config.control_mode = \
                CONTROL_MODE_POSITION_CONTROL

    def disable_axis0_input_buttons(self):
        self.axis0_btn_input_torque_clock_wise.setDisabled(True)
        self.axis0_btn_input_torque_counter_clock_wise.setDisabled(True)
        self.axis0_btn_input_torque_stop.setDisabled(True)
        self.axis0_btn_input_velocity_clock_wise.setDisabled(True)
        self.axis0_btn_input_velocity_counter_clock_wise.setDisabled(True)
        self.axis0_btn_input_velocity_stop.setDisabled(True)
        self.axis0_btn_input_position.setDisabled(True)

    def axis1_controller_mode_changed(self):
        self.disable_axis1_input_buttons()
        if self.axis1_radio_input_torque.isChecked():
            self.axis1_btn_input_torque_clock_wise.setEnabled(True)
            self.axis1_btn_input_torque_counter_clock_wise.setEnabled(True)
            self.axis1_btn_input_torque_stop.setEnabled(True)
            self.drive.axis1.controller.config.control_mode = \
                CONTROL_MODE_TORQUE_CONTROL
        elif self.axis1_radio_input_velocity.isChecked():
            self.axis1_btn_input_velocity_clock_wise.setEnabled(True)
            self.axis1_btn_input_velocity_counter_clock_wise.setEnabled(True)
            self.axis1_btn_input_velocity_stop.setEnabled(True)
            self.drive.axis1.controller.config.control_mode = \
                CONTROL_MODE_VELOCITY_CONTROL
        elif self.axis1_radio_input_position.isChecked():
            self.axis1_btn_input_position.setEnabled(True)
            self.drive.axis1.controller.config.control_mode = \
                CONTROL_MODE_POSITION_CONTROL

    def disable_axis1_input_buttons(self):
        self.axis1_btn_input_torque_clock_wise.setDisabled(True)
        self.axis1_btn_input_torque_counter_clock_wise.setDisabled(True)
        self.axis1_btn_input_torque_stop.setDisabled(True)
        self.axis1_btn_input_velocity_clock_wise.setDisabled(True)
        self.axis1_btn_input_velocity_counter_clock_wise.setDisabled(True)
        self.axis1_btn_input_velocity_stop.setDisabled(True)
        self.axis1_btn_input_position.setDisabled(True)

    def op_start_clicked(self):
        if not self.online:
            QMessageBox.information(self, 'Info', 'Connect drive first!',
                                    QMessageBox.Ok, QMessageBox.Ok)
            return
        if not self.play:
            self.play = True
            self.op_btn_start.setIcon(self.icon_stop)

            self.timer_state = pg.QtCore.QTimer()
            self.timer_state.timeout.connect(self.update_states)
            # TODO: Should I put it into odrive.conf?
            self.timer_state.start(STATE_UPDATING_PERIOD)

            self.axis_dict['start_time'] = pg.ptime.time()
            self.timer_graph = pg.QtCore.QTimer()
            self.timer_graph.timeout.connect(self.update_graphs)
            self.timer_graph.start(self.sampling_period)
        else:
            self.play = False
            self.op_btn_start.setIcon(self.icon_start)

            self.timer_state.stop()
            self.timer_graph.stop()

    def op_record_clicked(self):
        # TODO: Save the `wave` to files
        if not self.record:
            self.record = True
            self.op_btn_record.setIcon(self.icon_record_stop)
        else:
            self.record = False
            self.op_btn_record.setIcon(self.icon_record)

    def op_clean_clicked(self):
        self.clear_axis_graph_lists('axis0')
        self.clear_axis_graph_lists('axis1')
        self.axis_dict['start_time'] = pg.ptime.time()

    def clear_axis_graph_lists(self, axis_key):
        self.axis_dict[axis_key]['time_array'] = []
        self.axis_dict[axis_key]['velocity']['set_point'] = []
        self.axis_dict[axis_key]['velocity']['estimate'] = []
        self.axis_dict[axis_key]['current']['set_point'] = []
        self.axis_dict[axis_key]['current']['estimate'] = []
        self.axis_dict[axis_key]['position']['set_point'] = []
        self.axis_dict[axis_key]['position']['estimate'] = []
        self.axis_dict[axis_key]['vel_sp_curve'].setData([], [])
        self.axis_dict[axis_key]['vel_est_curve'].setData([], [])
        self.axis_dict[axis_key]['current_sp_curve'].setData([], [])
        self.axis_dict[axis_key]['current_est_curve'].setData([], [])
        self.axis_dict[axis_key]['pos_sp_curve'].setData([], [])
        self.axis_dict[axis_key]['pos_est_curve'].setData([], [])

    def axis0_graph_state_changed(self, state):
        if state != Qt.Checked:
            self.clear_axis_graph_lists('axis0')
        self.axis_graph_state_changed()

    def axis1_graph_state_changed(self, state):
        if state != Qt.Checked:
            self.clear_axis_graph_lists('axis1')
        self.axis_graph_state_changed()

    def axis_graph_state_changed(self):
        axis0_state = self.axis0_legend_check.isChecked()
        axis1_state = self.axis1_legend_check.isChecked()
        if not axis0_state and not axis1_state:
            self.timer_graph.stop()
            # TODO: Clear graphs, call clear_axis_graph_lists()?
        else:
            if not self.timer_graph.isActive():
                self.timer_graph.start(self.sampling_period)
                self.axis_dict['start_time'] = pg.ptime.time()

    def update_states(self):
        try:
            self.update_machine_state()
            self.update_input_mode_state()
            self.update_controller_mode()
            self.update_process_msg()
        except Exception as e:
            print(e)

    def update_machine_state(self):
        axis0_current_state = self.drive.axis0.current_state
        if self.axis0_state != axis0_current_state:
            self.axis0_state = axis0_current_state
            self.update_machine_axis0_state_color(axis0_current_state)

        axis1_current_state = self.drive.axis1.current_state
        if self.axis1_state != axis1_current_state:
            self.axis1_state = axis1_current_state
            self.update_machine_axis1_state_color(axis1_current_state)

    def update_machine_axis0_state_color(self, current_state):
        self.clear_axis0_state_buttons()
        color = BUTTON_CHANGED_COLOR
        if current_state == AXIS_STATE_IDLE:
            self.axis0_btn_state_idle.setStyleSheet(color)
        elif current_state == AXIS_STATE_STARTUP_SEQUENCE:
            self.axis0_btn_state_startup_sequence.setStyleSheet(color)
        elif current_state == AXIS_STATE_FULL_CALIBRATION_SEQUENCE:
            self.axis0_btn_state_full_calibration_sequence.setStyleSheet(color)
        elif current_state == AXIS_STATE_MOTOR_CALIBRATION:
            self.axis0_btn_state_motor_calibration.setStyleSheet(color)
        elif current_state == AXIS_STATE_ENCODER_INDEX_SEARCH:
            self.axis0_btn_state_encoder_index_search.setStyleSheet(color)
        elif current_state == AXIS_STATE_ENCODER_OFFSET_CALIBRATION:
            self.axis0_btn_state_encoder_offset_calibration.setStyleSheet(color)
        elif current_state == AXIS_STATE_CLOSED_LOOP_CONTROL:
            self.axis0_btn_state_closed_loop_control.setStyleSheet(color)
        elif current_state == AXIS_STATE_LOCKIN_SPIN:
            self.axis0_btn_state_lockin_spin.setStyleSheet(color)
        elif current_state == AXIS_STATE_ENCODER_DIR_FIND:
            self.axis0_btn_state_encoder_dir_find.setStyleSheet(color)
        elif current_state == AXIS_STATE_HOMING:
            self.axis0_btn_state_homing.setStyleSheet(color)
        elif current_state == AXIS_STATE_ENCODER_HALL_POLARITY_CALIBRATION:
            self.axis0_btn_state_encoder_hall_polarity_calibration.setStyleSheet(
                color)
        elif current_state == AXIS_STATE_ENCODER_HALL_PHASE_CALIBRATION:
            self.axis0_btn_state_encoder_hall_phase_calibration.setStyleSheet(
                color)

    def clear_axis0_state_buttons(self):
        self.axis0_btn_state_idle.setStyleSheet('')
        self.axis0_btn_state_startup_sequence.setStyleSheet('')
        self.axis0_btn_state_full_calibration_sequence.setStyleSheet('')
        self.axis0_btn_state_motor_calibration.setStyleSheet('')
        self.axis0_btn_state_encoder_index_search.setStyleSheet('')
        self.axis0_btn_state_encoder_offset_calibration.setStyleSheet('')
        self.axis0_btn_state_closed_loop_control.setStyleSheet('')
        self.axis0_btn_state_lockin_spin.setStyleSheet('')
        self.axis0_btn_state_encoder_dir_find.setStyleSheet('')
        self.axis0_btn_state_homing.setStyleSheet('')
        self.axis0_btn_state_encoder_hall_polarity_calibration.setStyleSheet('')
        self.axis0_btn_state_encoder_hall_phase_calibration.setStyleSheet('')

    def update_machine_axis1_state_color(self, current_state):
        self.clear_axis1_state_buttons()
        color = BUTTON_CHANGED_COLOR
        if current_state == AXIS_STATE_IDLE:
            self.axis1_btn_state_idle.setStyleSheet(color)
        elif current_state == AXIS_STATE_STARTUP_SEQUENCE:
            self.axis1_btn_state_startup_sequence.setStyleSheet(color)
        elif current_state == AXIS_STATE_FULL_CALIBRATION_SEQUENCE:
            self.axis1_btn_state_full_calibration_sequence.setStyleSheet(color)
        elif current_state == AXIS_STATE_MOTOR_CALIBRATION:
            self.axis1_btn_state_motor_calibration.setStyleSheet(color)
        elif current_state == AXIS_STATE_ENCODER_INDEX_SEARCH:
            self.axis1_btn_state_encoder_index_search.setStyleSheet(color)
        elif current_state == AXIS_STATE_ENCODER_OFFSET_CALIBRATION:
            self.axis1_btn_state_encoder_offset_calibration.setStyleSheet(color)
        elif current_state == AXIS_STATE_CLOSED_LOOP_CONTROL:
            self.axis1_btn_state_closed_loop_control.setStyleSheet(color)
        elif current_state == AXIS_STATE_LOCKIN_SPIN:
            self.axis1_btn_state_lockin_spin.setStyleSheet(color)
        elif current_state == AXIS_STATE_ENCODER_DIR_FIND:
            self.axis1_btn_state_encoder_dir_find.setStyleSheet(color)
        elif current_state == AXIS_STATE_HOMING:
            self.axis1_btn_state_homing.setStyleSheet(color)
        elif current_state == AXIS_STATE_ENCODER_HALL_POLARITY_CALIBRATION:
            self.axis1_btn_state_encoder_hall_polarity_calibration.setStyleSheet(
                color)
        elif current_state == AXIS_STATE_ENCODER_HALL_PHASE_CALIBRATION:
            self.axis1_btn_state_encoder_hall_phase_calibration.setStyleSheet(
                color)

    def clear_axis1_state_buttons(self):
        self.axis1_btn_state_idle.setStyleSheet('')
        self.axis1_btn_state_startup_sequence.setStyleSheet('')
        self.axis1_btn_state_full_calibration_sequence.setStyleSheet('')
        self.axis1_btn_state_motor_calibration.setStyleSheet('')
        self.axis1_btn_state_encoder_index_search.setStyleSheet('')
        self.axis1_btn_state_encoder_offset_calibration.setStyleSheet('')
        self.axis1_btn_state_closed_loop_control.setStyleSheet('')
        self.axis1_btn_state_lockin_spin.setStyleSheet('')
        self.axis1_btn_state_encoder_dir_find.setStyleSheet('')
        self.axis1_btn_state_homing.setStyleSheet('')
        self.axis1_btn_state_encoder_hall_polarity_calibration.setStyleSheet('')
        self.axis1_btn_state_encoder_hall_phase_calibration.setStyleSheet('')

    def update_input_mode_state(self):
        axis0_current_input_mode = self.drive.axis0.controller.config.input_mode
        if self.axis0_current_input_mode != axis0_current_input_mode:
            self.axis0_current_input_mode = axis0_current_input_mode
            self.update_axis0_input_mode_color(axis0_current_input_mode)

        axis1_current_input_mode = self.drive.axis1.controller.config.input_mode
        if self.axis1_current_input_mode != axis1_current_input_mode:
            self.axis1_current_input_mode = axis1_current_input_mode
            self.update_axis1_input_mode_color(axis1_current_input_mode)

    def update_axis0_input_mode_color(self, current_input_mode):
        self.clear_axis0_input_mode_buttons()
        color = BUTTON_CHANGED_COLOR
        if current_input_mode == INPUT_MODE_PASSTHROUGH:
            self.axis0_btn_input_mode_pass_through.setStyleSheet(color)
        elif current_input_mode == INPUT_MODE_VEL_RAMP:
            self.axis0_btn_input_mode_vel_ramp.setStyleSheet(color)
        elif current_input_mode == INPUT_MODE_POS_FILTER:
            self.axis0_btn_input_mode_pos_filter.setStyleSheet(color)
        elif current_input_mode == INPUT_MODE_MIX_CHANNELS:
            self.axis0_btn_input_mode_mix_channels.setStyleSheet(color)
        elif current_input_mode == INPUT_MODE_TRAP_TRAJ:
            self.axis0_btn_input_mode_trap_traj.setStyleSheet(color)
        elif current_input_mode == INPUT_MODE_TORQUE_RAMP:
            self.axis0_btn_input_mode_troque_ramp.setStyleSheet(color)
        elif current_input_mode == INPUT_MODE_MIRROR:
            self.axis0_btn_input_mode_mirror.setStyleSheet(color)
        elif current_input_mode == INPUT_MODE_TUNING:
            self.axis0_btn_input_mode_tuning.setStyleSheet(color)

    def clear_axis0_input_mode_buttons(self):
        self.axis0_btn_input_mode_pass_through.setStyleSheet('')
        self.axis0_btn_input_mode_vel_ramp.setStyleSheet('')
        self.axis0_btn_input_mode_pos_filter.setStyleSheet('')
        self.axis0_btn_input_mode_mix_channels.setStyleSheet('')
        self.axis0_btn_input_mode_trap_traj.setStyleSheet('')
        self.axis0_btn_input_mode_troque_ramp.setStyleSheet('')
        self.axis0_btn_input_mode_mirror.setStyleSheet('')
        self.axis0_btn_input_mode_tuning.setStyleSheet('')

    def update_axis1_input_mode_color(self, current_input_mode):
        self.clear_axis1_input_mode_buttons()
        color = BUTTON_CHANGED_COLOR
        if current_input_mode == INPUT_MODE_PASSTHROUGH:
            self.axis1_btn_input_mode_pass_through.setStyleSheet(color)
        elif current_input_mode == INPUT_MODE_VEL_RAMP:
            self.axis1_btn_input_mode_vel_ramp.setStyleSheet(color)
        elif current_input_mode == INPUT_MODE_POS_FILTER:
            self.axis1_btn_input_mode_pos_filter.setStyleSheet(color)
        elif current_input_mode == INPUT_MODE_MIX_CHANNELS:
            self.axis1_btn_input_mode_mix_channels.setStyleSheet(color)
        elif current_input_mode == INPUT_MODE_TRAP_TRAJ:
            self.axis1_btn_input_mode_trap_traj.setStyleSheet(color)
        elif current_input_mode == INPUT_MODE_TORQUE_RAMP:
            self.axis1_btn_input_mode_troque_ramp.setStyleSheet(color)
        elif current_input_mode == INPUT_MODE_MIRROR:
            self.axis1_btn_input_mode_mirror.setStyleSheet(color)
        elif current_input_mode == INPUT_MODE_TUNING:
            self.axis1_btn_input_mode_tuning.setStyleSheet(color)

    def clear_axis1_input_mode_buttons(self):
        self.axis1_btn_input_mode_pass_through.setStyleSheet('')
        self.axis1_btn_input_mode_vel_ramp.setStyleSheet('')
        self.axis1_btn_input_mode_pos_filter.setStyleSheet('')
        self.axis1_btn_input_mode_mix_channels.setStyleSheet('')
        self.axis1_btn_input_mode_trap_traj.setStyleSheet('')
        self.axis1_btn_input_mode_troque_ramp.setStyleSheet('')
        self.axis1_btn_input_mode_mirror.setStyleSheet('')
        self.axis1_btn_input_mode_tuning.setStyleSheet('')

    def update_controller_mode(self):
        axis0_control_mode = self.drive.axis0.controller.config.control_mode
        if axis0_control_mode == CONTROL_MODE_TORQUE_CONTROL:
            self.axis0_radio_input_torque.setChecked(True)
            self.axis0_controller_fields_position_enabled(
                CONTROL_MODE_TORQUE_CONTROL)
        elif axis0_control_mode == CONTROL_MODE_VELOCITY_CONTROL:
            self.axis0_radio_input_velocity.setChecked(True)
            self.axis0_controller_fields_position_enabled(
                CONTROL_MODE_VELOCITY_CONTROL)
        elif axis0_control_mode == CONTROL_MODE_POSITION_CONTROL:
            self.axis0_radio_input_position.setChecked(True)
            self.axis0_controller_fields_position_enabled(
                CONTROL_MODE_POSITION_CONTROL)

        axis1_control_mode = self.drive.axis1.controller.config.control_mode
        if axis1_control_mode == CONTROL_MODE_TORQUE_CONTROL:
            self.axis1_radio_input_torque.setChecked(True)
            self.axis1_controller_fields_position_enabled(
                CONTROL_MODE_TORQUE_CONTROL)
        elif axis1_control_mode == CONTROL_MODE_VELOCITY_CONTROL:
            self.axis1_radio_input_velocity.setChecked(True)
            self.axis1_controller_fields_position_enabled(
                CONTROL_MODE_VELOCITY_CONTROL)
        elif axis1_control_mode == CONTROL_MODE_POSITION_CONTROL:
            self.axis1_radio_input_position.setChecked(True)
            self.axis1_controller_fields_position_enabled(
                CONTROL_MODE_POSITION_CONTROL)

    def axis0_controller_fields_position_enabled(self, control_mode):
        self.disable_axis0_fields()
        if control_mode == CONTROL_MODE_TORQUE_CONTROL:
            self.axis0_btn_input_torque_clock_wise.setEnabled(True)
            self.axis0_btn_input_torque_counter_clock_wise.setEnabled(True)
            self.axis0_btn_input_torque_stop.setEnabled(True)
        elif control_mode == CONTROL_MODE_VELOCITY_CONTROL:
            self.axis0_btn_input_velocity_clock_wise.setEnabled(True)
            self.axis0_btn_input_velocity_counter_clock_wise.setEnabled(True)
            self.axis0_btn_input_velocity_stop.setEnabled(True)
        elif control_mode == CONTROL_MODE_POSITION_CONTROL:
            self.axis0_btn_input_position.setEnabled(True)

    def disable_axis0_fields(self):
        self.axis0_btn_input_torque_clock_wise.setDisabled(True)
        self.axis0_btn_input_torque_counter_clock_wise.setDisabled(True)
        self.axis0_btn_input_torque_stop.setDisabled(True)
        self.axis0_btn_input_velocity_clock_wise.setDisabled(True)
        self.axis0_btn_input_velocity_counter_clock_wise.setDisabled(True)
        self.axis0_btn_input_velocity_stop.setDisabled(True)
        self.axis0_btn_input_position.setDisabled(True)

    def axis1_controller_fields_position_enabled(self, control_mode):
        self.disable_axis1_fields()
        if control_mode == CONTROL_MODE_TORQUE_CONTROL:
            self.axis1_btn_input_torque_clock_wise.setEnabled(True)
            self.axis1_btn_input_torque_counter_clock_wise.setEnabled(True)
            self.axis1_btn_input_torque_stop.setEnabled(True)
        elif control_mode == CONTROL_MODE_VELOCITY_CONTROL:
            self.axis1_btn_input_velocity_clock_wise.setEnabled(True)
            self.axis1_btn_input_velocity_counter_clock_wise.setEnabled(True)
            self.axis1_btn_input_velocity_stop.setEnabled(True)
        elif control_mode == CONTROL_MODE_POSITION_CONTROL:
            self.axis1_btn_input_position.setEnabled(True)

    def disable_axis1_fields(self):
        self.axis1_btn_input_torque_clock_wise.setDisabled(True)
        self.axis1_btn_input_torque_counter_clock_wise.setDisabled(True)
        self.axis1_btn_input_torque_stop.setDisabled(True)
        self.axis1_btn_input_velocity_clock_wise.setDisabled(True)
        self.axis1_btn_input_velocity_counter_clock_wise.setDisabled(True)
        self.axis1_btn_input_velocity_stop.setDisabled(True)
        self.axis1_btn_input_position.setDisabled(True)

    def update_process_msg(self):
        axis0_message = 'A0: '
        axis1_message = 'A1: '
        axis0_error = check_axis_errors(hex(self.drive.axis0.error)[2:])
        axis1_error = check_axis_errors(hex(self.drive.axis1.error)[2:])
        axis0_encoder_error = check_axis_encoder_errors(
            hex(self.drive.axis0.encoder.error)[2:])
        axis1_encoder_error = check_axis_encoder_errors(
            hex(self.drive.axis1.encoder.error)[2:])
        axis0_motor_error = check_axis_motor_errors(
            hex(self.drive.axis0.motor.error)[2:])
        axis1_motor_error = check_axis_motor_errors(
            hex(self.drive.axis1.motor.error)[2:])

        axis0_error += ', E: '
        axis1_error += ', E: '

        axis0_error += axis0_encoder_error
        axis1_error += axis1_encoder_error

        axis0_error += ', M: '
        axis1_error += ', M: '

        axis0_error += axis0_motor_error
        axis1_error += axis1_motor_error

        axis0_message += axis0_error
        axis1_message += axis1_error

        if 'No errors' not in axis0_message:
            self.process.moveCursor(QTextCursor.End)
            self.process.append(axis0_message)
        if 'No errors' not in axis1_message:
            self.process.moveCursor(QTextCursor.End)
            self.process.append(axis1_message)

    def process_msg_up(self):
        self.process.moveCursor(QTextCursor.Start)

    def process_msg_down(self):
        self.process.moveCursor(QTextCursor.End)

    def process_msg_clear(self):
        self.process.setText('')

    def update_graphs(self):
        data = pg.ptime.time() - self.axis_dict['start_time']
        try:
            if self.axis0_legend_check.isChecked():
                self.axis_dict['axis0']['time_array'].append(data)
                self.update_velocity_graph('axis0', self.drive.axis0)
                self.update_current_graph('axis0', self.drive.axis0)
                self.update_position_graph('axis0', self.drive.axis0)
                self.update_X_range('axis0')
            if self.axis1_legend_check.isChecked():
                self.axis_dict['axis1']['time_array'].append(data)
                self.update_velocity_graph('axis1', self.drive.axis1)
                self.update_current_graph('axis1', self.drive.axis1)
                self.update_position_graph('axis1', self.drive.axis1)
                self.update_X_range('axis1')
        except Exception as e:
            print(e)

    def update_velocity_graph(self, axis_key, axis):
        self.axis_dict[axis_key]['velocity']['estimate'].append(
            axis.encoder.vel_estimate)
        self.axis_dict[axis_key]['velocity']['set_point'].append(
            axis.controller.vel_setpoint)
        self.axis_dict[axis_key]['vel_sp_curve'].setData(
            self.axis_dict[axis_key]['time_array'],
            self.axis_dict[axis_key]['velocity']['set_point'])
        self.axis_dict[axis_key]['vel_est_curve'].setData(
            self.axis_dict[axis_key]['time_array'],
            self.axis_dict[axis_key]['velocity']['estimate'])

    def update_current_graph(self, axis_key, axis):
        self.axis_dict[axis_key]['current']['estimate'].append(
            axis.motor.current_control.Iq_measured)
        self.axis_dict[axis_key]['current']['set_point'].append(
            axis.motor.current_control.Iq_setpoint)
        self.axis_dict[axis_key]['current_sp_curve'].setData(
            self.axis_dict[axis_key]['time_array'],
            self.axis_dict[axis_key]['current']['set_point'])
        self.axis_dict[axis_key]['current_est_curve'].setData(
            self.axis_dict[axis_key]['time_array'],
            self.axis_dict[axis_key]['current']['estimate'])

    def update_position_graph(self, axis_key, odrv_axis):
        self.axis_dict[axis_key]['position']['estimate'].append(
            odrv_axis.encoder.pos_estimate)
        self.axis_dict[axis_key]['position']['set_point'].append(
            odrv_axis.controller.pos_setpoint)
        self.axis_dict[axis_key]['pos_sp_curve'].setData(
            self.axis_dict[axis_key]['time_array'],
            self.axis_dict[axis_key]['position']['set_point'])
        self.axis_dict[axis_key]['pos_est_curve'].setData(
            self.axis_dict[axis_key]['time_array'],
            self.axis_dict[axis_key]['position']['estimate'])

    def update_X_range(self, axis):
        upper_limit = self.axis_dict[axis]['time_array'][-1]
        lower_limit = self.axis_dict[axis]['time_array'][0]
        if (upper_limit - lower_limit) > self.sampling_period:
            while (upper_limit - lower_limit) > self.sampling_period:
                self.axis_dict[axis]['time_array'].pop(0)
                self.axis_dict[axis]['velocity']['estimate'].pop(0)
                self.axis_dict[axis]['velocity']['set_point'].pop(0)
                self.axis_dict[axis]['current']['estimate'].pop(0)
                self.axis_dict[axis]['current']['set_point'].pop(0)
                self.axis_dict[axis]['position']['estimate'].pop(0)
                self.axis_dict[axis]['position']['set_point'].pop(0)
                upper_limit = self.axis_dict[axis]['time_array'][-1]
                lower_limit = self.axis_dict[axis]['time_array'][0]

    def get_sampling_period(self):
        sampling_period = SAMPLING_PERIOD
        if 'odrive' + str(self.drive_index) in self.conf:
            drive_conf = self.conf['odrive' + str(self.drive_index)]
        else:
            drive_conf = {}
        if 'sampling_period' in drive_conf:
            sampling_period = drive_conf['sampling_period']
        return sampling_period

    # TODO: Disconnect/Reconnect support.
    # TODO: Clean this func maybe
    def odrive_connect(self):
        self.odrive_worker = ODriveConnector()
        self.odrive_worker.sig_odrive_connected.connect(
            self.odrive_connected)
        self.odrive_worker.start()

    # TODO: Clean this func maybe
    def odrive_connected(self, drive_list):
        self.drive_list = drive_list
        if len(drive_list) == 0:
            QMessageBox.information(self, 'Info', 'Can not find drive!',
                                    QMessageBox.Ok, QMessageBox.Ok)
        elif len(drive_list) > 1:
            self.select_dialog = SelectDrive(drive_list)
            self.select_dialog.sig_odrive_select.connect(self.select_drive)
            self.select_dialog.show()
        else:
            self.drive = drive_list[0]
            self.drive_index = 0
        self.setWindowTitle('Dashboard: ' + 'odrv' + str(self.drive_index))
        self.config_btn_connect.setIcon(self.icon_connect)
        self.online = True

    # TODO: Clean this func maybe
    def select_drive(self, i):
        self.drive = self.drive_list[i]
        self.drive_index = i

    def config_clicked(self):
        if not self.online:
            QMessageBox.information(self, 'Info', 'Connect drive first!',
                                    QMessageBox.Ok, QMessageBox.Ok)
            return
        self.config_window = ODriveConfig(self.conf)
        self.config_window.sig_conf_changed.connect(self.reload_config)
        self.config_window.show()
        # TODO: Move the stuff into __init__()
        self.config_window.pass_odrive(self.drive, self.drive_index)

    def reload_config(self):
        self.conf = load_conf()


if __name__ == '__main__':
    import sys

    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    main_window = Dashboard()
    main_window.show()
    sys.exit(app.exec())
