import ac
import acsys
import math

app = "DriftSteerHUD"
appWindow = 0
angle_label = 0

APP_WIDTH = 200
APP_HEIGHT = 200
TIRE_WIDTH = 30
TIRE_HEIGHT = 60

# Approximate steering ratio (steering wheel angle -> tire angle)
# Most cars are between 12:1 and 16:1. Adjust to taste.
STEERING_RATIO = 14.0


def acMain(ac_version):
    global appWindow, angle_label

    appWindow = ac.newApp(app)
    ac.setSize(appWindow, APP_WIDTH, APP_HEIGHT)
    ac.setTitle(appWindow, "")
    ac.setIconPosition(appWindow, 0, -10000)
    ac.setBackgroundOpacity(appWindow, 0.5)
    ac.drawBorder(appWindow, 0)

    # Label to show the numeric tire angle
    angle_label = ac.addLabel(appWindow, "0.0")
    ac.setPosition(angle_label, APP_WIDTH // 2 - 20, APP_HEIGHT - 30)
    ac.setFontSize(angle_label, 16)
    ac.setFontColor(angle_label, 1.0, 1.0, 1.0, 1.0)

    ac.addRenderCallback(appWindow, onFormRender)
    ac.log("[" + app + "] Loaded")
    return app


def acUpdate(deltaT):
    pass


def onFormRender(deltaT):
    global angle_label

    ac.setBackgroundOpacity(appWindow, 0.5)

    # Get steering wheel angle in degrees
    car = ac.getFocusedCar()
    steer_angle = ac.getCarState(car, acsys.CS.Steer)

    # Convert to approximate tire angle
    tire_angle_deg = steer_angle / STEERING_RATIO

    # Update the numeric label
    ac.setText(angle_label, "{:.1f}".format(tire_angle_deg))

    # Draw the two tires
    center_y = APP_HEIGHT // 2 - 10
    left_x = APP_WIDTH // 2 - 50
    right_x = APP_WIDTH // 2 + 50

    draw_tire(left_x, center_y, tire_angle_deg)
    draw_tire(right_x, center_y, tire_angle_deg)


def draw_tire(cx, cy, angle_deg):
    """Draw a rotated rectangle representing a tire using AC's GL functions."""
    angle_rad = math.radians(angle_deg)
    hw = TIRE_WIDTH / 2.0
    hh = TIRE_HEIGHT / 2.0

    # Four corners of the rectangle before rotation
    corners = [
        (-hw, -hh),
        ( hw, -hh),
        ( hw,  hh),
        (-hw,  hh),
    ]

    # Rotate each corner
    rotated = []
    for x, y in corners:
        rx = x * math.cos(angle_rad) - y * math.sin(angle_rad)
        ry = x * math.sin(angle_rad) + y * math.cos(angle_rad)
        rotated.append((cx + rx, cy + ry))

    # Draw filled quad (dark tire color)
    ac.glBegin(3)  # GL_QUADS
    ac.glColor4f(0.2, 0.2, 0.2, 0.9)
    for x, y in rotated:
        ac.glVertex2f(x, y)
    ac.glEnd()

    # Draw white outline
    ac.glBegin(1)  # GL_LINES
    ac.glColor4f(1.0, 1.0, 1.0, 0.8)
    for i in range(4):
        x1, y1 = rotated[i]
        x2, y2 = rotated[(i + 1) % 4]
        ac.glVertex2f(x1, y1)
        ac.glVertex2f(x2, y2)
    ac.glEnd()

    # Direction indicator line (red, points forward from tire center)
    ac.glBegin(1)  # GL_LINES
    ac.glColor4f(1.0, 0.3, 0.3, 1.0)
    ac.glVertex2f(cx, cy)
    tip_x = cx - hh * math.sin(angle_rad)
    tip_y = cy - hh * math.cos(angle_rad)
    ac.glVertex2f(tip_x, tip_y)
    ac.glEnd()
