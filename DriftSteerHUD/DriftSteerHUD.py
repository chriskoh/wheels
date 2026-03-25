import ac
import acsys
import math

# App globals
appWindow = 0
tire_left = 0
tire_right = 0
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

    appWindow = ac.newApp("DriftSteerHUD")
    ac.setSize(appWindow, APP_WIDTH, APP_HEIGHT)
    ac.setTitle(appWindow, "Drift Steer HUD")
    ac.setBackgroundOpacity(appWindow, 0.5)

    # Label to show the numeric tire angle
    angle_label = ac.addLabel(appWindow, "0.0°")
    ac.setPosition(angle_label, APP_WIDTH // 2 - 20, APP_HEIGHT - 30)
    ac.setFontSize(angle_label, 16)
    ac.setFontColor(angle_label, 1.0, 1.0, 1.0, 1.0)

    ac.addRenderCallback(appWindow, onRender)
    ac.console("DriftSteerHUD loaded")
    return "DriftSteerHUD"


def acUpdate(deltaT):
    pass


def onRender(deltaT):
    global angle_label

    # Get steering wheel angle in degrees
    steer_angle = ac.getCarState(0, acsys.CS.SteerAngle)

    # Convert to approximate tire angle
    tire_angle_deg = steer_angle / STEERING_RATIO

    # Update the numeric label
    ac.setText(angle_label, "{:.1f}°".format(tire_angle_deg))

    # Draw the two tires
    center_y = APP_HEIGHT // 2 - 10
    left_x = APP_WIDTH // 2 - 50
    right_x = APP_WIDTH // 2 + 50

    draw_tire(left_x, center_y, tire_angle_deg)
    draw_tire(right_x, center_y, tire_angle_deg)


def draw_tire(cx, cy, angle_deg):
    """Draw a rotated rectangle representing a tire."""
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

    # Draw filled quad using AC's OpenGL rendering
    try:
        import ctypes
        from ctypes import c_float
        gl = ctypes.cdll.opengl32

        GL_QUADS = 0x0007

        # Dark tire color
        gl.glColor4f(c_float(0.2), c_float(0.2), c_float(0.2), c_float(0.9))
        gl.glBegin(GL_QUADS)
        for x, y in rotated:
            gl.glVertex2f(c_float(x), c_float(y))
        gl.glEnd()

        # White outline
        GL_LINE_LOOP = 0x0002
        gl.glColor4f(c_float(1.0), c_float(1.0), c_float(1.0), c_float(0.8))
        gl.glLineWidth(c_float(2.0))
        gl.glBegin(GL_LINE_LOOP)
        for x, y in rotated:
            gl.glVertex2f(c_float(x), c_float(y))
        gl.glEnd()

        # Direction indicator line (top center of tire, shows forward direction)
        gl.glColor4f(c_float(1.0), c_float(0.3), c_float(0.3), c_float(1.0))
        gl.glLineWidth(c_float(3.0))
        gl.glBegin(0x0001)  # GL_LINES
        gl.glVertex2f(c_float(cx), c_float(cy))
        tip_x = cx + hh * math.sin(angle_rad) * -1
        tip_y = cy - hh * math.cos(angle_rad)
        gl.glVertex2f(c_float(tip_x), c_float(tip_y))
        gl.glEnd()

    except Exception as e:
        ac.console("DriftSteerHUD render error: " + str(e))
