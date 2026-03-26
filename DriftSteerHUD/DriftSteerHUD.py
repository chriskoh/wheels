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
TEMP_COLD = 50.0
TEMP_COOL = 70.0
TEMP_OPTIMAL_LOW = 75.0
TEMP_OPTIMAL_HIGH = 100.0
TEMP_HOT = 120.0

# Car body dimensions (relative to center, before scaling)
CAR_BODY_W = 130  # total width
CAR_BODY_H = 200  # total height

scale = 1.0
SCALE_STEP = 0.1
SCALE_MIN = 0.5
SCALE_MAX = 3.0

prev_slip = 0.0
slip_smooth = 0.0


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
    """Return (r, g, b): blue -> green -> yellow -> orange -> red."""
    if temp < TEMP_COLD:
        return (0.1, 0.3, 1.0)
    elif temp < TEMP_OPTIMAL_LOW:
        t = (temp - TEMP_COLD) / (TEMP_OPTIMAL_LOW - TEMP_COLD)
        return (0.1 * (1.0 - t), 0.3 + 0.7 * t, 1.0 * (1.0 - t))
    elif temp < TEMP_OPTIMAL_HIGH:
        return (0.0, 1.0, 0.0)
    elif temp < TEMP_HOT:
        t = (temp - TEMP_OPTIMAL_HIGH) / (TEMP_HOT - TEMP_OPTIMAL_HIGH)
        if t < 0.33:
            s = t / 0.33
            return (s, 1.0, 0.0)
        elif t < 0.66:
            s = (t - 0.33) / 0.33
            return (1.0, 1.0 - 0.5 * s, 0.0)
        else:
            s = (t - 0.66) / 0.34
            return (1.0, 0.5 * (1.0 - s), 0.0)
    else:
        return (1.0, 0.0, 0.0)


def rotate_point(x, y, angle_rad, cx, cy):
    """Rotate point (x,y) around (cx,cy) by angle_rad."""
    dx = x - cx
    dy = y - cy
    rx = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
    ry = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
    return (cx + rx, cy + ry)


def get_body_slip_angle(car):
    """Get body slip angle in degrees from local velocity."""
    try:
        lv = ac.getCarState(car, acsys.CS.LocalVelocity)
        lvx = lv[0]  # lateral
        lvz = lv[2]  # forward
        if abs(lvz) < 0.5:
            return 0.0
        return math.degrees(math.atan2(lvx, abs(lvz)))
    except Exception:
        return 0.0



def onFormRender(deltaT):
    global angle_label, slip_smooth

    ac.setBackgroundOpacity(appWindow, 0.0)

    car = ac.getFocusedCar()

    # Steer angle
    try:
        steer_angle = ac.getCarState(car, acsys.CS.Steer)
        tire_angle_deg = steer_angle / STEERING_RATIO
    except Exception:
        tire_angle_deg = 0.0

    # Body slip angle
    body_slip_deg = get_body_slip_angle(car)
    slip_smooth = slip_smooth * 0.85 + body_slip_deg * 0.15

    # Tire temperatures
    fl_temp = fr_temp = rl_temp = rr_temp = 70.0
    try:
        fl_temp, fr_temp, rl_temp, rr_temp = ac.getCarState(car, acsys.CS.CurrentTyresCoreTemp)
    except Exception:
        pass

    ac.setText(angle_label, "{:.1f}".format(slip_smooth))

    s = scale
    tw = TIRE_WIDTH * s
    th = TIRE_HEIGHT * s

    # Center of the car in widget space
    car_cx = APP_WIDTH / 2.0
    car_cy = APP_HEIGHT / 2.0

    # Body slip rotation (the whole car rotates)
    body_rad = math.radians(slip_smooth)

    # Car body outline
    bw = CAR_BODY_W * s / 2.0
    bh = CAR_BODY_H * s / 2.0
    body_corners = [
        (car_cx - bw, car_cy - bh),
        (car_cx + bw, car_cy - bh),
        (car_cx + bw, car_cy + bh),
        (car_cx - bw, car_cy + bh),
    ]
    rotated_body = [rotate_point(x, y, body_rad, car_cx, car_cy) for x, y in body_corners]

    # Draw car body (semi-transparent fill)
    ac.glBegin(3)
    ac.glColor4f(0.2, 0.2, 0.2, 0.5)
    for x, y in rotated_body:
        ac.glVertex2f(x, y)
    ac.glEnd()

    # Body outline
    ac.glBegin(1)
    ac.glColor4f(0.8, 0.8, 0.8, 0.6)
    for i in range(4):
        x1, y1 = rotated_body[i]
        x2, y2 = rotated_body[(i + 1) % 4]
        ac.glVertex2f(x1, y1)
        ac.glVertex2f(x2, y2)
    ac.glEnd()

    # Wheel positions relative to car center (before rotation)
    spacing = 50 * s
    front_offset_y = -70 * s  # front axle offset from center
    rear_offset_y = 70 * s    # rear axle offset from center

    # Front left
    fl_cx, fl_cy = car_cx - spacing, car_cy + front_offset_y
    fl_cx, fl_cy = rotate_point(fl_cx, fl_cy, body_rad, car_cx, car_cy)
    draw_tire(fl_cx, fl_cy, body_rad + math.radians(tire_angle_deg), tw, th, fl_temp)

    # Front right
    fr_cx, fr_cy = car_cx + spacing, car_cy + front_offset_y
    fr_cx, fr_cy = rotate_point(fr_cx, fr_cy, body_rad, car_cx, car_cy)
    draw_tire(fr_cx, fr_cy, body_rad + math.radians(tire_angle_deg), tw, th, fr_temp)

    # Rear left
    rl_cx, rl_cy = car_cx - spacing, car_cy + rear_offset_y
    rl_cx, rl_cy = rotate_point(rl_cx, rl_cy, body_rad, car_cx, car_cy)
    draw_tire(rl_cx, rl_cy, body_rad, tw, th, rl_temp)

    # Rear right
    rr_cx, rr_cy = car_cx + spacing, car_cy + rear_offset_y
    rr_cx, rr_cy = rotate_point(rr_cx, rr_cy, body_rad, car_cx, car_cy)
    draw_tire(rr_cx, rr_cy, body_rad, tw, th, rr_temp)

    # --- Travel direction lines (fixed vertical = road direction) ---
    # These stay straight while the car rotates, showing the drift angle.
    line_offset_x = bw + 12 * s  # just outside the car body
    line_half_h = bh + 10 * s

    # Cyan when drifting, dim grey when straight — always visible
    if abs(slip_smooth) > 3.0:
        lr, lg, lb, la = 0.0, 0.9, 1.0, 0.9
    else:
        lr, lg, lb, la = 0.6, 0.6, 0.6, 0.5

    # Left travel line (separate draw call to avoid diagonal)
    ac.glBegin(1)
    ac.glColor4f(lr, lg, lb, la)
    ac.glVertex2f(car_cx - line_offset_x, car_cy - line_half_h)
    ac.glVertex2f(car_cx - line_offset_x, car_cy + line_half_h)
    ac.glEnd()

    # Right travel line
    ac.glBegin(1)
    ac.glColor4f(lr, lg, lb, la)
    ac.glVertex2f(car_cx + line_offset_x, car_cy - line_half_h)
    ac.glVertex2f(car_cx + line_offset_x, car_cy + line_half_h)
    ac.glEnd()


def draw_tire(cx, cy, angle_rad, tw, th, temp):
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
