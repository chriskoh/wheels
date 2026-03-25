# DriftSteerHUD - Assetto Corsa Steering Angle HUD

A simple HUD app for Assetto Corsa that visualizes your front tire steering angle in real-time. Built for learning to drift.

![Python](https://img.shields.io/badge/python-2.7%2F3.x-blue)
![AC](https://img.shields.io/badge/Assetto%20Corsa-compatible-green)

## What It Does

- Displays two tire rectangles that rotate based on your actual steering input
- Red direction indicator line on each tire shows where the wheels are pointing
- Numeric angle readout in degrees

## Installation

1. Download or clone this repo
2. Copy the `DriftSteerHUD` folder into your Assetto Corsa install:
   ```
   [Steam]/steamapps/common/assettocorsa/apps/python/
   ```
3. Launch Assetto Corsa
4. In a session, open the app sidebar (right side) and enable **DriftSteerHUD**

## Configuration

The `STEERING_RATIO` variable in `DriftSteerHUD.py` controls how steering wheel angle maps to tire angle. Default is `14.0` (14:1 ratio). Adjust per car if needed:

- Lower value = more tire movement per steering input
- Typical range: 12:1 to 16:1

## License

MIT
