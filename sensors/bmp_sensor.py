import board
import adafruit_bmp280

i2c = board.I2C()
bmp = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)

def read_bmp():
    bmp_temp = bmp.temperature
    bmp_pressure = bmp.pressure
    return bmp_temp, bmp_pressure