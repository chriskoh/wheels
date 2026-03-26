import ac
import acsys
import math

app = "SteerMeter"
appWindow = 0

APP_WIDTH = 200
APP_HEIGHT = 200

DRIFT_ANGLE_MIN = 5.0
STEERING_RATIO = 14.0
MAX_STEER_LOCK = 450.0

scale = 1.0
SCALE_STEP = 0.1
SCALE_MIN = 0.5
SCALE_MAX = 3.0
btn_increase = 0
btn_decrease = 0

# Smoothing
prev_slip_angle = 0.0
angle_rate_smooth = 0.0


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

def get_body_slip_angle(car):
    try:
        lv = ac.getCarState(car, acsys.CS.LocalVelocity)
        speed = ac.getCarState(car, acsys.CS.SpeedKMH)
        if speed < 5.0:
            return 0.0
        return math.degrees(math.atan2(lv[0], abs(lv[2])))
    except Exception:
        return 0.0

def draw_arc(cx, cy, radius, start_deg, end_deg, steps, r, g, b, a):
    if abs(end_deg - start_deg) < 0.5:
        return
    ac.glBegin(1)
    ac.glColor4f(r, g, b, a)
    for i in range(steps + 1):
        t = float(i) / steps
        ang = math.radians(start_deg + t * (end_deg - start_deg))
        ac.glVertex2f(cx + radius * math.cos(ang), cy + radius * math.sin(ang))
    ac.glEnd()

def draw_arc_filled(cx, cy, ri, ro, start_deg, end_deg, steps, r, g, b, a):
    if abs(end_deg - start_deg) < 0.5:
        return
    for i in range(steps):
        t0 = float(i) / steps
        t1 = float(i + 1) / steps
        a0 = math.radians(start_deg + t0 * (end_deg - start_deg))
        a1 = math.radians(start_deg + t1 * (end_deg - start_deg))
        ac.glBegin(3)
        ac.glColor4f(r, g, b, a)
        ac.glVertex2f(cx + ri * math.cos(a0), cy + ri * math.sin(a0))
        ac.glVertex2f(cx + ro * math.cos(a0), cy + ro * math.sin(a0))
        ac.glVertex2f(cx + ro * math.cos(a1), cy + ro * math.sin(a1))
        ac.glVertex2f(cx + ri * math.cos(a1), cy + ri * math.sin(a1))
        ac.glEnd()

def draw_needle(cx, cy, ri, ro, angle_deg, r, g, b, a, width=3.0):
    rad = math.radians(angle_deg)
    hw = width / 2.0
    px = -math.sin(rad) * hw
    py = math.cos(rad) * hw
    x0 = cx + ri * math.cos(rad)
    y0 = cy + ri * math.sin(rad)
    x1 = cx + ro * math.cos(rad)
    y1 = cy + ro * math.sin(rad)
    ac.glBegin(3)
    ac.glColor4f(r, g, b, a)
    ac.glVertex2f(x0 - px, y0 - py)
    ac.glVertex2f(x0 + px, y0 + py)
    ac.glVertex2f(x1 + px, y1 + py)
    ac.glVertex2f(x1 - px, y1 - py)
    ac.glEnd()

def draw_steering_wheel(cx, cy, radius, steer_rad, s):
    draw_arc(cx, cy, radius, 0, 360, 48, 0.6, 0.6, 0.6, 0.8)
    draw_arc(cx, cy, radius - 2 * s, 0, 360, 48, 0.35, 0.35, 0.35, 0.5)
    spoke_inner = 18.0 * s
    spoke_outer = radius - 3 * s
    spoke_w = 3.0 * s
    for spoke_base_deg in [90, 210, 330]:
        rad = steer_rad + math.radians(spoke_base_deg)
        x0 = cx + spoke_inner * math.cos(rad)
        y0 = cy + spoke_inner * math.sin(rad)
        x1 = cx + spoke_outer * math.cos(rad)
        y1 = cy + spoke_outer * math.sin(rad)
        hw = spoke_w / 2.0
        ppx = -math.sin(rad) * hw
        ppy = math.cos(rad) * hw
        ac.glBegin(3)
        ac.glColor4f(0.5, 0.5, 0.5, 0.7)
        ac.glVertex2f(x0 - ppx, y0 - ppy)
        ac.glVertex2f(x0 + ppx, y0 + ppy)
        ac.glVertex2f(x1 + ppx, y1 + ppy)
        ac.glVertex2f(x1 - ppx, y1 - ppy)
        ac.glEnd()
    draw_arc(cx, cy, spoke_inner, 0, 360, 24, 0.5, 0.5, 0.5, 0.6)

def steer_to_display(steer_wheel_deg):
    norm = max(-1.0, min(1.0, steer_wheel_deg / MAX_STEER_LOCK))
    return -90.0 + norm * 120.0


def onFormRender(deltaT):
    global prev_slip_angle, angle_rate_smooth

    ac.setBackgroundOpacity(appWindow, 0.0)
    car = ac.getFocusedCar()
    slip_angle = get_body_slip_angle(car)
    abs_angle = abs(slip_angle)

    steer = 0.0
    try:
        steer = ac.getCarState(car, acsys.CS.Steer)
    except Exception:
        pass

    # Track angle rate (using signed slip so we know direction)
    if deltaT > 0:
        raw_rate = (slip_angle - prev_slip_angle) / deltaT
    else:
        raw_rate = 0.0
    prev_slip_angle = slip_angle
    angle_rate_smooth = angle_rate_smooth * 0.88 + raw_rate * 0.12

    is_drifting = abs_angle > DRIFT_ANGLE_MIN

    s = scale
    cx = APP_WIDTH / 2.0
    cy = APP_HEIGHT / 2.0
    wheel_r = 70.0 * s
    band_w = 14.0 * s

    # Draw steering wheel
    steer_display = max(-180.0, min(180.0, steer))
    steer_rad = math.radians(steer_display)
    draw_steering_wheel(cx, cy, wheel_r, steer_rad, s)

    if not is_drifting:
        return

    # Determine which direction to steer based on what the drift is doing.
    #
    # angle_rate_smooth: positive = slip angle growing positive (nose going more left)
    #                    negative = slip angle growing negative (nose going more right)
    #
    # If slip_angle > 0 (nose left of travel = drifting left):
    #   angle_rate > 0 = drift opening  -> need more RIGHT steer (counter-steer) to catch
    #   angle_rate < 0 = drift tightening -> could steer more LEFT to open it
    #
    # If slip_angle < 0 (nose right of travel = drifting right):
    #   angle_rate < 0 = drift opening  -> need more LEFT steer (counter-steer) to catch
    #   angle_rate > 0 = drift tightening -> could steer more RIGHT to open it
    #
    # Simplification: the sign of angle_rate tells us which way the nose is moving.
    # Positive rate = nose moving left = steer RIGHT to counter.
    # Negative rate = nose moving right = steer LEFT to counter.
    #
    # So: direction to steer = opposite sign of angle_rate
    # On the display: positive steer = right = clockwise on screen

    # How urgent is the correction? Map rate magnitude to arc size
    rate_magnitude = abs(angle_rate_smooth)

    # Dead zone: if rate is small, drift is stable -> show green center
    if rate_magnitude < 3.0:
        # Stable - show small green arc at top (12 o'clock)
        draw_arc_filled(cx, cy, wheel_r - band_w, wheel_r,
                        -100, -80, 8, 0.1, 0.6, 0.1, 0.6)
        return

    # Map rate to arc sweep (bigger rate = bigger/brighter indicator)
    sweep = min(60.0, rate_magnitude * 2.0)  # max 60 degrees of arc
    intensity = min(1.0, rate_magnitude / 30.0)

    # Direction: steer opposite to angle_rate to counter
    # angle_rate > 0 -> nose going left -> steer right -> positive on display
    # On display: -90 = top, 0 = right, -180 = left
    if angle_rate_smooth > 0:
        # Need to steer RIGHT -> show arc on the right side
        arc_start = -90.0
        arc_end = -90.0 + sweep
        r, g, b = 1.0 * intensity, 0.5 * (1.0 - intensity), 0.0
    else:
        # Need to steer LEFT -> show arc on the left side
        arc_start = -90.0 - sweep
        arc_end = -90.0
        r, g, b = 1.0 * intensity, 0.5 * (1.0 - intensity), 0.0

    # Draw the directional indicator arc
    draw_arc_filled(cx, cy, wheel_r - band_w, wheel_r,
                    arc_start, arc_end, 16, r, g, b, 0.7)

    # Arrow tip at the leading edge
    if angle_rate_smooth > 0:
        tip_deg = arc_end
    else:
        tip_deg = arc_start
    draw_needle(cx, cy, wheel_r - band_w - 4 * s, wheel_r + 4 * s,
                tip_deg, r, g, b, 1.0, 4.0 * s)
