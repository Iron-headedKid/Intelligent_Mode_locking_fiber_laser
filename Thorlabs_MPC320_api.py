import serial
from serial.tools import list_ports
import re
import struct
from typing import Optional
import time


# Find the port according to serial number of the device
def find_device(serial_number):
    for port in serial.tools.list_ports.comports():
        if (serial_number is not None) and (
                (port.serial_number is None) or not re.match(serial_number, port.serial_number)):
            continue
        return port


# The format of the message. please refer to the official documentation for details,
# which is titled "Thorlabs Motion Controllers Host-Controller Communications Protocol."
def pack_data(
        msgid: int,
        dest: int,
        source: int,
        *,
        param1: int = 0,
        param2: int = 0,
        data: Optional[bytes] = None
):
    if data is not None:
        assert param1 == param2 == 0
        return struct.pack("<HHBB", msgid, len(data), dest | 0x80, source) + data
    else:
        return struct.pack("<H4B", msgid, param1, param2, dest, source)


# The paddle angle ranges from 0 to 160°, corresponding to positions from 0 to 1297
def _check_angle_and_convert_position(angle):
    if not 0 <= angle <= 160:
        raise ValueError("Angle must be between 0 and 160!")
    else:
        return round(angle * 8.10625)  # the position must be an integer


def position_convert_angle(position):
    return round(position / 8.10625, 1)


class MPC320:
    """
    Class for controlling Thorlabs MPC320 motor controller.
    Parameters:
        serial_number (str): The serial number of the device. this serial number is an 8-digit decimal number.
        the first two digits (referred to as the prefix) are "38" for MPC.
    """
    # Message IDs for various operations
    MESSAGE_ID_REQ_INFO = 0x0005    # Requesting information about the device
    MESSAGE_ID_SET_ENABLE = 0x0210   # Enabling the paddle
    MESSAGE_MOD_IDENTIFY = 0x0223  # Identifying the device
    MESSAGE_ID_MOVE_HOME = 0x0443  # Moving to home position, which is the initialization location
    MESSAGE_ID_MOVE_TO = 0x0453  # Moving to a given position, range from 0 to 160°
    MESSAGE_ID_MOVE_JOG = 0x046A  # Jogging, direction: 1 - angle increase, 2 - backward
    MESSAGE_ID_REQ_STATUS = 0x0490  # Requesting paddle's position
    MESSAGE_ID_SET_PARAMS = 0x0530  # Setting Velocity, HomePosition, JogStep1, JogStep2, JogStep3
    MESSAGE_ID_REQ_PARAMS = 0x0531  # Requesting Velocity, HomePosition, JogStep1, JogStep2, JogStep3
    # Device addresses
    HOST = 0x01  # Host address, such as PC address
    USB_PORT = 0x50  # USB port address, which is the MPC mother board address
    BAYS = (0x50, 0x21, 0x22, 0x23)  # Bays addresses, which are the addresses of the paddle motors
    # Channels addresses correspond one-to-one with the paddles' bays, 0x07 means all channels.
    CHANNELS = (0x07, 0x01, 0x02, 0x04)

    def __init__(self, serial_number="38"):
        """
        Initialize the MPC320 controller.
        if the serial number is not entered, it will automatically search for and connect to the first device with "38".
        """
        self.serial_number = serial_number
        self.serial_port = find_device(serial_number)
        self.MPC = serial.Serial(self.serial_port.device, 115200, timeout=0.5)
        self.enable_paddle()
        self.set_params(velocity=100, home_position=0, jog_step1=1, jog_step2=1, jog_step3=1)
        self.get_info()
        self.MPC.reset_input_buffer()   # clear the input buffer
        self.MPC.reset_output_buffer()  # clear the output buffer
        self.params = self.get_params()
        self.velocity = self.params[1]
        self.home_angle = self.params[2]
        self.jog_step = self.params[3:]
        self.angle = [self.get_status(1)[2], self.get_status(2)[2], self.get_status(3)[2]]
        # home all paddles
        for i in range(3):
            self.move_home(i + 1)
        print(f"{serial_number} MPC320 initialized")

    def get_info(self):
        self.MPC.reset_input_buffer()  # clear the input buffer
        get_info = pack_data(msgid=self.MESSAGE_ID_REQ_INFO, dest=self.USB_PORT, source=self.HOST)
        self.MPC.write(get_info)
        time.sleep(0.03)        # wait for the data to be received
        # print(self.MPC.read_all())

    # Identifying the device by flashing its LED
    def identify(self):
        self.MPC.reset_input_buffer()  # clear the input buffer
        identify = pack_data(msgid=self.MESSAGE_MOD_IDENTIFY, dest=self.USB_PORT, source=self.HOST)
        self.MPC.write(identify)

    def enable_paddle(self):
        enable_channel = pack_data(msgid=self.MESSAGE_ID_SET_ENABLE, param1=self.CHANNELS[0], param2=0x01,
                                   dest=self.USB_PORT, source=self.HOST)
        self.MPC.write(enable_channel)

    # The number of paddles is 3 for MPC320, while it is 2 for MPC220
    def _check_paddle(self, paddle):
        self.MPC.reset_input_buffer()  # clear the input buffer
        if paddle not in [1, 2, 3]:
            raise ValueError("Wrong paddle number!")

    # Extract relevant information from the message
    def analyse_data(self):
        # wait for the data to be received
        while self.MPC.in_waiting < 18:
            pass
        # print(self.MPC.in_waiting)  # Return the number of bytes in the reception cache
        response = self.MPC.read_all()
        # print(response)
        message_id = struct.unpack("<H", response[:2])[0]
        # information = None
        if message_id == 0x0491:    # the status of the paddle(20bytes)
            data = struct.unpack("<HLH", response[6:14])
            # The information is (prompt_label, paddle, angle, velocity)
            information = ('status', data[0], position_convert_angle(data[1]), data[2] * 10)

        elif message_id == 0x0532:  # the parameters of the MPC(18bytes)
            data = struct.unpack("<5H", response[8:18])
            # The information is (prompt_label, velocity, home_angle, jog_step1, jog_step2, jog_step3)
            information = ['params', data[0], position_convert_angle(data[1]), position_convert_angle(data[2]),
                           position_convert_angle(data[3]), position_convert_angle(data[4])]
        else:
            raise ValueError(f"Unknown message ID! Received message ID: {hex(message_id)}")
        return information

    def identify_moving_completed(self, paddle: int):
        start_time = time.time()
        while True:
            end_time = time.time()
            # 20+6
            if self.MPC.in_waiting >= 26:
                # print(self.MPC.read_all())
                self.MPC.reset_input_buffer()  # clear the input buffer
                self.angle[paddle - 1] = self.get_status(paddle=paddle)[2]  # update the latest angle
                # print(f"the paddle {paddle} angle is {self.angle[paddle - 1]}°")
                # print(f"the time of moving is {end_time - start_time}s")
                # print("Moving is finished")
                break
            # the experimental maximum moving time is nearly 7s, which is dependent on the velocity.
            elif end_time - start_time > (70/self.velocity):
                raise TimeoutError("Moving timeout!")

    def open(self):
        if not self.MPC.is_open:
            self.MPC.open()
            time.sleep(0.05)
        print(f"{self.serial_number} MPC320 opened")

    def get_angle(self):
        return self.angle

    # Requesting paddle's position
    def get_status(self, paddle: int):
        self._check_paddle(paddle)
        get_status = pack_data(msgid=self.MESSAGE_ID_REQ_STATUS, param1=self.CHANNELS[paddle],
                               dest=self.BAYS[paddle], source=self.HOST)
        self.MPC.write(get_status)
        return self.analyse_data()

    def get_params(self):
        self.MPC.reset_input_buffer()  # clear the input buffer
        get_params = pack_data(msgid=self.MESSAGE_ID_REQ_PARAMS, dest=self.USB_PORT, source=self.HOST)
        self.MPC.write(get_params)
        return self.analyse_data()

    # Setting paddle's parameters.
    # The unit of home position and jog step is degrees (°).
    # The unit of velocity is percent of maximum velocity (%), range from 10 to 100, multiples of 10 (Floor).
    # The manual claims that the maximum speed is 400°/s, but our actual experiment is approximately 230°/s.
    # It may be that the data transmission delay leads to the actual speed becoming slower.
    def set_params(self, velocity: int, home_position: int, jog_step1: float, jog_step2: float, jog_step3: float):
        self.MPC.reset_input_buffer()  # clear the input buffer
        if not 10 <= velocity <= 100:
            raise ValueError("Velocity must be between 10 and 100!")
        home_position = _check_angle_and_convert_position(home_position)
        jog_step1 = _check_angle_and_convert_position(jog_step1)
        jog_step2 = _check_angle_and_convert_position(jog_step2)
        jog_step3 = _check_angle_and_convert_position(jog_step3)
        set_params = pack_data(msgid=self.MESSAGE_ID_SET_PARAMS, dest=self.USB_PORT, source=self.HOST,
                               data=struct.pack("<6H", 0, velocity, home_position, jog_step1, jog_step2, jog_step3))
        self.MPC.write(set_params)
        print("MPC parameter settings completed: ", self.get_params())

    def move_home(self, paddle: int):
        self._check_paddle(paddle)
        move_home = pack_data(msgid=self.MESSAGE_ID_MOVE_HOME, param1=self.CHANNELS[paddle],
                              dest=self.BAYS[paddle], source=self.HOST)
        self.MPC.write(move_home)
        # avoid timeout error in some extreme cases
        if self.angle[paddle - 1] != self.home_angle:
            self.identify_moving_completed(paddle=paddle)
        else:
            time.sleep(0.02)
            self.MPC.read_all()  # clear the buffer

    def move_home_all(self):
        self.MPC.reset_input_buffer()  # clear the input buffer
        move_home_all = pack_data(msgid=self.MESSAGE_ID_MOVE_HOME, param1=self.CHANNELS[0],
                                  dest=self.USB_PORT, source=self.HOST)
        self.MPC.write(move_home_all)
        time.sleep(2.1)
        self.MPC.read_all()  # clear the buffer

    def move_to(self, paddle: int, angle: float):
        self._check_paddle(paddle)
        position = _check_angle_and_convert_position(angle)
        move_to = pack_data(msgid=self.MESSAGE_ID_MOVE_TO, dest=self.BAYS[paddle], source=self.HOST,
                            data=struct.pack("<Hl", self.CHANNELS[paddle], position))
        self.MPC.write(move_to)
        # avoid timeout error in some extreme cases
        if self.angle[paddle - 1] != angle:
            self.identify_moving_completed(paddle=paddle)
        else:
            time.sleep(0.02)
            self.MPC.read_all()  # clear the buffer

    def move_jog(self, paddle: int, direction: int):  # direction: 1 - angle increase, 2 - backward
        self._check_paddle(paddle)
        if direction not in [1, 2]:
            raise ValueError("Direction must be 1 or 2!")
        move_jog = pack_data(msgid=self.MESSAGE_ID_MOVE_JOG, param1=self.CHANNELS[paddle], param2=direction,
                             dest=self.BAYS[paddle], source=self.HOST)
        self.MPC.write(move_jog)
        # avoid timeout error in some extreme cases
        if abs(80 + ((-1) ** (direction-1)) * 80 - self.angle[paddle - 1]) >= self.jog_step[paddle - 1]:
            self.identify_moving_completed(paddle=paddle)
        else:
            print(f"the paddle {paddle} already reached the limit!")
            time.sleep(0.02)
            self.MPC.read_all()  # clear the buffer

    def close(self):
        self.MPC.close()
        print(f"{self.serial_number} MPC320 closed")


# 如果报错：AttributeError: 'NoneType' object has no attribute 'device'
# 解决方法：进入设备管理器，点击通用串行总线控制器，找到APT USB Device，右键属性，高级，勾选加载VCP，确定，重新插拔设备，即可解决。
# MPC = MPC320()
# angle = MPC.get_angle()
# print(angle)
# print(type(angle[0]))
