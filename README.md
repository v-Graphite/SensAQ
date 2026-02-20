# SensAQ - Air Monitoring System


SensAQ is a Raspberry Pi–based air quality monitoring system designed for real-time indoor air analysis.

## Features

- Real-time CO₂ measurement (ppm)
- Temperature, humidity and air pressure monitoring
- Visual air quality evaluation
- Acustic alarm for critical CO₂ levels
- Manual alarm acknowledgment via hardware button
- Fullscreen dashboard interface
- Automatic system startup

## Hardware

- Raspberry Pi 3B+
- CO₂, Temperature, Humidity sensor SCD41 (the temperature on mine was broken)
- Temperature / Humidity / Pressure sensor BMP280
- 3.5mm audio output, PAM8403, Speaker
- LED indicator
- Push button
- resistors and many cables
- 5 inch display

## Software Stack

- Python 
- Pygame (UI + Audio)

## Installation

```bash
git clone https://github.com/v-Graphite/SensAQ.git
cd SensAQ
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt