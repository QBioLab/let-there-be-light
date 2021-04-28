from collections import namedtuple
import serial
import struct

"""
v0.1 first version
"""

# outgoing CMD_CONTROL - control gimbal movement
ControlData = namedtuple(
    'ControlData',
    'roll_mode pitch_mode yaw_mode roll_speed roll_angle \
     pitch_speed pitch_angle yaw_speed yaw_angle')
AngleData = namedtuple(
    'AngleData',
    'imu_roll_angle target_roll_angle target_roll_speed \
     imu_pitch_angle target_pitch_angle target_pitch_speed \
     imu_yaw_angle target_yaw_angle target_yaw_speed')
Message = namedtuple(
    'Message',
    'start_character command_id payload_size header_checksum \
    payload payload_checksum')


class gimbal:
    def __init__(self, PORT):
        self.connection = serial.Serial(PORT, baudrate=115200, timeout=10)

    def pack_control_data(self, control_data: ControlData) -> bytes:
        return struct.pack('<BBBhhhhhh', *control_data)

    def create_message(self, command_id: int, payload: bytes) -> Message:
        payload_size = len(payload)
        return Message(start_character=ord('>'),
              command_id=command_id,
              payload_size=payload_size,
              header_checksum=(command_id + payload_size) % 256,
              payload=payload,
              payload_checksum=sum(payload) % 256)

    def pack_message(self, message: Message) -> bytes:
        message_format = '<BBBB{}sB'.format(message.payload_size)
        return struct.pack(message_format, *message)


    def unpack_message(self, data: bytes, payload_size: int) -> Message:
        message_format = '<BBBB{}sB'.format(payload_size)
        return Message._make(struct.unpack(message_format, data))

    def read_message(self, connection: serial.Serial, payload_size: int) -> Message:
        # 5 is the length of the header + payload checksum byte
        # 1 is the payload size
        response_data = connection.read(5 + payload_size)
        #print('received response', response_data)
        return self.unpack_message(response_data, payload_size)

    def park_gimbal(self):
        CMD_CONTROL = 67
        control_data = ControlData(roll_mode=0, roll_speed=0, roll_angle=0,
                               pitch_mode=2, pitch_speed=32767, pitch_angle=4096,
                               yaw_mode=2, yaw_speed=32767, yaw_angle=0)
        #print('command to send:', control_data)
        packed_control_data = self.pack_control_data(control_data)
        #print('packed command as payload:', packed_control_data)
        message = self.create_message(CMD_CONTROL, packed_control_data)
        packed_message = self.pack_message(message)
        self.connection.write(packed_message)
        message = self.read_message(self.connection, 1)
        #print('received confirmation:', message)

    def rotate_gimbal(self, pitch_angle, yaw_angle):
        CMD_CONTROL = 67
        control_data = ControlData(roll_mode=0, roll_speed=0, roll_angle=0,
                               pitch_mode=2, pitch_speed=32767, pitch_angle=pitch_angle,
                               yaw_mode=2, yaw_speed=32767, yaw_angle=yaw_angle)
        packed_control_data = self.pack_control_data(control_data)
        message = self.create_message(CMD_CONTROL, packed_control_data)
        packed_message = self.pack_message(message)
        self.connection.write(packed_message)
        message = self.read_message(self.connection, 1)
        print('received confirmation:', message)
        print('confirmed command with ID:', ord(message.payload))

    def rotate_gimbal_rel(self, pitch_angle, yaw_angle):
        CMD_CONTROL = 67
        control_data = ControlData(roll_mode=0, roll_speed=0, roll_angle=0,
                               pitch_mode=5, pitch_speed=32767, pitch_angle=pitch_angle,
                               yaw_mode=5, yaw_speed=32767, yaw_angle=yaw_angle)
        packed_control_data = self.pack_control_data(control_data)
        message = self.create_message(CMD_CONTROL, packed_control_data)
        packed_message = self.pack_message(message)
        self.connection.write(packed_message)
        message = self.read_message(self.connection, 1)
        print('received confirmation:', message)
        print('confirmed command with ID:', ord(message.payload))

    def get_angles(self):
        CMD_GET_ANGLES = 73
        message = self.create_message(CMD_GET_ANGLES, b'')
        packed_message = self.pack_message(message)
        self.connection.write(packed_message)
        message = self.read_message(self.connection, 18) # 2*3*3
        return AngleData._make(struct.unpack('hhhhhhhhh', message.payload))

if __name__ == '__main__':
     gimbal_run = gimbal("/dev/ttyUSB0")
     gimbal.park_gimbal()
