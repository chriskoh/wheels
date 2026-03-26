import ac
import acsys
import math

app = "ThrottleMeter"
appWindow = 0
thr_label = 0

APP_WIDTH = 30
APP_HEIGHT = 400

# Drift detection
DRIFT_ANGLE_MIN = 5.0

# Smoothing
prev_slip_angle = 0.0
prev_speed = 0.0
angle_rate_smooth = 0.0
speed_rate_smooth = 0.0
throttle_signal = 0.0
prev_needle_pos = 0.0

# Scale
scale = 2.4
SCALE_STEP = 0.05
SCALE_MIN = 0.3
SCALE_MAX = 4.0
btn_increase = 0
btn_decrease = 0


def acMain(ac_version):
    global appWindow, btn_increase, btn_decrease, thr_label

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

    thr_label = ac.addLabel(appWindow, "0")
    ac.setPosition(thr_label, 2, APP_HEIGHT - 18)
    ac.setFontSize(thr_label, 10)
    ac.setFontColor(thr_label, 0.7, 0.7, 0.7, 1.0)

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
    global prev_slip_angle, prev_speed
    global angle_rate_smooth, speed_rate_smooth, throttle_signal

    ac.setBackgroundOpacity(appWindow, 0.0)

    car = ac.getFocusedCar()
    slip_angle = get_body_slip_angle(car)
    abs_angle = abs(slip_angle)

    speed = 0.0
    try:
        speed = ac.getCarState(car, acsys.CS.SpeedKMH)
    except Exception:
        pass

    # Angle rate of change (deg/s)
    if deltaT > 0:
        raw_angle_rate = (abs_angle - abs(prev_slip_angle)) / deltaT
        raw_speed_rate = (speed - prev_speed) / deltaT
    else:
        raw_angle_rate = 0.0
        raw_speed_rate = 0.0
    prev_slip_angle = slip_angle
    prev_speed = speed

    angle_rate_smooth = angle_rate_smooth * 0.92 + raw_angle_rate * 0.08
    speed_rate_smooth = speed_rate_smooth * 0.92 + raw_speed_rate * 0.08

    throttle_signal = angle_rate_smooth + speed_rate_smooth * 4.0

    is_drifting = abs_angle > DRIFT_ANGLE_MIN

    draw_vertical_meter(is_drifting)


def draw_vertical_meter(active):
    """Vertical bar with 5 zones. Top to bottom: red (spin) | orange (extending) | green (stable) | cyan (tightening) | blue (grip-up)"""
    s = scale
    bar_x = 5 * s
    bar_y = 22 * s
    bar_w = (APP_WIDTH - 10) * s
    bar_h = (APP_HEIGHT - 30) * s
    center_y = bar_y + bar_h / 2.0

    # Zone boundaries (fraction of half-height from center)
    # top: DARK RED (spin) | orange (extending) | GREEN (stable) | cyan (tightening) | DARK RED (dead) :bottom
    green_frac = 0.175
    mid_frac = 0.50

    green_hh = bar_h * green_frac
    mid_hh = bar_h * mid_frac

    # Red zone (top — spin/dead)
    ac.glBegin(3)
    ac.glColor4f(0.6, 0.05, 0.05, 1.0)
    ac.glVertex2f(bar_x, bar_y)
    ac.glVertex2f(bar_x + bar_w, bar_y)
    ac.glVertex2f(bar_x + bar_w, center_y - mid_hh)
    ac.glVertex2f(bar_x, center_y - mid_hh)
    ac.glEnd()

    # Orange zone (upper — extending)
    ac.glBegin(3)
    ac.glColor4f(0.5, 0.25, 0.0, 1.0)
    ac.glVertex2f(bar_x, center_y - mid_hh)
    ac.glVertex2f(bar_x + bar_w, center_y - mid_hh)
    ac.glVertex2f(bar_x + bar_w, center_y - green_hh)
    ac.glVertex2f(bar_x, center_y - green_hh)
    ac.glEnd()

    # Green zone (center — stable)
    ac.glBegin(3)
    ac.glColor4f(0.1, 0.4, 0.1, 1.0)
    ac.glVertex2f(bar_x, center_y - green_hh)
    ac.glVertex2f(bar_x + bar_w, center_y - green_hh)
    ac.glVertex2f(bar_x + bar_w, center_y + green_hh)
    ac.glVertex2f(bar_x, center_y + green_hh)
    ac.glEnd()

    # Cyan zone (lower — tightening)
    ac.glBegin(3)
    ac.glColor4f(0.0, 0.3, 0.4, 1.0)
    ac.glVertex2f(bar_x, center_y + green_hh)
    ac.glVertex2f(bar_x + bar_w, center_y + green_hh)
    ac.glVertex2f(bar_x + bar_w, center_y + mid_hh)
    ac.glVertex2f(bar_x, center_y + mid_hh)
    ac.glEnd()

    # Red zone (bottom — grip-up/dead)
    ac.glBegin(3)
    ac.glColor4f(0.6, 0.05, 0.05, 1.0)
    ac.glVertex2f(bar_x, center_y + mid_hh)
    ac.glVertex2f(bar_x + bar_w, center_y + mid_hh)
    ac.glVertex2f(bar_x + bar_w, bar_y + bar_h)
    ac.glVertex2f(bar_x, bar_y + bar_h)
    ac.glEnd()

    # Zone border lines
    for by in [center_y - mid_hh, center_y - green_hh, center_y + green_hh, center_y + mid_hh]:
        ac.glBegin(0)
        ac.glColor4f(0.5, 0.5, 0.5, 0.4)
        ac.glVertex2f(bar_x, by)
        ac.glVertex2f(bar_x + bar_w, by)
        ac.glEnd()

    if not active:
        return

    # Map combined throttle signal to position
    clamped = max(-160.0, min(160.0, throttle_signal))
    normalized = clamped / 160.0

    # Smooth needle movement per frame to prevent jitter
    global prev_needle_pos
    max_move = 0.03
    delta = normalized - prev_needle_pos
    if abs(delta) > max_move:
        normalized = prev_needle_pos + max_move * (1.0 if delta > 0 else -1.0)
    prev_needle_pos = normalized

    # UP = too much, DOWN = not enough
    needle_y = center_y - normalized * (bar_h / 2.0)
    needle_h = 8 * s

    # Clamp to bar
    needle_y = max(bar_y + needle_h + 2, min(bar_y + bar_h - needle_h - 2, needle_y))

    # Needle color matches zone
    abs_n = abs(normalized)
    if abs_n < green_frac:
        nr, ng, nb = 0.3, 1.0, 0.3       # green
    elif abs_n < mid_frac:
        if normalized > 0:
            nr, ng, nb = 1.0, 0.6, 0.0    # orange (extending, up)
        else:
            nr, ng, nb = 0.0, 0.8, 0.9    # cyan (tightening, down)
    else:
        nr, ng, nb = 1.0, 0.1, 0.1        # red (danger, either side)

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
