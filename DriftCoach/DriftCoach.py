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

APP_WIDTH = 280
APP_HEIGHT = 320

# Drift state thresholds
DRIFT_ANGLE_MIN = 5.0       # Below this = grip driving
DRIFT_ANGLE_INITIATE = 10.0 # Starting to slide
DRIFT_ANGLE_SPIN = 70.0     # Likely spinning out
YAW_SPIN_THRESHOLD = 3.0    # Yaw rate that suggests a spin (rad/s)

# Session stats
stats_max_angle = 0.0
stats_longest_drift = 0.0
stats_current_drift_time = 0.0
stats_spin_count = 0
stats_drift_count = 0
was_drifting = False
was_spinning = False

# Drift state
GRIP = 0
INITIATING = 1
SUSTAINING = 2
SPINNING = 3
state_names = ["GRIP", "INITIATING", "DRIFTING", "SPINNING"]


def acMain(ac_version):
    global appWindow
    global slip_angle_label, slip_value_label, state_label
    global countersteer_label, yaw_label, stats_label

    appWindow = ac.newApp(app)
    ac.setSize(appWindow, APP_WIDTH, APP_HEIGHT)
    ac.setTitle(appWindow, "")
    ac.setIconPosition(appWindow, 0, -10000)
    ac.setBackgroundOpacity(appWindow, 0.7)
    ac.drawBorder(appWindow, 0)

    y = 5

    # Drift angle title
    slip_angle_label = ac.addLabel(appWindow, "DRIFT ANGLE")
    ac.setPosition(slip_angle_label, APP_WIDTH // 2 - 50, y)
    ac.setFontSize(slip_angle_label, 14)
    ac.setFontColor(slip_angle_label, 0.7, 0.7, 0.7, 1.0)
    y += 20

    # Big drift angle value
    slip_value_label = ac.addLabel(appWindow, "0.0")
    ac.setPosition(slip_value_label, APP_WIDTH // 2 - 40, y)
    ac.setFontSize(slip_value_label, 42)
    ac.setFontColor(slip_value_label, 1.0, 1.0, 1.0, 1.0)
    y += 55

    # Drift state
    state_label = ac.addLabel(appWindow, "GRIP")
    ac.setPosition(state_label, APP_WIDTH // 2 - 40, y)
    ac.setFontSize(state_label, 22)
    ac.setFontColor(state_label, 0.5, 1.0, 0.5, 1.0)
    y += 35

    # Counter-steer info
    countersteer_label = ac.addLabel(appWindow, "STEER: ---")
    ac.setPosition(countersteer_label, 10, y)
    ac.setFontSize(countersteer_label, 16)
    ac.setFontColor(countersteer_label, 1.0, 1.0, 1.0, 1.0)
    y += 25

    # Yaw rate
    yaw_label = ac.addLabel(appWindow, "YAW: 0.0")
    ac.setPosition(yaw_label, 10, y)
    ac.setFontSize(yaw_label, 16)
    ac.setFontColor(yaw_label, 1.0, 1.0, 1.0, 1.0)
    y += 35

    # Session stats
    stats_label = ac.addLabel(appWindow, "")
    ac.setPosition(stats_label, 10, y)
    ac.setFontSize(stats_label, 13)
    ac.setFontColor(stats_label, 0.7, 0.7, 0.7, 1.0)

    ac.addRenderCallback(appWindow, onFormRender)
    ac.log("[" + app + "] Loaded")
    return app


def acUpdate(deltaT):
    pass


def get_body_slip_angle(car):
    """Calculate body slip angle from local velocity."""
    try:
        lv = ac.getCarState(car, acsys.CS.LocalVelocity)
        # lv[0] = lateral, lv[2] = forward (based on AC coordinate system)
        speed = ac.getCarState(car, acsys.CS.SpeedKMH)
        if speed < 5.0:
            return 0.0
        return math.degrees(math.atan2(lv[0], abs(lv[2])))
    except Exception:
        return 0.0


def get_yaw_rate(car):
    """Get yaw rate from local angular velocity."""
    try:
        av = ac.getCarState(car, acsys.CS.LocalAngularVelocity)
        return av[1]  # y component = yaw
    except Exception:
        return 0.0


def get_drift_state(slip_angle, yaw_rate):
    """Determine current drift state."""
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
    """Return (r, g, b) for drift angle display."""
    a = abs(angle)
    if a < DRIFT_ANGLE_MIN:
        return (0.5, 1.0, 0.5)       # Green - grip
    elif a < 20:
        return (0.5, 1.0, 0.5)       # Green - light drift
    elif a < 35:
        return (1.0, 1.0, 0.2)       # Yellow - moderate
    elif a < 50:
        return (1.0, 0.6, 0.1)       # Orange - aggressive
    elif a < DRIFT_ANGLE_SPIN:
        return (1.0, 0.3, 0.1)       # Red-orange - extreme
    else:
        return (1.0, 0.0, 0.0)       # Red - spinning


def state_color(state):
    """Color for drift state text."""
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

    ac.setBackgroundOpacity(appWindow, 0.7)

    car = ac.getFocusedCar()

    # Core data
    slip_angle = get_body_slip_angle(car)
    yaw_rate = get_yaw_rate(car)
    steer = 0.0
    try:
        steer = ac.getCarState(car, acsys.CS.Steer)
    except Exception:
        pass

    drift_state = get_drift_state(slip_angle, yaw_rate)
    abs_angle = abs(slip_angle)

    # === UPDATE SLIP ANGLE DISPLAY ===
    r, g, b = angle_to_color(slip_angle)
    ac.setFontColor(slip_value_label, r, g, b, 1.0)
    ac.setText(slip_value_label, "{:.1f}".format(abs_angle))

    # === UPDATE STATE ===
    sr, sg, sb = state_color(drift_state)
    ac.setFontColor(state_label, sr, sg, sb, 1.0)
    ac.setText(state_label, state_names[drift_state])

    # === COUNTER-STEER ===
    is_drifting = drift_state == SUSTAINING or drift_state == INITIATING
    if is_drifting and abs_angle > DRIFT_ANGLE_MIN:
        # Check if counter-steering (steer and slip same sign)
        is_counter = (slip_angle > 0 and steer > 0) or (slip_angle < 0 and steer < 0)
        steer_ratio = abs(steer) / max(abs_angle * 14.0, 1.0)  # rough match ratio

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

    # === YAW RATE ===
    abs_yaw = abs(yaw_rate)
    if abs_yaw > YAW_SPIN_THRESHOLD:
        ac.setFontColor(yaw_label, 1.0, 0.2, 0.2, 1.0)
    elif abs_yaw > 1.5:
        ac.setFontColor(yaw_label, 1.0, 1.0, 0.3, 1.0)
    else:
        ac.setFontColor(yaw_label, 0.7, 0.7, 0.7, 1.0)
    ac.setText(yaw_label, "YAW: {:.1f}".format(yaw_rate))

    # === SESSION STATS ===
    currently_drifting = drift_state == SUSTAINING
    currently_spinning = drift_state == SPINNING

    # Track max angle
    if abs_angle > stats_max_angle and currently_drifting:
        stats_max_angle = abs_angle

    # Track drift duration
    if currently_drifting:
        stats_current_drift_time += deltaT
        if not was_drifting:
            stats_drift_count += 1
    else:
        if was_drifting and stats_current_drift_time > stats_longest_drift:
            stats_longest_drift = stats_current_drift_time
        if not currently_drifting:
            stats_current_drift_time = 0.0

    # Track spins
    if currently_spinning and not was_spinning:
        stats_spin_count += 1

    was_drifting = currently_drifting
    was_spinning = currently_spinning

    # Display stats
    longest = max(stats_longest_drift, stats_current_drift_time)
    stats_text = "Max: {:.1f}  Longest: {:.1f}s  Drifts: {}  Spins: {}".format(
        stats_max_angle, longest, stats_drift_count, stats_spin_count
    )
    ac.setText(stats_label, stats_text)

    # === DRAW SLIP ANGLE ARC ===
    draw_angle_arc(slip_angle)


def draw_angle_arc(slip_angle):
    """Draw a visual arc showing the drift angle."""
    cx = APP_WIDTH / 2.0
    cy = 95.0
    radius = 60.0
    abs_angle = abs(slip_angle)

    # Draw background arc (gray, full range)
    ac.glBegin(1)  # line strip
    ac.glColor4f(0.3, 0.3, 0.3, 0.5)
    for i in range(-90, 91, 5):
        x = cx + radius * math.cos(math.radians(i - 90))
        y = cy + radius * math.sin(math.radians(i - 90))
        ac.glVertex2f(x, y)
    ac.glEnd()

    # Draw center tick
    ac.glBegin(0)  # lines
    ac.glColor4f(0.6, 0.6, 0.6, 0.8)
    ac.glVertex2f(cx, cy - radius - 5)
    ac.glVertex2f(cx, cy - radius + 5)
    ac.glEnd()

    # Draw active arc (colored by angle)
    if abs_angle > 1.0:
        r, g, b = angle_to_color(slip_angle)
        ac.glBegin(1)
        ac.glColor4f(r, g, b, 0.9)

        # Map slip angle to arc: 0 = top, positive = right, negative = left
        # Clamp to display range
        display_angle = max(-80, min(80, slip_angle))
        steps = max(2, int(abs(display_angle) / 2))

        if display_angle > 0:
            for i in range(steps + 1):
                a = (float(i) / steps) * display_angle
                x = cx + radius * math.cos(math.radians(a - 90))
                y = cy + radius * math.sin(math.radians(a - 90))
                ac.glVertex2f(x, y)
        else:
            for i in range(steps + 1):
                a = (float(i) / steps) * display_angle
                x = cx + radius * math.cos(math.radians(a - 90))
                y = cy + radius * math.sin(math.radians(a - 90))
                ac.glVertex2f(x, y)
        ac.glEnd()

        # Draw angle pointer at the end
        end_angle = max(-80, min(80, slip_angle))
        px = cx + radius * math.cos(math.radians(end_angle - 90))
        py = cy + radius * math.sin(math.radians(end_angle - 90))
        ac.glBegin(0)
        ac.glColor4f(r, g, b, 1.0)
        inner_x = cx + (radius - 8) * math.cos(math.radians(end_angle - 90))
        inner_y = cy + (radius - 8) * math.sin(math.radians(end_angle - 90))
        outer_x = cx + (radius + 8) * math.cos(math.radians(end_angle - 90))
        outer_y = cy + (radius + 8) * math.sin(math.radians(end_angle - 90))
        ac.glVertex2f(inner_x, inner_y)
        ac.glVertex2f(outer_x, outer_y)
        ac.glEnd()
