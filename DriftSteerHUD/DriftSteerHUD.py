import ac
import acsys
import math

app = "DriftSteerHUD"
appWindow = 0
btn_increase = 0
btn_decrease = 0

APP_WIDTH = 200
APP_HEIGHT = 250
TIRE_WIDTH = 30
TIRE_HEIGHT = 60
STEERING_RATIO = 14.0

# Temperature color thresholds (Celsius)
TEMP_COLD = 50.0
TEMP_COOL = 70.0
TEMP_OPTIMAL_LOW = 75.0
TEMP_OPTIMAL_HIGH = 100.0
TEMP_HOT = 120.0

scale = 1.0
SCALE_STEP = 0.1
SCALE_MIN = 0.5
SCALE_MAX = 3.0


def acMain(ac_version):
    global appWindow, btn_increase, btn_decrease

    appWindow = ac.newApp(app)
    ac.setSize(appWindow, APP_WIDTH, APP_HEIGHT)
    ac.setTitle(appWindow, "")
    ac.setIconPosition(appWindow, 0, -10000)
    ac.setBackgroundOpacity(appWindow, 0.0)
    ac.drawBorder(appWindow, 0)

    btn_decrease = ac.addButton(appWindow, "-")
    ac.setSize(btn_decrease, 20, 20)
    ac.setPosition(btn_decrease, 2, 2)
    ac.setFontSize(btn_decrease, 14)
    ac.addOnClickedListener(btn_decrease, onDecrease)

    btn_increase = ac.addButton(appWindow, "+")
    ac.setSize(btn_increase, 20, 20)
    ac.setPosition(btn_increase, 24, 2)
    ac.setFontSize(btn_increase, 14)
    ac.addOnClickedListener(btn_increase, onIncrease)

    ac.addRenderCallback(appWindow, onFormRender)
    ac.log("[" + app + "] Loaded")
    return app


def acUpdate(deltaT):
    pass


def onIncrease(*args):
    global scale
    if scale < SCALE_MAX:
        scale += SCALE_STEP


def onDecrease(*args):
    global scale
    if scale > SCALE_MIN:
        scale -= SCALE_STEP


def temp_to_color(temp):
    """Return (r, g, b): blue -> green -> yellow -> orange -> red."""
    if temp < TEMP_COLD:
        return (0.1, 0.3, 1.0)
    elif temp < TEMP_OPTIMAL_LOW:
        t = (temp - TEMP_COLD) / (TEMP_OPTIMAL_LOW - TEMP_COLD)
        return (0.1 * (1.0 - t), 0.3 + 0.7 * t, 1.0 * (1.0 - t))
    elif temp < TEMP_OPTIMAL_HIGH:
        return (0.0, 1.0, 0.0)
    elif temp < TEMP_HOT:
        t = (temp - TEMP_OPTIMAL_HIGH) / (TEMP_HOT - TEMP_OPTIMAL_HIGH)
        if t < 0.33:
            s = t / 0.33
            return (s, 1.0, 0.0)
        elif t < 0.66:
            s = (t - 0.33) / 0.33
            return (1.0, 1.0 - 0.5 * s, 0.0)
        else:
            s = (t - 0.66) / 0.34
            return (1.0, 0.5 * (1.0 - s), 0.0)
    else:
        return (1.0, 0.0, 0.0)


def draw_tire(cx, cy, angle_rad, tw, th, temp):
    hw = tw / 2.0
    hh = th / 2.0

    corners = [
        (-hw, -hh),
        ( hw, -hh),
        ( hw,  hh),
        (-hw,  hh),
    ]

    rotated = []
    for x, y in corners:
        rx = x * math.cos(angle_rad) - y * math.sin(angle_rad)
        ry = x * math.sin(angle_rad) + y * math.cos(angle_rad)
        rotated.append((cx + rx, cy + ry))

    # Filled tire colored by temperature
    r, g, b = temp_to_color(temp)
    ac.glBegin(3)
    ac.glColor4f(r, g, b, 0.85)
    for x, y in rotated:
        ac.glVertex2f(x, y)
    ac.glEnd()

    # White outline
    ac.glBegin(1)
    ac.glColor4f(1.0, 1.0, 1.0, 0.8)
    for i in range(4):
        x1, y1 = rotated[i]
        x2, y2 = rotated[(i + 1) % 4]
        ac.glVertex2f(x1, y1)
        ac.glVertex2f(x2, y2)
    ac.glEnd()


def onFormRender(deltaT):
    ac.setBackgroundOpacity(appWindow, 0.0)

    car = ac.getFocusedCar()

    # Steer angle
    try:
        steer_angle = ac.getCarState(car, acsys.CS.Steer)
        tire_angle_deg = steer_angle / STEERING_RATIO
    except Exception:
        tire_angle_deg = 0.0

    # Tire temperatures
    fl_temp = fr_temp = rl_temp = rr_temp = 70.0
    try:
        fl_temp, fr_temp, rl_temp, rr_temp = ac.getCarState(car, acsys.CS.CurrentTyresCoreTemp)
    except Exception:
        pass

    s = scale
    tw = TIRE_WIDTH * s
    th = TIRE_HEIGHT * s

    # Center of the car in widget space
    car_cx = APP_WIDTH / 2.0
    car_cy = APP_HEIGHT / 2.0

    # Wheel positions
    spacing = 50 * s
    front_offset_y = -70 * s
    rear_offset_y = 70 * s

    front_steer_rad = math.radians(tire_angle_deg)

    # Front left — steered
    fl_cx, fl_cy = car_cx - spacing, car_cy + front_offset_y
    draw_tire(fl_cx, fl_cy, front_steer_rad, tw, th, fl_temp)

    # Front right — steered
    fr_cx, fr_cy = car_cx + spacing, car_cy + front_offset_y
    draw_tire(fr_cx, fr_cy, front_steer_rad, tw, th, fr_temp)

    # Rear left — always straight
    rl_cx, rl_cy = car_cx - spacing, car_cy + rear_offset_y
    draw_tire(rl_cx, rl_cy, 0.0, tw, th, rl_temp)

    # Rear right — always straight
    rr_cx, rr_cy = car_cx + spacing, car_cy + rear_offset_y
    draw_tire(rr_cx, rr_cy, 0.0, tw, th, rr_temp)
