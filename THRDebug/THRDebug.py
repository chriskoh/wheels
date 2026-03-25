import ac
import acsys
import math

app = "THRDebug"
appWindow = 0
thr_label = 0

APP_WIDTH = 160
APP_HEIGHT = 60

DRIFT_ANGLE_MIN = 5.0

prev_slip_angle = 0.0
prev_speed = 0.0
angle_rate_smooth = 0.0
speed_rate_smooth = 0.0
throttle_signal = 0.0


def acMain(ac_version):
    global appWindow, thr_label

    appWindow = ac.newApp(app)
    ac.setSize(appWindow, APP_WIDTH, APP_HEIGHT)
    ac.setTitle(appWindow, "")
    ac.setIconPosition(appWindow, 0, -10000)
    ac.setBackgroundOpacity(appWindow, 0.9)
    ac.drawBorder(appWindow, 0)

    thr_label = ac.addLabel(appWindow, "THR: 0")
    ac.setPosition(thr_label, 10, 10)
    ac.setFontSize(thr_label, 32)
    ac.setFontColor(thr_label, 1.0, 1.0, 1.0, 1.0)

    ac.addRenderCallback(appWindow, onFormRender)
    ac.log("[" + app + "] Loaded")
    return app


def acUpdate(deltaT):
    pass


def get_body_slip_angle(car):
    try:
        lv = ac.getCarState(car, acsys.CS.LocalVelocity)
        speed = ac.getCarState(car, acsys.CS.SpeedKMH)
        if speed < 5.0:
            return 0.0
        return math.degrees(math.atan2(lv[0], abs(lv[2])))
    except Exception:
        return 0.0


def onFormRender(deltaT):
    global prev_slip_angle, prev_speed
    global angle_rate_smooth, speed_rate_smooth, throttle_signal

    ac.setBackgroundOpacity(appWindow, 0.9)

    car = ac.getFocusedCar()
    slip_angle = get_body_slip_angle(car)
    abs_angle = abs(slip_angle)

    speed = 0.0
    try:
        speed = ac.getCarState(car, acsys.CS.SpeedKMH)
    except Exception:
        pass

    if deltaT > 0:
        raw_angle_rate = (abs_angle - abs(prev_slip_angle)) / deltaT
        raw_speed_rate = (speed - prev_speed) / deltaT
    else:
        raw_angle_rate = 0.0
        raw_speed_rate = 0.0
    prev_slip_angle = slip_angle
    prev_speed = speed

    angle_rate_smooth = angle_rate_smooth * 0.90 + raw_angle_rate * 0.10
    speed_rate_smooth = speed_rate_smooth * 0.90 + raw_speed_rate * 0.10

    throttle_signal = angle_rate_smooth + speed_rate_smooth * 4.0

    ac.setText(thr_label, "THR: {:.0f}".format(throttle_signal))
