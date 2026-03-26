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
STEERING_RATIO = 14.0

# Smoothing
prev_slip_angle = 0.0
prev_speed = 0.0
angle_rate_smooth = 0.0
speed_rate_smooth = 0.0
throttle_signal = 0.0
prev_needle_pos = 0.0

# Scale
scale = 1.8
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
    steer = 0.0
    try:
        speed = ac.getCarState(car, acsys.CS.SpeedKMH)
    except Exception:
        pass
    try:
        steer = ac.getCarState(car, acsys.CS.Steer)
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

    # Base throttle signal
    base_signal = angle_rate_smooth + speed_rate_smooth * 6.0

    # Steer cross-influence: under-countering means throttle is effectively "too much"
    steer_cross = 0.0
    if abs_angle > 10.0:
        tire_angle = abs(steer) / STEERING_RATIO
        steer_coverage = tire_angle / max(abs_angle, 1.0)
        # coverage < 1 = under-countering, nudge throttle signal positive (too much gas)
        # coverage > 1 = over-countering, nudge throttle signal negative (can add gas)
        steer_cross = (1.0 - steer_coverage) * 3.0

    throttle_signal = base_signal + steer_cross

    is_drifting = abs_angle > DRIFT_ANGLE_MIN

    draw_vertical_meter(is_drifting)


def draw_vertical_meter(active):
    """Vertical bar: black background, green target zone, white needle."""
    s = scale
    bar_x = 5 * s
    bar_y = 22 * s
    bar_w = (APP_WIDTH - 10) * s
    bar_h = (APP_HEIGHT - 30) * s
    center_y = bar_y + bar_h / 2.0

    # Black background
    ac.glBegin(3)
    ac.glColor4f(0.08, 0.08, 0.08, 1.0)
    ac.glVertex2f(bar_x, bar_y)
    ac.glVertex2f(bar_x + bar_w, bar_y)
    ac.glVertex2f(bar_x + bar_w, bar_y + bar_h)
    ac.glVertex2f(bar_x, bar_y + bar_h)
    ac.glEnd()

    # Green target zone in center (30%)
    zone_h = bar_h * 0.30
    zone_top = center_y - zone_h / 2
    zone_bot = center_y + zone_h / 2
    ac.glBegin(3)
    ac.glColor4f(0.1, 0.4, 0.1, 1.0)
    ac.glVertex2f(bar_x, zone_top)
    ac.glVertex2f(bar_x + bar_w, zone_top)
    ac.glVertex2f(bar_x + bar_w, zone_bot)
    ac.glVertex2f(bar_x, zone_bot)
    ac.glEnd()

    # Zone border lines
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

    # Map combined throttle signal to position
    clamped = max(-160.0, min(160.0, throttle_signal))
    normalized = clamped / 160.0

    # Smooth needle movement per frame
    global prev_needle_pos
    max_move = 0.03
    delta = normalized - prev_needle_pos
    if abs(delta) > max_move:
        normalized = prev_needle_pos + max_move * (1.0 if delta > 0 else -1.0)
    prev_needle_pos = normalized

    # UP = too much, DOWN = not enough
    needle_y = center_y - normalized * (bar_h / 2.0)
    needle_h = 8 * s
    needle_y = max(bar_y + needle_h + 2, min(bar_y + bar_h - needle_h - 2, needle_y))

    # Needle color: green in zone, red outside
    in_zone = abs(normalized) < 0.15
    if in_zone:
        nr, ng, nb = 0.3, 1.0, 0.3
    else:
        nr, ng, nb = 1.0, 0.2, 0.2

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
