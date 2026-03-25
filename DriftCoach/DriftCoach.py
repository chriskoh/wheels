import ac
import acsys
import math

app = "DriftCoach"
appWindow = 0

# Labels
slip_angle_label = 0
slip_value_label = 0
state_label = 0
countersteer_label = 0
yaw_label = 0
stats_label = 0
throttle_title_label = 0
throttle_more_label = 0
throttle_less_label = 0
btn_increase = 0
btn_decrease = 0

BASE_WIDTH = 320
BASE_HEIGHT = 500

# Drift state thresholds
DRIFT_ANGLE_MIN = 5.0
DRIFT_ANGLE_INITIATE = 10.0
DRIFT_ANGLE_SPIN = 70.0
YAW_SPIN_THRESHOLD = 3.0

# Scale
scale = 1.0
SCALE_STEP = 0.1
SCALE_MIN = 0.6
SCALE_MAX = 2.0

# Session stats
stats_max_angle = 0.0
stats_longest_drift = 0.0
stats_current_drift_time = 0.0
stats_spin_count = 0
stats_drift_count = 0
was_drifting = False
was_spinning = False
prev_slip_angle = 0.0
prev_speed = 0.0
angle_rate_smooth = 0.0
speed_rate_smooth = 0.0
throttle_signal = 0.0

# Drift states
GRIP = 0
INITIATING = 1
SUSTAINING = 2
SPINNING = 3
state_names = ["GRIP", "INITIATING", "DRIFTING", "SPINNING"]


def acMain(ac_version):
    global appWindow
    global slip_angle_label, slip_value_label, state_label
    global countersteer_label, yaw_label, stats_label, throttle_title_label
    global throttle_more_label, throttle_less_label
    global btn_increase, btn_decrease

    appWindow = ac.newApp(app)
    ac.setSize(appWindow, BASE_WIDTH, BASE_HEIGHT)
    ac.setTitle(appWindow, "")
    ac.setIconPosition(appWindow, 0, -10000)
    ac.setBackgroundOpacity(appWindow, 0.7)
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

    slip_angle_label = ac.addLabel(appWindow, "DRIFT ANGLE")
    ac.setPosition(slip_angle_label, BASE_WIDTH // 2 - 55, 5)
    ac.setFontSize(slip_angle_label, 16)
    ac.setFontColor(slip_angle_label, 0.7, 0.7, 0.7, 1.0)

    slip_value_label = ac.addLabel(appWindow, "0.0")
    ac.setPosition(slip_value_label, BASE_WIDTH // 2 - 45, 28)
    ac.setFontSize(slip_value_label, 48)
    ac.setFontColor(slip_value_label, 1.0, 1.0, 1.0, 1.0)

    state_label = ac.addLabel(appWindow, "GRIP")
    ac.setPosition(state_label, BASE_WIDTH // 2 - 50, 90)
    ac.setFontSize(state_label, 28)
    ac.setFontColor(state_label, 0.5, 1.0, 0.5, 1.0)

    countersteer_label = ac.addLabel(appWindow, "STEER: ---")
    ac.setPosition(countersteer_label, 12, 135)
    ac.setFontSize(countersteer_label, 18)
    ac.setFontColor(countersteer_label, 1.0, 1.0, 1.0, 1.0)

    yaw_label = ac.addLabel(appWindow, "YAW: 0.0")
    ac.setPosition(yaw_label, 12, 165)
    ac.setFontSize(yaw_label, 18)
    ac.setFontColor(yaw_label, 1.0, 1.0, 1.0, 1.0)

    # Throttle meter title (the bar is drawn in GL)
    throttle_title_label = ac.addLabel(appWindow, "THROTTLE")
    ac.setPosition(throttle_title_label, 12, 205)
    ac.setFontSize(throttle_title_label, 24)
    ac.setFontColor(throttle_title_label, 1.0, 1.0, 1.0, 1.0)

    stats_label = ac.addLabel(appWindow, "")
    ac.setPosition(stats_label, 12, 300)
    ac.setFontSize(stats_label, 14)
    ac.setFontColor(stats_label, 0.7, 0.7, 0.7, 1.0)

    # Throttle bar direction labels
    throttle_more_label = ac.addLabel(appWindow, "MORE")
    ac.setPosition(throttle_more_label, 12, 282)
    ac.setFontSize(throttle_more_label, 11)
    ac.setFontColor(throttle_more_label, 0.5, 0.5, 0.5, 1.0)

    throttle_less_label = ac.addLabel(appWindow, "LESS")
    ac.setPosition(throttle_less_label, BASE_WIDTH - 45, 282)
    ac.setFontSize(throttle_less_label, 11)
    ac.setFontColor(throttle_less_label, 0.5, 0.5, 0.5, 1.0)

    ac.addRenderCallback(appWindow, onFormRender)
    ac.log("[" + app + "] Loaded")
    return app


def acUpdate(deltaT):
    pass


def onIncrease(*args):
    global scale
    if scale < SCALE_MAX:
        scale += SCALE_STEP
        apply_scale()


def onDecrease(*args):
    global scale
    if scale > SCALE_MIN:
        scale -= SCALE_STEP
        apply_scale()


def apply_scale():
    s = scale
    w = int(BASE_WIDTH * s)
    h = int(BASE_HEIGHT * s)
    ac.setSize(appWindow, w, h)

    ac.setPosition(slip_angle_label, w // 2 - int(55 * s), int(5 * s))
    ac.setFontSize(slip_angle_label, int(16 * s))
    ac.setPosition(slip_value_label, w // 2 - int(45 * s), int(28 * s))
    ac.setFontSize(slip_value_label, int(48 * s))
    ac.setPosition(state_label, w // 2 - int(50 * s), int(90 * s))
    ac.setFontSize(state_label, int(28 * s))
    ac.setPosition(countersteer_label, int(12 * s), int(135 * s))
    ac.setFontSize(countersteer_label, int(18 * s))
    ac.setPosition(yaw_label, int(12 * s), int(165 * s))
    ac.setFontSize(yaw_label, int(18 * s))
    ac.setPosition(throttle_title_label, int(12 * s), int(205 * s))
    ac.setFontSize(throttle_title_label, int(24 * s))
    ac.setPosition(stats_label, int(12 * s), int(300 * s))
    ac.setFontSize(stats_label, int(14 * s))


def get_body_slip_angle(car):
    try:
        lv = ac.getCarState(car, acsys.CS.LocalVelocity)
        speed = ac.getCarState(car, acsys.CS.SpeedKMH)
        if speed < 5.0:
            return 0.0
        return math.degrees(math.atan2(lv[0], abs(lv[2])))
    except Exception:
        return 0.0


def get_yaw_rate(car):
    try:
        av = ac.getCarState(car, acsys.CS.LocalAngularVelocity)
        return av[1]
    except Exception:
        return 0.0


def get_drift_state(slip_angle, yaw_rate):
    abs_angle = abs(slip_angle)
    abs_yaw = abs(yaw_rate)
    if abs_yaw > YAW_SPIN_THRESHOLD and abs_angle > DRIFT_ANGLE_SPIN:
        return SPINNING
    elif abs_angle > DRIFT_ANGLE_INITIATE:
        return SUSTAINING
    elif abs_angle > DRIFT_ANGLE_MIN:
        return INITIATING
    else:
        return GRIP


def angle_to_color(angle):
    a = abs(angle)
    if a < 20:
        return (0.5, 1.0, 0.5)
    elif a < 35:
        return (1.0, 1.0, 0.2)
    elif a < 50:
        return (1.0, 0.6, 0.1)
    elif a < DRIFT_ANGLE_SPIN:
        return (1.0, 0.3, 0.1)
    else:
        return (1.0, 0.0, 0.0)


def state_color(state):
    if state == GRIP:
        return (0.5, 1.0, 0.5)
    elif state == INITIATING:
        return (1.0, 1.0, 0.3)
    elif state == SUSTAINING:
        return (0.3, 0.8, 1.0)
    elif state == SPINNING:
        return (1.0, 0.1, 0.1)
    return (1.0, 1.0, 1.0)


def onFormRender(deltaT):
    global stats_max_angle, stats_longest_drift, stats_current_drift_time
    global stats_spin_count, stats_drift_count
    global was_drifting, was_spinning
    global prev_slip_angle, prev_speed
    global angle_rate_smooth, speed_rate_smooth, throttle_signal

    ac.setBackgroundOpacity(appWindow, 0.7)

    car = ac.getFocusedCar()
    slip_angle = get_body_slip_angle(car)
    yaw_rate = get_yaw_rate(car)
    steer = 0.0
    try:
        steer = ac.getCarState(car, acsys.CS.Steer)
    except Exception:
        pass

    drift_state = get_drift_state(slip_angle, yaw_rate)
    abs_angle = abs(slip_angle)
    is_drifting = drift_state == SUSTAINING or drift_state == INITIATING

    # === SLIP ANGLE DISPLAY ===
    r, g, b = angle_to_color(slip_angle)
    ac.setFontColor(slip_value_label, r, g, b, 1.0)
    ac.setText(slip_value_label, "{:.1f} ".format(abs_angle))

    # === STATE ===
    sr, sg, sb = state_color(drift_state)
    ac.setFontColor(state_label, sr, sg, sb, 1.0)
    ac.setText(state_label, state_names[drift_state])

    # === COUNTER-STEER ===
    # During a drift, you counter-steer: wheels point into the slide direction.
    # We check if steer opposes the slip angle sign (try both conventions).
    # Also detect if ANY significant steer is happening in the right direction.
    if is_drifting and abs_angle > DRIFT_ANGLE_MIN:
        # Try: counter-steer = steer sign OPPOSITE to slip sign
        # (if car slides right/positive, you steer left/negative to catch it)
        same_sign = (slip_angle > 0 and steer > 0) or (slip_angle < 0 and steer < 0)
        opp_sign = (slip_angle > 0 and steer < 0) or (slip_angle < 0 and steer > 0)

        abs_steer = abs(steer)
        # If steer is significant (more than 10 degrees)
        if abs_steer > 10:
            # We don't know the sign convention yet, so check both
            # The correct one is whichever makes the car NOT spin
            # Heuristic: if angle is stable or decreasing with this steer, it's counter
            if same_sign or opp_sign:
                ac.setText(countersteer_label, "COUNTER: {:.0f}".format(abs_steer))
                ac.setFontColor(countersteer_label, 0.3, 1.0, 0.3, 1.0)
            else:
                ac.setText(countersteer_label, "NO COUNTER")
                ac.setFontColor(countersteer_label, 1.0, 0.2, 0.2, 1.0)
        else:
            ac.setText(countersteer_label, "NO COUNTER")
            ac.setFontColor(countersteer_label, 1.0, 0.2, 0.2, 1.0)
    else:
        ac.setText(countersteer_label, "STEER: ---")
        ac.setFontColor(countersteer_label, 0.6, 0.6, 0.6, 1.0)

    # === YAW RATE ===
    abs_yaw = abs(yaw_rate)
    if abs_yaw > YAW_SPIN_THRESHOLD:
        ac.setFontColor(yaw_label, 1.0, 0.2, 0.2, 1.0)
    elif abs_yaw > 1.5:
        ac.setFontColor(yaw_label, 1.0, 1.0, 0.3, 1.0)
    else:
        ac.setFontColor(yaw_label, 0.7, 0.7, 0.7, 1.0)
    ac.setText(yaw_label, "YAW: {:.1f}/s".format(yaw_rate))

    # === THROTTLE SIGNAL (angle rate + speed rate) ===
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

    angle_rate_smooth = angle_rate_smooth * 0.85 + raw_angle_rate * 0.15
    speed_rate_smooth = speed_rate_smooth * 0.85 + raw_speed_rate * 0.15

    # Combined signal:
    # Positive = too much gas (angle growing fast, speed climbing)
    # Negative = not enough gas (angle shrinking, speed dropping)
    # Speed gets heavy weight — losing speed during a drift is critical
    throttle_signal = angle_rate_smooth + speed_rate_smooth * 4.0

    # Show signal value on the throttle label for debugging
    ac.setText(throttle_title_label, "THROTTLE")

    # Draw the throttle meter bar (done in GL below)
    # Also update session stats

    # === SESSION STATS ===
    currently_drifting = drift_state == SUSTAINING
    currently_spinning = drift_state == SPINNING

    if abs_angle > stats_max_angle and currently_drifting:
        stats_max_angle = abs_angle

    if currently_drifting:
        stats_current_drift_time += deltaT
        if not was_drifting:
            stats_drift_count += 1
    else:
        if was_drifting and stats_current_drift_time > stats_longest_drift:
            stats_longest_drift = stats_current_drift_time
        if not currently_drifting:
            stats_current_drift_time = 0.0

    if currently_spinning and not was_spinning:
        stats_spin_count += 1

    was_drifting = currently_drifting
    was_spinning = currently_spinning

    longest = max(stats_longest_drift, stats_current_drift_time)
    ac.setText(stats_label, "Max:{:.0f} Long:{:.1f}s Drft:{} Spin:{}".format(
        stats_max_angle, longest, stats_drift_count, stats_spin_count
    ))

    # === DRAW ===
    draw_angle_arc(slip_angle)
    draw_throttle_meter(is_drifting and abs_angle > DRIFT_ANGLE_MIN)


def draw_throttle_meter(active):
    """Draw a horizontal bar with a green target zone and a thick visible needle."""
    s = scale
    bar_y = 250 * s
    bar_x = 10 * s
    bar_w = (BASE_WIDTH - 20) * s
    bar_h = 30 * s
    center_x = bar_x + bar_w / 2.0

    # Background bar
    ac.glBegin(3)
    ac.glColor4f(0.1, 0.1, 0.1, 0.85)
    ac.glVertex2f(bar_x, bar_y)
    ac.glVertex2f(bar_x + bar_w, bar_y)
    ac.glVertex2f(bar_x + bar_w, bar_y + bar_h)
    ac.glVertex2f(bar_x, bar_y + bar_h)
    ac.glEnd()

    # Green target zone in center
    zone_w = bar_w * 0.35
    zone_left = center_x - zone_w / 2
    zone_right = center_x + zone_w / 2
    ac.glBegin(3)
    ac.glColor4f(0.1, 0.4, 0.1, 0.6)
    ac.glVertex2f(zone_left, bar_y)
    ac.glVertex2f(zone_right, bar_y)
    ac.glVertex2f(zone_right, bar_y + bar_h)
    ac.glVertex2f(zone_left, bar_y + bar_h)
    ac.glEnd()

    # Zone border lines
    ac.glBegin(0)
    ac.glColor4f(0.3, 1.0, 0.3, 0.8)
    ac.glVertex2f(zone_left, bar_y)
    ac.glVertex2f(zone_left, bar_y + bar_h)
    ac.glEnd()
    ac.glBegin(0)
    ac.glColor4f(0.3, 1.0, 0.3, 0.8)
    ac.glVertex2f(zone_right, bar_y)
    ac.glVertex2f(zone_right, bar_y + bar_h)
    ac.glEnd()

    if not active:
        return

    # Map angle_rate_smooth to position
    clamped = max(-80.0, min(80.0, throttle_signal))
    normalized = clamped / 80.0

    # Needle position — very chunky
    needle_x = center_x + normalized * (bar_w / 2.0)
    needle_w = 14 * s

    # Clamp needle to bar bounds
    needle_x = max(bar_x + needle_w + 2, min(bar_x + bar_w - needle_w - 2, needle_x))

    # Color based on distance from center
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
    ac.glVertex2f(needle_x - needle_w - 2, bar_y)
    ac.glVertex2f(needle_x + needle_w + 2, bar_y)
    ac.glVertex2f(needle_x + needle_w + 2, bar_y + bar_h)
    ac.glVertex2f(needle_x - needle_w - 2, bar_y + bar_h)
    ac.glEnd()

    # Colored needle fill
    ac.glBegin(3)
    ac.glColor4f(nr, ng, nb, 1.0)
    ac.glVertex2f(needle_x - needle_w, bar_y + 2)
    ac.glVertex2f(needle_x + needle_w, bar_y + 2)
    ac.glVertex2f(needle_x + needle_w, bar_y + bar_h - 2)
    ac.glVertex2f(needle_x - needle_w, bar_y + bar_h - 2)
    ac.glEnd()



def draw_angle_arc(slip_angle):
    s = scale
    cx = (BASE_WIDTH * s) / 2.0
    cy = 95.0 * s
    radius = 60.0 * s

    # Background arc
    ac.glBegin(1)
    ac.glColor4f(0.3, 0.3, 0.3, 0.5)
    for i in range(-90, 91, 5):
        x = cx + radius * math.cos(math.radians(i - 90))
        y = cy + radius * math.sin(math.radians(i - 90))
        ac.glVertex2f(x, y)
    ac.glEnd()

    # Center tick
    ac.glBegin(0)
    ac.glColor4f(0.6, 0.6, 0.6, 0.8)
    ac.glVertex2f(cx, cy - radius - 5 * s)
    ac.glVertex2f(cx, cy - radius + 5 * s)
    ac.glEnd()

    # Active arc
    abs_angle = abs(slip_angle)
    if abs_angle > 1.0:
        r, g, b = angle_to_color(slip_angle)
        ac.glBegin(1)
        ac.glColor4f(r, g, b, 0.9)
        display_angle = max(-80, min(80, slip_angle))
        steps = max(2, int(abs(display_angle) / 2))
        for i in range(steps + 1):
            a = (float(i) / steps) * display_angle
            x = cx + radius * math.cos(math.radians(a - 90))
            y = cy + radius * math.sin(math.radians(a - 90))
            ac.glVertex2f(x, y)
        ac.glEnd()

        # Pointer
        end_angle = max(-80, min(80, slip_angle))
        ac.glBegin(0)
        ac.glColor4f(r, g, b, 1.0)
        inner_x = cx + (radius - 8 * s) * math.cos(math.radians(end_angle - 90))
        inner_y = cy + (radius - 8 * s) * math.sin(math.radians(end_angle - 90))
        outer_x = cx + (radius + 8 * s) * math.cos(math.radians(end_angle - 90))
        outer_y = cy + (radius + 8 * s) * math.sin(math.radians(end_angle - 90))
        ac.glVertex2f(inner_x, inner_y)
        ac.glVertex2f(outer_x, outer_y)
        ac.glEnd()
