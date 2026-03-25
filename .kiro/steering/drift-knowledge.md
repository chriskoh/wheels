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

## Assetto Corsa Python API — VERIFIED Available Telemetry

Tested in-game 2026-03-24. 92 working, 1 error, 12 missing.
All via `ac.getCarState(car, acsys.CS.<id>)` unless noted.

### Scalar Values (all CONFIRMED working)
- `Steer` — steering wheel angle in DEGREES (docs say radians, they're wrong). Sample: 130.6
- `Gas` — throttle 0.0-1.0
- `Brake` — brake 0.0-1.0
- `Clutch` — clutch 0.0-1.0 (1.0 = fully depressed)
- `Gear` — current gear (int)
- `RPM` — engine RPM (float)
- `SpeedKMH` / `SpeedMPH` / `SpeedMS` — speed in various units
- `BestLap` — best lap ms (int)
- `LapTime` — current lap ms (int)
- `LastLap` — last lap ms (int)
- `LapCount` — laps completed (int)
- `LapInvalidated` — 0 or 1
- `CGHeight` — center of gravity height (float, sample: 0.44)
- `DriveTrainSpeed` — speed at wheels (float)
- `DriftPoints` — current lap drift score
- `DriftBestLap` — best drift lap score
- `DriftLastLap` — last drift lap score
- `InstantDrift` — real-time drift score
- `IsDriftInvalid` — 0 or 1
- `IsEngineLimiterOn` — 0 or 1
- `LastFF` — last force feedback value
- `NormalizedSplinePosition` — track position 0.0-1.0
- `PerformanceMeter` — delta to best lap
- `TurboBoost` — turbo pressure
- `Caster` — caster angle (float, sample: -8.5)

### DOES NOT EXIST
- `SteerAngle` — ERROR: "type object 'CS' has no attribute 'SteerAngle'"

### 3D Vectors (CONFIRMED working, return 3-element tuple)
- `AccG` — G-forces (x, y, z)
- `LocalAngularVelocity` — rotation rates in car space. CRITICAL: y = yaw rate
- `LocalVelocity` — velocity in car space. x = lateral, y = vertical, z = forward (NOTE: probe showed y=-0.335 when stationary, z=0.009 — y appears to be vertical/gravity, needs testing while moving)
- `Velocity` — world-space velocity
- `SpeedTotal` — (kmh, mph, ms) all at once
- `WorldPosition` — car world coordinates

### 4D Vectors (CONFIRMED working, return 4-element tuple: FL, FR, RL, RR)
- `WheelAngularSpeed` — returns 4 values despite being listed as 3D in docs
- `SlipAngle` — per-tire slip angle in degrees. Sample: FL=-8.5, FR=13.4, RL=-5.3, RR=6.0
- `SlipRatio` — tire spin vs ground speed. Sample: 0.019, -0.011, 0.001, 0.003
- `Load` — vertical load per tire in Newtons. Sample: FL=2624, FR=2838, RL=4200, RR=4086
- `CamberRad` — camber per wheel in radians. Sample: -0.106, -0.041, -0.016, -0.016
- `CurrentTyresCoreTemp` — core temp per tire in Celsius. Sample: 26.0 (cold start)
- `LastTyresTemp` — returns 3 values (not 4!), shows -200 when no data. Unreliable.
- `DynamicPressure` — tire pressure PSI. Sample: 30.0 all around
- `SuspensionTravel` — suspension compression in meters. Sample: 0.019-0.045
- `TyreDirtyLevel` — dirt level 0-10. Sample: 0.0
- `Mz` — self-aligning torque. Sample: 0.047, 0.436, 1.752, -2.102
- `NdSlip` — normalized slip. Sample: 0.963, 1.474, 0.552, 0.622
- `TyreSlip` — returns 0.0 at standstill, needs testing while moving
- `DY` — lateral friction coefficient. Sample: 1.261, 1.314, 1.247, 1.250
- `TyreRadius` — unloaded radius in meters. Sample: 0.303
- `TyreLoadedRadius` — loaded radius. Sample: 0.293, 0.292, 0.287, 0.287

### Per-Wheel 3D Vectors (with acsys.WHEELS.FL/FR/RL/RR)
- `TyreContactPoint` — WORKS. World position where tire meets ground.
- `TyreContactNormal` — WORKS. Surface normal at contact (0,1,0 = flat ground).
- `TyreHeadingVector` — returns -1 (BROKEN, does not work)
- `TyreRightVector` — returns -1 (BROKEN, does not work)

### Extra/Undocumented (CONFIRMED working)
- `Aero` — returns float (needs index: 0=drag, 1=lift front, 2=lift rear). Returns 0.0 at standstill.
- `RideHeight` — returns 2-element vector (front, rear) in meters. Sample: 0.103, 0.092
- `ERSRecovery` / `ERSDelivery` / `ERSHeatCharging` — ERS settings (int, 0 for non-hybrid)
- `ERSCurrentKJ` / `ERSMaxJ` — ERS energy (float, 0 for non-hybrid)
- `P2PStatus` / `P2PActivations` — push-to-pass (int, 0 for most cars)

### CONFIRMED MISSING (not on acsys.CS)
- `ThermalState` — DOES NOT EXIST (use CurrentTyresCoreTemp instead)
- `TyreWear` — not available
- `BrakeTemperature` — not available
- `EngineTorque` / `EngineMaxTorque` — not available
- `MaxRPM` / `MaxSpeed` — not available
- `Turbo` — not available (use TurboBoost instead)
- `DRSAvailable` / `DRSEnabled` — not available
- `KERSCharge` / `KERSInput` — not available
- `SteerAngle` — not available (use Steer instead)

### Utility Functions (CONFIRMED working)
- `ac.getDriverName(car)` — driver name string
- `ac.getCarName(car)` — car model ID string
- `ac.getTrackName(car)` — track name string
- `ac.getTrackConfiguration(car)` — track config string
- `ac.getFocusedCar()` — focused car index (int)
- `ac.getCarBallast(car)` — ballast kg (int)
- `ac.getCarMinHeight(car)` — min ride height (float, -1.0 if not set)
- `ac.isAcLive()` — is AC running (int 0/1)
- `ac.isCarInPitlane(car)` — in pit lane (int 0/1)
- `ac.getCarSkin(car)` — skin name string
- `ac.getDriverNationCode(car)` — nation code string
- `ac.getTrackLength(car)` — track length in meters (float)
- `ac.getWindSpeed()` — wind speed (int)
- `ac.getWindDirection()` — wind direction degrees (int)
- `ac.isAIControlled(car)` — is AI (int 0/1)

### Calculating Body Slip Angle
Body slip angle can be derived from LocalVelocity:
```python
local_vel = ac.getCarState(car, acsys.CS.LocalVelocity)
# NOTE: from probe data, LocalVelocity appears to be (lateral, vertical, forward)
# Need to verify x vs z while car is moving
body_slip_angle = math.degrees(math.atan2(local_vel[0], abs(local_vel[2])))
```

### Detecting Counter-Steer
```python
steer = ac.getCarState(car, acsys.CS.Steer)
# If body_slip_angle and steer have same sign = counter-steering
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
