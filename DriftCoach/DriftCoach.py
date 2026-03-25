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
throttle_label = 0
btn_increase = 0
btn_decrease = 0

BASE_WIDTH = 280
BASE_HEIGHT = 320

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
angle_rate = 0.0

# Drift states
GRIP = 0
INITIATING = 1
SUSTAINING = 2
SPINNING = 3
state_names = ["GRIP", "INITIATING", "DRIFTING", "SPINNING"]


def acMain(ac_version):
    global appWindow
    global slip_angle_label, slip_value_label, state_label
    global countersteer_label, yaw_label, stats_label, throttle_label
    global btn_increase, btn_decrease

    appWindow = ac.newApp(app)
    ac.setSize(appWindow, BASE_WIDTH, BASE_HEIGHT)
    ac.setTitle(appWindow, "")
    ac.setIconPosition(appWindow, 0, -10000)
    ac.setBackgroundOpacity(appWindow, 0.7)
    ac.drawBorder(appWindow, 0)

    # Size buttons
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

    # Drift angle title
    slip_angle_label = ac.addLabel(appWindow, "DRIFT ANGLE")
    ac.setPosition(slip_angle_label, BASE_WIDTH // 2 - 50, 5)
    ac.setFontSize(slip_angle_label, 14)
    ac.setFontColor(slip_angle_label, 0.7, 0.7, 0.7, 1.0)

    # Big drift angle value
    slip_value_label = ac.addLabel(appWindow, "0.0")
    ac.setPosition(slip_value_label, BASE_WIDTH // 2 - 40, 25)
    ac.setFontSize(slip_value_label, 42)
    ac.setFontColor(slip_value_label, 1.0, 1.0, 1.0, 1.0)

    # Drift state
    state_label = ac.addLabel(appWindow, "GRIP")
    ac.setPosition(state_label, BASE_WIDTH // 2 - 40, 80)
    ac.setFontSize(state_label, 22)
    ac.setFontColor(state_label, 0.5, 1.0, 0.5, 1.0)

    # Counter-steer info
    countersteer_label = ac.addLabel(appWindow, "STEER: ---")
    ac.setPosition(countersteer_label, 10, 115)
    ac.setFontSize(countersteer_label, 16)
    ac.setFontColor(countersteer_label, 1.0, 1.0, 1.0, 1.0)

    # Yaw rate
    yaw_label = ac.addLabel(appWindow, "YAW: 0.0")
    ac.setPosition(yaw_label, 10, 140)
    ac.setFontSize(yaw_label, 16)
    ac.setFontColor(yaw_label, 1.0, 1.0, 1.0, 1.0)

    # Throttle coach
    throttle_label = ac.addLabel(appWindow, "THROTTLE: ---")
    ac.setPosition(throttle_label, 10, 165)
    ac.setFontSize(throttle_label, 16)
    ac.setFontColor(throttle_label, 0.6, 0.6, 0.6, 1.0)

    # Session stats
    stats_label = ac.addLabel(appWindow, "")
    ac.setPosition(stats_label, 10, 195)
    ac.setFontSize(stats_label, 13)
    ac.setFontColor(stats_label, 0.7, 0.7, 0.7, 1.0)

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

    # Reposition and resize labels
    ac.setPosition(slip_angle_label, w // 2 - int(50 * s), int(5 * s))
    ac.setFontSize(slip_angle_label, int(14 * s))

    ac.setPosition(slip_value_label, w // 2 - int(40 * s), int(25 * s))
    ac.setFontSize(slip_value_label, int(42 * s))

    ac.setPosition(state_label, w // 2 - int(40 * s), int(80 * s))
    ac.setFontSize(state_label, int(22 * s))

    ac.setPosition(countersteer_label, int(10 * s), int(115 * s))
    ac.setFontSize(countersteer_label, int(16 * s))

    ac.setPosition(yaw_label, int(10 * s), int(140 * s))
    ac.setFontSize(yaw_label, int(16 * s))

    ac.setPosition(throttle_label, int(10 * s), int(165 * s))
    ac.setFontSize(throttle_label, int(16 * s))

    ac.setPosition(stats_label, int(10 * s), int(195 * s))
    ac.setFontSize(stats_label, int(13 * s))


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
    global prev_slip_angle, angle_rate

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

    # Slip angle display
    r, g, b = angle_to_color(slip_angle)
    ac.setFontColor(slip_value_label, r, g, b, 1.0)
    ac.setText(slip_value_label, "{:.1f}".format(abs_angle))

    # State display
    sr, sg, sb = state_color(drift_state)
    ac.setFontColor(state_label, sr, sg, sb, 1.0)
    ac.setText(state_label, state_names[drift_state])

    # Counter-steer
    is_drifting = drift_state == SUSTAINING or drift_state == INITIATING
    if is_drifting and abs_angle > DRIFT_ANGLE_MIN:
        is_counter = (slip_angle > 0 and steer > 0) or (slip_angle < 0 and steer < 0)
        steer_ratio = abs(steer) / max(abs_angle * 14.0, 1.0)
        if is_counter:
            if steer_ratio < 0.5:
                ac.setText(countersteer_label, "COUNTER: MORE")
                ac.setFontColor(countersteer_label, 1.0, 0.6, 0.2, 1.0)
            elif steer_ratio > 1.5:
                ac.setText(countersteer_label, "COUNTER: LESS")
                ac.setFontColor(countersteer_label, 1.0, 0.6, 0.2, 1.0)
            else:
                ac.setText(countersteer_label, "COUNTER: GOOD")
                ac.setFontColor(countersteer_label, 0.3, 1.0, 0.3, 1.0)
        else:
            ac.setText(countersteer_label, "NO COUNTER")
            ac.setFontColor(countersteer_label, 1.0, 0.2, 0.2, 1.0)
    else:
        ac.setText(countersteer_label, "STEER: ---")
        ac.setFontColor(countersteer_label, 0.6, 0.6, 0.6, 1.0)

    # Yaw rate
    abs_yaw = abs(yaw_rate)
    if abs_yaw > YAW_SPIN_THRESHOLD:
        ac.setFontColor(yaw_label, 1.0, 0.2, 0.2, 1.0)
    elif abs_yaw > 1.5:
        ac.setFontColor(yaw_label, 1.0, 1.0, 0.3, 1.0)
    else:
        ac.setFontColor(yaw_label, 0.7, 0.7, 0.7, 1.0)
    ac.setText(yaw_label, "YAW: {:.1f}".format(yaw_rate))

    # === THROTTLE COACH ===
    throttle = 0.0
    try:
        throttle = ac.getCarState(car, acsys.CS.Gas)
    except Exception:
        pass

    # Track angle rate of change (degrees per second)
    if deltaT > 0:
        angle_rate = (abs_angle - abs(prev_slip_angle)) / deltaT
    else:
        angle_rate = 0.0
    prev_slip_angle = slip_angle

    if is_drifting and abs_angle > DRIFT_ANGLE_MIN:
        # angle_rate > 0 means angle is growing (more sideways)
        # angle_rate < 0 means angle is shrinking (drift dying)
        if angle_rate < -15.0:
            # Angle dropping fast — drift is dying
            ac.setText(throttle_label, "THROTTLE: MORE")
            ac.setFontColor(throttle_label, 1.0, 0.5, 0.1, 1.0)
        elif angle_rate > 20.0:
            # Angle growing fast — about to spin
            ac.setText(throttle_label, "THROTTLE: LESS")
            ac.setFontColor(throttle_label, 1.0, 0.2, 0.2, 1.0)
        else:
            # Angle is stable-ish
            ac.setText(throttle_label, "THROTTLE: GOOD")
            ac.setFontColor(throttle_label, 0.3, 1.0, 0.3, 1.0)
    else:
        ac.setText(throttle_label, "THROTTLE: ---")
        ac.setFontColor(throttle_label, 0.6, 0.6, 0.6, 1.0)

    # Session stats
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

    # Draw arc
    draw_angle_arc(slip_angle)


def draw_angle_arc(slip_angle):
    s = scale
    cx = (BASE_WIDTH * s) / 2.0
    cy = 95.0 * s
    radius = 60.0 * s
    abs_angle = abs(slip_angle)

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
