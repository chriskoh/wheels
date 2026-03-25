import ac
import acsys
import math

app = "ThrottleMeter"
appWindow = 0

APP_WIDTH = 50
APP_HEIGHT = 200

# Drift detection
DRIFT_ANGLE_MIN = 5.0

# Smoothing
prev_slip_angle = 0.0
angle_rate_smooth = 0.0

# Scale
scale = 1.0
SCALE_STEP = 0.1
SCALE_MIN = 0.5
SCALE_MAX = 3.0
btn_increase = 0
btn_decrease = 0


def acMain(ac_version):
    global appWindow, btn_increase, btn_decrease

    appWindow = ac.newApp(app)
    ac.setSize(appWindow, APP_WIDTH, APP_HEIGHT)
    ac.setTitle(appWindow, "")
    ac.setIconPosition(appWindow, 0, -10000)
    ac.setBackgroundOpacity(appWindow, 0.0)
    ac.drawBorder(appWindow, 0)

    btn_decrease = ac.addButton(appWindow, "-")
    ac.setSize(btn_decrease, 16, 16)
    ac.setPosition(btn_decrease, 2, 2)
    ac.setFontSize(btn_decrease, 12)
    ac.addOnClickedListener(btn_decrease, onDecrease)

    btn_increase = ac.addButton(appWindow, "+")
    ac.setSize(btn_increase, 16, 16)
    ac.setPosition(btn_increase, 20, 2)
    ac.setFontSize(btn_increase, 12)
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
    global prev_slip_angle, angle_rate_smooth

    ac.setBackgroundOpacity(appWindow, 0.0)

    car = ac.getFocusedCar()
    slip_angle = get_body_slip_angle(car)
    abs_angle = abs(slip_angle)

    # Angle rate of change
    if deltaT > 0:
        raw_rate = (abs_angle - abs(prev_slip_angle)) / deltaT
    else:
        raw_rate = 0.0
    prev_slip_angle = slip_angle

    # Smooth
    angle_rate_smooth = angle_rate_smooth * 0.92 + raw_rate * 0.08

    is_drifting = abs_angle > DRIFT_ANGLE_MIN

    draw_vertical_meter(is_drifting)


def draw_vertical_meter(active):
    s = scale
    bar_x = 5 * s
    bar_y = 22 * s
    bar_w = (APP_WIDTH - 10) * s
    bar_h = (APP_HEIGHT - 30) * s
    center_y = bar_y + bar_h / 2.0

    # Background
    ac.glBegin(3)
    ac.glColor4f(0.1, 0.1, 0.1, 0.85)
    ac.glVertex2f(bar_x, bar_y)
    ac.glVertex2f(bar_x + bar_w, bar_y)
    ac.glVertex2f(bar_x + bar_w, bar_y + bar_h)
    ac.glVertex2f(bar_x, bar_y + bar_h)
    ac.glEnd()

    # Green target zone in center
    zone_h = bar_h * 0.35
    zone_top = center_y - zone_h / 2
    zone_bot = center_y + zone_h / 2
    ac.glBegin(3)
    ac.glColor4f(0.1, 0.4, 0.1, 0.6)
    ac.glVertex2f(bar_x, zone_top)
    ac.glVertex2f(bar_x + bar_w, zone_top)
    ac.glVertex2f(bar_x + bar_w, zone_bot)
    ac.glVertex2f(bar_x, zone_bot)
    ac.glEnd()

    # Zone borders
    ac.glBegin(0)
    ac.glColor4f(0.3, 1.0, 0.3, 0.8)
    ac.glVertex2f(bar_x, zone_top)
    ac.glVertex2f(bar_x + bar_w, zone_top)
    ac.glEnd()
    ac.glBegin(0)
    ac.glColor4f(0.3, 1.0, 0.3, 0.8)
    ac.glVertex2f(bar_x, zone_bot)
    ac.glVertex2f(bar_x + bar_w, zone_bot)
    ac.glEnd()

    if not active:
        return

    # Map rate to vertical position
    # Positive rate (angle growing, too much gas) = needle goes UP
    # Negative rate (drift dying, need more gas) = needle goes DOWN
    clamped = max(-80.0, min(80.0, angle_rate_smooth))
    normalized = clamped / 80.0

    # UP = too much, DOWN = not enough
    needle_y = center_y - normalized * (bar_h / 2.0)
    needle_h = 14 * s

    # Clamp to bar
    needle_y = max(bar_y + needle_h + 2, min(bar_y + bar_h - needle_h - 2, needle_y))

    # Color gradient
    abs_n = abs(normalized)
    if abs_n < 0.2:
        nr, ng, nb = 0.3, 1.0, 0.3
    elif abs_n < 0.55:
        t = (abs_n - 0.2) / 0.35
        nr = 0.3 + 0.7 * t
        ng = 1.0 - 0.3 * t
        nb = 0.3 * (1.0 - t)
    else:
        t = min(1.0, (abs_n - 0.55) / 0.45)
        nr = 1.0
        ng = 0.7 * (1.0 - t)
        nb = 0.1 * (1.0 - t)

    # White outline
    ac.glBegin(3)
    ac.glColor4f(1.0, 1.0, 1.0, 1.0)
    ac.glVertex2f(bar_x, needle_y - needle_h - 2)
    ac.glVertex2f(bar_x + bar_w, needle_y - needle_h - 2)
    ac.glVertex2f(bar_x + bar_w, needle_y + needle_h + 2)
    ac.glVertex2f(bar_x, needle_y + needle_h + 2)
    ac.glEnd()

    # Colored fill
    ac.glBegin(3)
    ac.glColor4f(nr, ng, nb, 1.0)
    ac.glVertex2f(bar_x + 2, needle_y - needle_h)
    ac.glVertex2f(bar_x + bar_w - 2, needle_y - needle_h)
    ac.glVertex2f(bar_x + bar_w - 2, needle_y + needle_h)
    ac.glVertex2f(bar_x + 2, needle_y + needle_h)
    ac.glEnd()
