import math

f = open('SteerMeter/SteerMeter.py', 'r').read()

wheel_func = '''def draw_steering_wheel(cx, cy, radius, steer_rad, s):
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


'''

f = f.replace('def onFormRender(deltaT):', wheel_func + 'def onFormRender(deltaT):')

old_block = """    # --- Draw wheel ring (always visible) ---
    draw_arc(cx, cy, wheel_r, 0, 360, 48, 0.4, 0.4, 0.4, 0.6)

    # Current steering position as wheel rotation
    # steer is in degrees at the wheel, we show it directly as rotation
    # Clamp display to +/- 180 for visual sanity
    steer_display = max(-180.0, min(180.0, steer))
    # On screen: 0 deg = right (3 o'clock), -90 = top (12 o'clock)
    # We want top = straight, so offset by -90
    # Positive steer = right turn = clockwise on screen
    current_angle_deg = -90.0 + steer_display"""

new_block = """    # Draw steering wheel (rotates with input)
    steer_display = max(-180.0, min(180.0, steer))
    steer_rad = math.radians(steer_display)
    draw_steering_wheel(cx, cy, wheel_r, steer_rad, s)

    # Current steer needle on the rim
    current_angle_deg = -90.0 + steer_display"""

f = f.replace(old_block, new_block)

with open('SteerMeter/SteerMeter.py', 'w') as out:
    out.write(f)

print("draw_steering_wheel in file:", "draw_steering_wheel" in f)
