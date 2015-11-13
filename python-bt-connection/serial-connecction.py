from serial import Serial

SERIAL_PORT = "/dev/..."

class SerialWrapper():

    def __init__(self):
        if not app.debug:
            self.serial_connection = Serial(SERIAL_PORT, 9600, timeout=1)
        else:
            self.serial_connection = None

    def write(self, var):
        if self.serial_connection:
            self.serial_connection.write(var)
        else:
            app.logger.info("Fake write off %s" % var)

    def readlines(self):
        if self.serial_connection:
            return self.serial_connection.readlines()
        return []

    def close(self):
        if self.serial_connection:
            self.serial_connection.close()

ser = SerialWrapper()
