import time
import struct
import serial
from serial.tools import list_ports

NUM_DIALS = 4
DIAL_STEPS_PER_MM = 201.620195931
DIAL_BOARD_INIT_RESPONSE = "formlabs-dial-indicator-board\r\n"

class DialIndicatorCommunicationException(Exception):
    def __init__(self, msg):
        super(DialIndicatorCommunicationException, self).__init__(msg)
        self.message = msg

class DialIndicatorBoard():
    def __init__(self):
        self.dial_port = None
        self.dial_zeros = [0] * NUM_DIALS
        self.initial_dial_zeros = [0] * NUM_DIALS
        self.connect()

    def connect(self):
        # search all COM ports for the dial indicator board
        valid_ports = ["/dev/ttyUSB.*", "/dev/tty.usbserial.*", "USB Serial Port.*", "/dev/cu.usbserial*"]
        for test_port in valid_ports:
            print test_port
            ports = list(list_ports.grep(test_port))
            print ports
            if not ports:
                continue
            port_name = ports[0][0]
            try:
                # open the serial port
                port = serial.Serial(port_name, 9600, timeout=1)

                # wait after opening the port because the
                # arduino resets on serial connection
                time.sleep(2)

                # send the ping
                port.write('p')
                port.flush()

                verification = port.readline()
                print "verification", verification

                # verify the pong
                if  verification != DIAL_BOARD_INIT_RESPONSE:
                    port.close()
                    continue
                self.dial_port = port
                self.initial_zero()
                return True
            except (serial.SerialException, OSError):
                pass
        raise DialIndicatorCommunicationException(RuntimeError("Cannot find the Dial Indicator Board"))

    def disconnect(self, *args, **kwargs):
        if self.dial_port is not None:
            self.dial_port.close()

    def _read_dials(self):
        """Returns a tuple of measurements for the dials in mm"""
        try:
            # request to read dial indicators
            self.dial_port.write('r')
            self.dial_port.flush()

            # read in values
            values = [float(self.dial_port.readline()) for i in range(NUM_DIALS)]
            checksum = float(self.dial_port.readline())
            if sum(values) != checksum:
                raise ValueError("Error reading from dial indicator board")

            # Correct for error where the arduino overflows its 16 bit counter
            for i in range(len(values)):
                values[i] = (values[i] - self.initial_dial_zeros[i] + 2**16 + 2**15) % 2**16 - 2**15
            return tuple([values[i] / DIAL_STEPS_PER_MM for i in range(NUM_DIALS)])
        except serial.SerialException:
            raise DialIndicatorCommunicationException("Unable to get reading")

    def get_readings(self):
        values = self._read_dials()
        return tuple([values[i] - self.dial_zeros[i] for i in range(NUM_DIALS)])

    def initial_zero(self):
        values = self._read_dials()
        self.initial_dial_zeros = [values[i] * DIAL_STEPS_PER_MM for i in range(NUM_DIALS)]
        return self.initial_dial_zeros

    def zero(self, correction_mm=[0, 0, 0, 0]):
        # Correction = [x, y, z, w] in mm
        correction_dial = []
        for val in correction_mm:
            correction_dial.append(val * DIAL_STEPS_PER_MM)
        values = self._read_dials()
        self.dial_zeros = [values[i] + correction_dial[i] for i in range(NUM_DIALS)]
        return self.dial_zeros

    def get_connected_dials(self):
        try:
            self.dial_port.write('c')
            self.dial_port.flush()

            return self.dial_port.readline()
        except serial.SerialException:
            raise DialIndicatorCommunicationException("Unable to get connected dials")

    def verify_dials_connected(self, dials):
        connected_dials = self.get_connected_dials()
        not_found = ""
        all_dials_connected = True
        for dial in dials:
            if dial not in connected_dials:
                all_dials_connected = False
                not_found += dial
        return all_dials_connected, not_found

    def set_leds(self, colors):
        try:
            """Write the given colors to the LEDs."""
            data = struct.pack(12 * 'B', *colors)

            self.dial_port.write('l')
            self.dial_port.write(data)
            self.dial_port.flush()
        except serial.SerialException:
            raise DialIndicatorCommunicationException("Unable to write colors to LEDs")