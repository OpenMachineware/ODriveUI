def check_axis_error_b1(bit):
    error_string = 'NULL'
    if bit == '0':  # ERROR_NONE = 0x00,
        error_string = 'No errors'
    # An invalid state was requested
    elif bit == '1':  # ERROR_INVALID_STATE = 0x01
        error_string = 'ERROR_INVALID_STATE'
    elif bit == '2':  # ERROR_DC_BUS_UNDER_VOLTAGE = 0x02,
        error_string = 'ERROR_DC_BUS_UNDER_VOLTAGE'
    elif bit == '4':  # ERROR_DC_BUS_OVER_VOLTAGE = 0x04,
        error_string = 'ERROR_DC_BUS_OVER_VOLTAGE'
    elif bit == '8':  # ERROR_CURRENT_MEASUREMENT_TIMEOUT = 0x08,
        error_string = 'ERROR_CURRENT_MEASUREMENT_TIMEOUT'
    return error_string


def check_axis_error_b2(bit):
    error_string = ' '
    # The brake resistor was unexpectedly disarmed
    if bit == '1':  # ERROR_BRAKE_RESISTOR_DISARMED = 0x10
        error_string = 'ERROR_BRAKE_RESISTOR_DISARMED'
    # The motor was unexpectedly disarmed
    elif bit == '2':  # ERROR_MOTOR_DISARMED = 0x20
        error_string = 'ERROR_MOTOR_DISARMED'
    # odrvX.axisX.motor.error in motor.hpp
    elif bit == '4':  # ERROR_MOTOR_FAILED = 0x40,
        error_string = 'ERROR_MOTOR_FAILED'
    elif bit == '8':  # ERROR_SENSORLESS_ESTIMATOR_FAILED = 0x80,
        error_string = 'ERROR_SENSORLESS_ESTIMATOR_FAILED'
    return error_string


def check_axis_error_b3(bit):
    error_string = ' '
    # odrvX.axisX.encoder.error in encoder.hpp
    if bit == '1':  # ERROR_ENCODER_FAILED = 0x100
        error_string = 'ERROR_ENCODER_FAILED'
    elif bit == '2':  # ERROR_CONTROLLER_FAILED = 0x200,
        error_string = 'ERROR_CONTROLLER_FAILED'
    elif bit == '4':  # ERROR_POS_CTRL_DURING_SENSORLESS = 0x400,
        error_string = 'ERROR_POS_CTRL_DURING_SENSORLESS'
    return error_string


def check_axis_errors(axis_error):
    error_string = ''
    if len(axis_error) == 1:
        first_bit = axis_error
        error_string = check_axis_error_b1(first_bit)
    elif len(axis_error) == 2:
        first_bit = axis_error[1]
        second_bit = axis_error[0]
        error_string = check_axis_error_b1(first_bit)
        error_string += ' - '
        error_string += check_axis_error_b2(second_bit)
    elif len(axis_error) == 3:
        first_bit = axis_error[2]
        second_bit = axis_error[1]
        third_bit = axis_error[0]
        error_string = check_axis_error_b1(first_bit)
        error_string += ' - '
        error_string += check_axis_error_b2(second_bit)
        error_string += ' - '
        error_string += check_axis_error_b3(third_bit)
    return error_string


def check_encoder_error_b1(bit):
    error_string = 'NULL'
    if bit == '0':  # ERROR_NONE = 0x00,
        error_string = 'No errors'
    elif bit == '1':  # ERROR_UNSTABLE_GAIN = 0x01,
        error_string = 'ERROR_UNSTABLE_GAIN'
    elif bit == '2':  # ERROR_CPR_OUT_OF_RANGE = 0x02,
        error_string = 'ERROR_CPR_OUT_OF_RANGE'
    elif bit == '4':  # ERROR_NO_RESPONSE = 0x04,
        error_string = 'ERROR_NO_RESPONSE'
    elif bit == '8':  # ERROR_UNSUPPORTED_ENCODER_MODE = 0x08,
        error_string = 'ERROR_UNSUPPORTED_ENCODER_MODE'
    return error_string


def check_encoder_error_b2(bit):
    error_string = ' '
    if bit == '1':  # ERROR_ILLEGAL_HALL_STATE = 0x10,
        error_string = 'ERROR_ILLEGAL_HALL_STATE'
    elif bit == '2':  # ERROR_INDEX_NOT_FOUND_YET = 0x20,
        error_string = 'ERROR_INDEX_NOT_FOUND_YET'
    return error_string


def check_axis_encoder_errors(encoder_error):
    error_string = ''
    if len(encoder_error) == 1:
        first_bit = encoder_error
        error_string = check_encoder_error_b1(first_bit)
    elif len(encoder_error) == 2:
        first_bit = encoder_error[1]
        second_bit = encoder_error[0]
        error_string = check_encoder_error_b1(first_bit)
        error_string += ' - '
        error_string += check_encoder_error_b2(second_bit)
    return error_string


def check_motor_error_b1(bit):
    error_string = 'NULL'
    if bit == '0':  # ERROR_NONE = 0x00,
        error_string = 'No errors'
    elif bit == '1':  # ERROR_PHASE_RESISTANCE_OUT_OF_RANGE = 0x0001,
        error_string = 'ERROR_PHASE_RESISTANCE_OUT_OF_RANGE'
    elif bit == '2':  # ERROR_PHASE_INDUCTANCE_OUT_OF_RANGE = 0x0002,
        error_string = 'ERROR_PHASE_INDUCTANCE_OUT_OF_RANGE'
    elif bit == '4':  # ERROR_ADC_FAILED = 0x0004,
        error_string = 'ERROR_ADC_FAILED'
    elif bit == '8':  # ERROR_DRV_FAULT = 0x0008,
        error_string = 'ERROR_DRV_FAULT'
    return error_string


def check_motor_error_b2(bit):
    error_string = ' '
    if bit == '1':  # ERROR_CONTROL_DEADLINE_MISSED = 0x0010,
        error_string = 'ERROR_CONTROL_DEADLINE_MISSED'
    elif bit == '2':  # ERROR_NOT_IMPLEMENTED_MOTOR_TYPE = 0x0020,
        error_string = 'ERROR_NOT_IMPLEMENTED_MOTOR_TYPE'
    elif bit == '4':  # ERROR_BRAKE_CURRENT_OUT_OF_RANGE = 0x0040,
        error_string = 'ERROR_BRAKE_CURRENT_OUT_OF_RANGE'
    elif bit == '8':  # ERROR_MODULATION_MAGNITUDE = 0x0080,
        error_string = 'ERROR_MODULATION_MAGNITUDE'
    return error_string


def check_motor_error_b3(bit):
    error_string = ' '
    if bit == '1':  # ERROR_BRAKE_DEADTIME_VIOLATION = 0x0100,
        error_string = 'ERROR_BRAKE_DEADTIME_VIOLATION'
    elif bit == '2':  # ERROR_UNEXPECTED_TIMER_CALLBACK = 0x0200,
        error_string = 'ERROR_UNEXPECTED_TIMER_CALLBACK'
    elif bit == '4':  # ERROR_CURRENT_SENSE_SATURATION = 0x0400
        error_string = 'ERROR_CURRENT_SENSE_SATURATION'
    return error_string


def check_axis_motor_errors(motor_error):
    error_string = ''
    if len(motor_error) == 1:
        first_bit = motor_error
        error_string = check_motor_error_b1(first_bit)
    elif len(motor_error) == 2:
        first_bit = motor_error[1]
        second_bit = motor_error[0]
        error_string = check_motor_error_b1(first_bit)
        error_string += ' - '
        error_string += check_motor_error_b2(second_bit)
    elif len(motor_error) == 3:
        first_bit = motor_error[2]
        second_bit = motor_error[1]
        third_bit = motor_error[0]
        error_string = check_motor_error_b1(first_bit)
        error_string += ' - '
        error_string += check_motor_error_b2(second_bit)
        error_string += ' - '
        error_string += check_motor_error_b3(third_bit)
    return error_string
