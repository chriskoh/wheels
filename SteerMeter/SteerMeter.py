import ac
import acsys
import math

app = "SteerMeter"
appWindow = 0

APP_WIDTH = 200
APP_HEIGHT = 200

# Drift detection
DRIFT_ANGLE_MIN = 5.0
STEERING_RATIO = 14.0

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
    """Draw an arc as a line strip."""
    if abs(end_deg - start_deg) < 0.5:
        return
    ac.glBegin(1)
    ac.glColor4f(r, g, b, a)
    for i in range(steps + 1):
        t = float(i) / steps
        angle = math.radians(start_deg + t * (end_deg - start_deg))
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        ac.glVertex2f(x, y)
    ac.glEnd()


def draw_arc_filled(cx, cy, r_inner, r_outer, start_deg, end_deg, steps, r, g, b, a):
    """Draw a filled arc band using quads between inner and outer radius."""
    if abs(end_deg - start_deg) < 0.5:
        return
    for i in range(steps):
        t0 = float(i) / steps
        t1 = float(i + 1) / steps
        a0 = math.radians(start_deg + t0 * (end_deg - start_deg))
        a1 = math.radians(start_deg + t1 * (end_deg - start_deg))

        ix0 = cx + r_inner * math.cos(a0)
        iy0 = cy + r_inner * math.sin(a0)
        ox0 = cx + r_outer * math.cos(a0)
        oy0 = cy + r_outer * math.sin(a0)
        ix1 = cx + r_inner * math.cos(a1)
        iy1 = cy + r_inner * math.sin(a1)
        ox1 = cx + r_outer * math.cos(a1)
        oy1 = cy + r_outer * math.sin(a1)

        ac.glBegin(3)
        ac.glColor4f(r, g, b, a)
        ac.glVertex2f(ix0, iy0)
        ac.glVertex2f(ox0, oy0)
        ac.glVertex2f(ox1, oy1)
        ac.glVertex2f(ix1, iy1)
        ac.glEnd()


def draw_needle(cx, cy, r_inner, r_outer, angle_deg, r, g, b, a, width=3.0):
    """Draw a radial needle line at a given angle."""
    rad = math.radians(angle_deg)
    x0 = cx + r_inner * math.cos(rad)
    y0 = cy + r_inner * math.sin(rad)
    x1 = cx + r_outer * math.cos(rad)
    y1 = cy + r_outer * math.sin(rad)

    # Draw as a thin quad for visibility
    hw = width / 2.0
    perp_x = -math.sin(rad) * hw
    perp_y = math.cos(rad) * hw

    ac.glBegin(3)
    ac.glColor4f(r, g, b, a)
    ac.glVertex2f(x0 - perp_x, y0 - perp_y)
    ac.glVertex2f(x0 + perp_x, y0 + perp_y)
    ac.glVertex2f(x1 + perp_x, y1 + perp_y)
    ac.glVertex2f(x1 - perp_x, y1 - perp_y)
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
        px = -math.sin(rad) * hw
        py = math.cos(rad) * hw
        ac.glBegin(3)
        ac.glColor4f(0.5, 0.5, 0.5, 0.7)
        ac.glVertex2f(x0 - px, y0 - py)
        ac.glVertex2f(x0 + px, y0 + py)
        ac.glVertex2f(x1 + px, y1 + py)
        ac.glVertex2f(x1 - px, y1 - py)
        ac.glEnd()
    draw_arc(cx, cy, spoke_inner, 0, 360, 24, 0.5, 0.5, 0.5, 0.6)


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

    # Current steer needle on the rim
    current_angle_deg = -90.0 + steer_display

    # Draw current steer needle (white, bright)
    draw_needle(cx, cy, wheel_r - band_w - 4 * s, wheel_r + 6 * s,
                current_angle_deg, 1.0, 1.0, 1.0, 1.0, 3.0 * s)

    if not is_drifting:
        return

    # --- Compute safe steering zone ---
    # The ideal counter-steer angle at the wheels ≈ -slip_angle
    # (slip positive = nose left of travel, need steer right = positive steer)
    # But the "ideal" is a range, not a point.

    # Base ideal: counter-steer matches slip angle
    ideal_steer = -slip_angle * STEERING_RATIO  # back to steering wheel degrees

    # Zone width: how much margin around ideal
    # Narrower at high speed and high throttle (less forgiving)
    base_zone_width = 60.0  # degrees of steering wheel
    speed_factor = max(0.4, 1.0 - (speed - 40.0) * 0.004)  # shrinks above 40km/h
    throttle_factor = max(0.5, 1.0 - (gas - 0.3) * 0.5)    # shrinks above 30% gas
    zone_width = base_zone_width * speed_factor * throttle_factor

    zone_inner_steer = ideal_steer - zone_width / 2.0  # tighten edge
    zone_outer_steer = ideal_steer + zone_width / 2.0  # extend edge

    # Convert to display angles
    zone_inner_deg = -90.0 + max(-180.0, min(180.0, zone_inner_steer))
    zone_outer_deg = -90.0 + max(-180.0, min(180.0, zone_outer_steer))

    # Make sure inner < outer for drawing
    arc_start = min(zone_inner_deg, zone_outer_deg)
    arc_end = max(zone_inner_deg, zone_outer_deg)

    # Draw green safe zone arc band
    draw_arc_filled(cx, cy, wheel_r - band_w, wheel_r,
                    arc_start, arc_end, 24, 0.1, 0.6, 0.1, 0.5)

    # Draw zone edges (brighter green lines)
    draw_arc(cx, cy, wheel_r - band_w, arc_start, arc_start + 0.1, 1, 0.3, 1.0, 0.3, 0.8)
    draw_needle(cx, cy, wheel_r - band_w - 2 * s, wheel_r + 2 * s,
                arc_start, 0.3, 1.0, 0.3, 0.6, 2.0 * s)
    draw_needle(cx, cy, wheel_r - band_w - 2 * s, wheel_r + 2 * s,
                arc_end, 0.3, 1.0, 0.3, 0.6, 2.0 * s)

    # Redraw current needle on top so it's always visible
    draw_needle(cx, cy, wheel_r - band_w - 4 * s, wheel_r + 6 * s,
                current_angle_deg, 1.0, 1.0, 1.0, 1.0, 3.0 * s)
