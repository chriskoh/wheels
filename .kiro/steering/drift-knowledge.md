---
inclusion: auto
---

# Drift Knowledge Base

This document contains everything needed to build drift training tools for Assetto Corsa.

## Physics of Drifting

Drifting is controlled oversteer. The rear tires exceed their grip limit while the driver maintains directional control through counter-steering and throttle modulation.

### Key Forces
- Centripetal force pushes the car outward in a turn
- Friction force from tires resists sliding (static friction > kinetic friction, so once tires break loose they stay loose easier)
- Weight transfer: braking shifts weight forward (less rear grip = easier to break loose), acceleration shifts weight rearward
- Yaw momentum: once the car starts rotating, inertia keeps it rotating — the driver must actively manage this

### The Slip Angle
- Slip angle = difference between where a tire is pointed and where it's actually traveling
- In a drift, rear slip angle greatly exceeds front slip angle
- The car's body slip angle (overall drift angle) is the angle between the car's centerline and its direction of travel
- Competition drift angles typically range from 20-60+ degrees
- Bigger angle = more impressive but harder to control
- The front wheels point opposite to the turn direction (counter-steer / opposite lock)

### Tire Behavior
- Tires generate maximum lateral force at a specific slip angle (typically 6-12 degrees for road tires)
- Beyond peak slip angle, lateral force drops — this is where drifting lives
- Tire temperature affects grip: cold tires (below 50C) have poor grip, optimal 75-100C, overheating (120C+) degrades rubber
- Rear tires in a drift run much hotter due to constant sliding
- Tire wear is extreme during drifting — rear tires can be destroyed in minutes of hard sliding

## Drift Initiation Techniques

### Power Over
- Simply apply excessive throttle to overwhelm rear tire grip
- Works best with high-power RWD cars
- Most basic technique, good for learning throttle control

### Clutch Kick
- Rapidly disengage and re-engage clutch while on throttle
- The sudden torque spike breaks rear traction
- Used for mid-corner initiation or to increase angle during a drift
- Very common in competition

### Handbrake (E-brake)
- Pull handbrake to lock rear wheels momentarily
- Initiates rotation without needing high power
- Good for lower-speed entries and tight corners
- Release quickly — holding too long kills momentum

### Scandinavian Flick (Feint)
- Steer away from the corner first, then quickly steer into it
- The weight transfer from the flick unloads the rear
- Very effective for high-speed entries
- Requires good timing — too early or late and it doesn't work

### Lift-Off Oversteer
- Suddenly lift off the throttle mid-corner
- Weight shifts forward, rear loses grip
- Subtle technique, good for initiating at moderate speeds
- Common in turbo cars where boost drop also reduces rear torque

### Braking Drift
- Trail brake into a corner to shift weight forward
- Rear lightens and breaks loose
- Can combine with steering input for more aggressive initiation

## Drift Maintenance

### Throttle Control
- THE most important skill in drifting
- More throttle = wider angle, rear slides more
- Less throttle = tighter angle, rear starts to grip up
- Must be smooth and progressive — jerky inputs cause spin or grip-up
- "Feathering" the throttle = making small rapid adjustments to maintain angle
- Throttle position during a sustained drift is typically 50-80%

### Counter-Steering
- Steer in the opposite direction of the slide to maintain control
- The amount of counter-steer matches the drift angle
- Too much counter-steer = car straightens out (grip-up)
- Too little counter-steer = car spins
- Should be smooth and reactive, not jerky
- Hands should allow the wheel to self-center and catch it — not fight it

### Reading the Car
- Feel the yaw rate (rotation speed) — if it's increasing, you're about to spin
- Feel the lateral G-force — tells you how hard you're sliding
- Listen to engine RPM — dropping RPM means losing momentum
- Watch the road ahead, not the hood — look where you want to go

## Drift Transitions

### What is a Transition
- Changing drift direction from one corner to the next
- The hardest part of drifting — where most beginners fail
- Requires quickly unwinding counter-steer, flicking the car the other way, and re-establishing the drift

### Transition Technique
1. Reduce throttle slightly to let rear grip up momentarily
2. Quickly steer toward the new corner direction
3. Use weight transfer (the car's momentum) to swing the rear the other way
4. Apply throttle to break rear traction in the new direction
5. Counter-steer and modulate throttle to maintain new drift

### Common Transition Mistakes
- Too slow on steering input — car straightens out completely, losing flow
- Too much throttle during transition — rear doesn't change direction, spins
- Not enough throttle after transition — drift dies, car grips up
- Panic counter-steer — over-correcting causes tank slapper oscillation

## Competition Judging (Formula Drift Style)

### Line (scored)
- Following the prescribed racing line through clipping points
- Inner clipping points: front bumper should come as close as possible
- Outer clipping points: rear bumper proximity is judged
- Transition zones: smooth direction changes between corners

### Angle (scored)
- Higher body slip angle = more points
- Consistency of angle throughout the run matters
- Steering corrections should be minimal mid-corner
- Judges reward pushing the limits

### Speed (scored)
- Higher speed through the course = more points
- Speed must be maintained throughout — slowing mid-drift loses points
- Aggressive entries are rewarded

### Style (scored)
- Smoke production (tire smoke = commitment)
- Proximity to walls/clips
- Smoothness and fluidity
- Aggression and commitment
- Crowd factor

## Car Setup for Drifting

### Drivetrain
- RWD is essential (or AWD with heavy rear bias)
- Locked or very aggressive LSD (limited slip differential)
- A fully locked diff makes both rear wheels spin at the same rate — more predictable slides
- Higher power helps maintain slides but isn't required to learn

### Suspension
- Stiffer front springs, softer rear (promotes oversteer)
- Front camber: -3 to -5 degrees (better contact during counter-steer)
- Rear camber: -1 to -2 degrees
- Front toe: slight toe-out (quicker turn-in)
- Rear toe: zero or slight toe-in (stability)
- Lower ride height improves response but too low scrapes

### Steering
- Maximum steering lock/angle is critical — more lock = more angle possible
- Steering ratio affects how fast the wheels respond to input
- Quick ratio preferred for fast counter-steer response
- Typical steering lock: 35-50+ degrees at the wheels

## Skill Progression (Beginner to Advanced)

### Stage 1: Basic Control
- Learn to initiate a slide (donuts, figure 8s)
- Understand throttle = angle relationship
- Get comfortable with counter-steering
- Practice in open areas, low speed

### Stage 2: Sustained Drifts
- Hold a drift through a single corner
- Maintain consistent angle and speed
- Smooth throttle modulation
- Proper counter-steer amount

### Stage 3: Transitions
- Link two corners together
- Quick direction changes
- Weight transfer management
- Maintaining speed through transitions

### Stage 4: Line Control
- Hit specific clipping points while drifting
- Adjust line mid-drift
- Consistent angle on repeated runs
- Speed management through a course

### Stage 5: Competition Ready
- Maximum angle with control
- Wall proximity (inches from barriers)
- Tandem drifting (following/leading another car)
- Adapting to different cars and tracks

## Assetto Corsa Python API — Available Drift Telemetry

All accessed via `ac.getCarState(car, acsys.CS.<identifier>)`:

### Scalar Values
- `Steer` — steering wheel angle (degrees, despite docs saying radians)
- `Gas` — throttle position 0.0 to 1.0
- `Brake` — brake position 0.0 to 1.0
- `Clutch` — clutch position 0.0 to 1.0
- `SpeedKMH` / `SpeedMPH` / `SpeedMS` — current speed
- `Gear` — current gear
- `RPM` — engine RPM
- `DriftPoints` — current lap drift points
- `DriftBestLap` — best lap drift points
- `InstantDrift` — current instant drift score
- `IsDriftInvalid` — whether current drift is invalidated
- `CGHeight` — center of gravity height

### 3D Vectors (x, y, z)
- `AccG` — G-forces on the car
- `LocalAngularVelocity` — yaw/pitch/roll rates (car-relative). Y component = yaw rate = how fast car is rotating
- `LocalVelocity` — velocity in car coordinates. X = lateral (sideways) speed, Z = longitudinal (forward) speed
- `Velocity` — world-space velocity vector
- `WorldPosition` — car position on track
- `WheelAngularSpeed` — wheel rotation speeds

### 4D Vectors (FL, FR, RL, RR)
- `SlipAngle` — slip angle per tire in degrees
- `SlipRatio` — ratio of tire spin vs ground speed per wheel
- `CurrentTyresCoreTemp` — core temperature per tire
- `DynamicPressure` — tire pressure per wheel
- `Load` — vertical load per tire
- `SuspensionTravel` — suspension compression per wheel
- `CamberRad` — camber angle per wheel in radians
- `TyreDirtyLevel` — dirt on tires (0-10)
- `Mz` — self-aligning torque per tire
- `NdSlip` / `TyreSlip` / `DY` — various tire slip metrics

### Per-Wheel 3D Vectors (need FL/FR/RL/RR as optional param)
- `TyreContactPoint` — where tire touches ground
- `TyreContactNormal` — surface normal at contact
- `TyreHeadingVector` — direction tire is pointing
- `TyreRightVector` — tire's lateral direction

### Calculating Body Slip Angle
Body slip angle can be derived from LocalVelocity:
```python
local_vel = ac.getCarState(car, acsys.CS.LocalVelocity)
# local_vel[0] = lateral velocity, local_vel[2] = forward velocity
body_slip_angle = math.degrees(math.atan2(local_vel[0], local_vel[2]))
```
This gives the angle between where the car is pointed and where it's actually going — the core drift angle metric.

### Detecting Counter-Steer
Counter-steer occurs when the steering direction opposes the drift direction:
```python
steer = ac.getCarState(car, acsys.CS.Steer)
# If body_slip_angle is positive (sliding right) and steer is positive (wheels right), that's counter-steer
is_counter_steering = (body_slip_angle > 0 and steer > 0) or (body_slip_angle < 0 and steer < 0)
```

### AC GL Drawing Functions
- `ac.glBegin(mode)` — 0=lines, 1=line strip, 2=triangles, 3=quads
- `ac.glEnd()` — finish primitive
- `ac.glVertex2f(x, y)` — add vertex
- `ac.glColor3f(r, g, b)` / `ac.glColor4f(r, g, b, a)` — set color
- `ac.glQuad(x, y, w, h)` — quick rectangle
- `ac.glQuadTextured(x, y, w, h, texture_id)` — textured rectangle
- `ac.newTexture(path)` — load texture from AC root
