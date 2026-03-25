import ac
import acsys
import math

app = "DriftSteerHUD"
appWindow = 0
angle_label = 0
size_label = 0
btn_increase = 0
btn_decrease = 0

APP_WIDTH = 200
APP_HEIGHT = 200
TIRE_WIDTH = 30
TIRE_HEIGHT = 60
STEERING_RATIO = 14.0

# Scale factor (1.0 = default, adjustable in-game)
scale = 1.0
SCALE_STEP = 0.1
SCALE_MIN = 0.5
SCALE_MAX = 3.0


def acMain(ac_version):
    global appWindow, angle_label, btn_increase, btn_decrease, size_label

    appWindow = ac.newApp(app)
    ac.setSize(appWindow, APP_WIDTH, APP_HEIGHT)
    ac.setTitle(appWindow, "")
    ac.setIconPosition(appWindow, 0, -10000)
    ac.setBackgroundOpacity(appWindow, 0.0)
    ac.drawBorder(appWindow, 0)

    # Numeric tire angle label
    angle_label = ac.addLabel(appWindow, "0.0")
    ac.setPosition(angle_label, APP_WIDTH // 2 - 20, APP_HEIGHT - 30)
    ac.setFontSize(angle_label, 16)
    ac.setFontColor(angle_label, 1.0, 1.0, 1.0, 1.0)

    # Size controls (top-left corner)
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


def onFormRender(deltaT):
    global angle_label

    ac.setBackgroundOpacity(appWindow, 0.0)

    car = ac.getFocusedCar()
    steer_angle = ac.getCarState(car, acsys.CS.Steer)
    tire_angle_deg = steer_angle / STEERING_RATIO

    ac.setText(angle_label, "{:.1f}".format(tire_angle_deg))

    # Draw tires scaled
    tw = TIRE_WIDTH * scale
    th = TIRE_HEIGHT * scale
    center_y = APP_HEIGHT // 2 - 10
    spacing = 50 * scale
    left_x = APP_WIDTH / 2.0 - spacing
    right_x = APP_WIDTH / 2.0 + spacing

    draw_tire(left_x, center_y, tire_angle_deg, tw, th)
    draw_tire(right_x, center_y, tire_angle_deg, tw, th)


def draw_tire(cx, cy, angle_deg, tw, th):
    angle_rad = math.radians(angle_deg)
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

    # Filled tire
    ac.glBegin(3)
    ac.glColor4f(0.2, 0.2, 0.2, 0.9)
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

    # Red direction line
    ac.glBegin(1)
    ac.glColor4f(1.0, 0.3, 0.3, 1.0)
    ac.glVertex2f(cx, cy)
    tip_x = cx - hh * math.sin(angle_rad)
    tip_y = cy - hh * math.cos(angle_rad)
    ac.glVertex2f(tip_x, tip_y)
    ac.glEnd()
