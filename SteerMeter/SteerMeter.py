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
    ac.setBackgroundOpacity(appWindow, 0.0)
    car = ac.getFocusedCar()
    slip_angle = get_body_slip_angle(car)
    abs_angle = abs(slip_angle)
    steer = 0.0
    gas = 0.0
    speed = 0.0
    try:
        steer = ac.getCarState(car, acsys.CS.Steer)
    except Exception:
        pass
    try:
        gas = ac.getCarState(car, acsys.CS.Gas)
    except Exception:
        pass
    try:
        speed = ac.getCarState(car, acsys.CS.SpeedKMH)
    except Exception:
        pass

    is_drifting = abs_angle > DRIFT_ANGLE_MIN
    s = scale
    cx = APP_WIDTH / 2.0
    cy = APP_HEIGHT / 2.0
    wheel_r = 70.0 * s
    band_w = 12.0 * s

    # Draw steering wheel (rotates with input)
    steer_display = max(-180.0, min(180.0, steer))
    steer_rad = math.radians(steer_display)
    draw_steering_wheel(cx, cy, wheel_r, steer_rad, s)

    # Current steer needle
    current_deg = steer_to_display(steer)
    draw_needle(cx, cy, wheel_r - band_w - 4 * s, wheel_r + 6 * s,
                current_deg, 1.0, 1.0, 1.0, 1.0, 3.0 * s)

    if not is_drifting:
        return

    # Safe steering zone — computed in tire angle space
    max_tire_angle = MAX_STEER_LOCK / STEERING_RATIO
    ideal_tire = -slip_angle
    ideal_tire = max(-max_tire_angle, min(max_tire_angle, ideal_tire))

    # Zone width in tire degrees
    base_width = 6.0
    speed_factor = max(0.4, 1.0 - (speed - 40.0) * 0.004)
    throttle_factor = max(0.5, 1.0 - (gas - 0.3) * 0.5)
    zone_half = (base_width * speed_factor * throttle_factor) / 2.0

    zone_lo_tire = ideal_tire - zone_half
    zone_hi_tire = ideal_tire + zone_half

    # Convert to steering wheel degrees then to display
    zone_lo_deg = steer_to_display(zone_lo_tire * STEERING_RATIO)
    zone_hi_deg = steer_to_display(zone_hi_tire * STEERING_RATIO)

    arc_start = min(zone_lo_deg, zone_hi_deg)
    arc_end = max(zone_lo_deg, zone_hi_deg)

    # Green safe zone arc
    draw_arc_filled(cx, cy, wheel_r - band_w, wheel_r,
                    arc_start, arc_end, 24, 0.1, 0.6, 0.1, 0.5)
    draw_needle(cx, cy, wheel_r - band_w - 2 * s, wheel_r + 2 * s,
                arc_start, 0.3, 1.0, 0.3, 0.6, 2.0 * s)
    draw_needle(cx, cy, wheel_r - band_w - 2 * s, wheel_r + 2 * s,
                arc_end, 0.3, 1.0, 0.3, 0.6, 2.0 * s)

    # Redraw steer needle on top
    draw_needle(cx, cy, wheel_r - band_w - 4 * s, wheel_r + 6 * s,
                current_deg, 1.0, 1.0, 1.0, 1.0, 3.0 * s)
