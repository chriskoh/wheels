import ac
import acsys
import math

app = "DriftSteerHUD"
appWindow = 0
angle_label = 0
btn_increase = 0
btn_decrease = 0

APP_WIDTH = 200
APP_HEIGHT = 250
TIRE_WIDTH = 30
TIRE_HEIGHT = 60
STEERING_RATIO = 14.0

# Temperature color thresholds (Celsius)
TEMP_COLD = 60.0     # Below this = blue (too cold)
TEMP_OPTIMAL = 85.0  # Around this = green (ideal)
TEMP_HOT = 110.0     # Above this = red (overheating)

scale = 1.0
SCALE_STEP = 0.1
SCALE_MIN = 0.5
SCALE_MAX = 3.0


def acMain(ac_version):
    global appWindow, angle_label, btn_increase, btn_decrease

    appWindow = ac.newApp(app)
    ac.setSize(appWindow, APP_WIDTH, APP_HEIGHT)
    ac.setTitle(appWindow, "")
    ac.setIconPosition(appWindow, 0, -10000)
    ac.setBackgroundOpacity(appWindow, 0.0)
    ac.drawBorder(appWindow, 0)

    angle_label = ac.addLabel(appWindow, "0.0")
    ac.setPosition(angle_label, APP_WIDTH // 2 - 20, APP_HEIGHT - 30)
    ac.setFontSize(angle_label, 16)
    ac.setFontColor(angle_label, 1.0, 1.0, 1.0, 1.0)

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
    """Return (r, g, b) based on tire temperature."""
    if temp < TEMP_COLD:
        # Blue (too cold)
        return (0.2, 0.4, 1.0)
    elif temp < TEMP_OPTIMAL:
        # Blend from blue to green
        t = (temp - TEMP_COLD) / (TEMP_OPTIMAL - TEMP_COLD)
        return (0.2 * (1.0 - t), 0.4 + 0.6 * t, 1.0 * (1.0 - t) + 0.2 * t)
    elif temp < TEMP_HOT:
        # Blend from green to red
        t = (temp - TEMP_OPTIMAL) / (TEMP_HOT - TEMP_OPTIMAL)
        return (t, 1.0 * (1.0 - t), 0.2 * (1.0 - t))
    else:
        # Red (overheating)
        return (1.0, 0.0, 0.0)


def onFormRender(deltaT):
    global angle_label

    ac.setBackgroundOpacity(appWindow, 0.0)

    try:
        car = ac.getFocusedCar()
        steer_angle = ac.getCarState(car, acsys.CS.Steer)
        tire_angle_deg = math.degrees(steer_angle) / STEERING_RATIO

        # Get tire temps as 4D vector: FL, FR, RL, RR
        temps = ac.getCarState(car, acsys.CS.ThermalState)
        fl_temp = temps[0]
        fr_temp = temps[1]
        rl_temp = temps[2]
        rr_temp = temps[3]
    except Exception:
        tire_angle_deg = 0.0
        fl_temp = fr_temp = rl_temp = rr_temp = 70.0

    ac.setText(angle_label, "{:.1f}".format(tire_angle_deg))

    tw = TIRE_WIDTH * scale
    th = TIRE_HEIGHT * scale
    spacing = 50 * scale
    cx = APP_WIDTH / 2.0

    # Front tires (rotated by steering)
    front_y = APP_HEIGHT * 0.3
    draw_tire(cx - spacing, front_y, tire_angle_deg, tw, th, fl_temp)
    draw_tire(cx + spacing, front_y, tire_angle_deg, tw, th, fr_temp)

    # Rear tires (no rotation)
    rear_y = APP_HEIGHT * 0.7
    draw_tire(cx - spacing, rear_y, 0.0, tw, th, rl_temp)
    draw_tire(cx + spacing, rear_y, 0.0, tw, th, rr_temp)


def draw_tire(cx, cy, angle_deg, tw, th, temp):
    angle_rad = math.radians(angle_deg)
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
