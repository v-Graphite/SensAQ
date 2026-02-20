import time
import board
import adafruit_scd4x

i2c = board.I2C()
scd = adafruit_scd4x.SCD4X(i2c)
scd.start_periodic_measurement()
time.sleep(5)

def read():
    if scd.data_ready:
        return scd.CO2, scd.relative_humidity #, scd.temperature,
    return None