import ac
import acsys
import math
import os

app = "APIProbe"
appWindow = 0
status_label = 0
results = []
probed = False
log_path = ""


def acMain(ac_version):
    global appWindow, status_label, log_path

    appWindow = ac.newApp(app)
    ac.setSize(appWindow, 400, 100)
    ac.setTitle(appWindow, "API Probe")
    ac.setBackgroundOpacity(appWindow, 0.8)

    status_label = ac.addLabel(appWindow, "Waiting for session...")
    ac.setPosition(status_label, 10, 30)
    ac.setFontSize(status_label, 14)
    ac.setFontColor(status_label, 1.0, 1.0, 1.0, 1.0)

    # Log to the app folder
    log_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "api_results.txt"
    )

    ac.log("[" + app + "] Loaded. Will probe on first update.")
    return app


def probe(name, fn):
    """Try a function, return (name, result_type, value_preview) or (name, 'ERROR', error_msg)."""
    try:
        val = fn()
        # Figure out what type we got
        if isinstance(val, (list, tuple)):
            t = "vector[{}]".format(len(val))
            preview = ", ".join("{:.3f}".format(v) for v in val[:6])
        elif isinstance(val, float):
            t = "float"
            preview = "{:.4f}".format(val)
        elif isinstance(val, int):
            t = "int"
            preview = str(val)
        else:
            t = type(val).__name__
            preview = str(val)[:60]
        return (name, t, preview)
    except Exception as e:
        return (name, "ERROR", str(e)[:80])


def acUpdate(deltaT):
    global probed, results

    if probed:
        return
    probed = True

    car = 0  # player car
    r = []

    ac.setText(status_label, "Probing APIs...")

    # === SCALAR VALUES ===
    scalars = [
        ("Steer", acsys.CS.Steer),
        ("Gas", acsys.CS.Gas),
        ("Brake", acsys.CS.Brake),
        ("Clutch", acsys.CS.Clutch),
        ("Gear", acsys.CS.Gear),
        ("RPM", acsys.CS.RPM),
        ("SpeedKMH", acsys.CS.SpeedKMH),
        ("SpeedMPH", acsys.CS.SpeedMPH),
        ("SpeedMS", acsys.CS.SpeedMS),
        ("BestLap", acsys.CS.BestLap),
        ("LapTime", acsys.CS.LapTime),
        ("LastLap", acsys.CS.LastLap),
        ("LapCount", acsys.CS.LapCount),
        ("LapInvalidated", acsys.CS.LapInvalidated),
        ("CGHeight", acsys.CS.CGHeight),
        ("DriveTrainSpeed", acsys.CS.DriveTrainSpeed),
        ("DriftPoints", acsys.CS.DriftPoints),
        ("DriftBestLap", acsys.CS.DriftBestLap),
        ("DriftLastLap", acsys.CS.DriftLastLap),
        ("InstantDrift", acsys.CS.InstantDrift),
        ("IsDriftInvalid", acsys.CS.IsDriftInvalid),
        ("IsEngineLimiterOn", acsys.CS.IsEngineLimiterOn),
        ("LastFF", acsys.CS.LastFF),
        ("NormalizedSplinePosition", acsys.CS.NormalizedSplinePosition),
        ("PerformanceMeter", acsys.CS.PerformanceMeter),
        ("TurboBoost", acsys.CS.TurboBoost),
    ]

    for name, cs_id in scalars:
        r.append(probe("Scalar." + name, lambda cid=cs_id: ac.getCarState(car, cid)))

    # Try Caster (may not exist)
    r.append(probe("Scalar.Caster", lambda: ac.getCarState(car, acsys.CS.Caster)))
    r.append(probe("Scalar.SteerAngle", lambda: ac.getCarState(car, acsys.CS.SteerAngle)))

    # === 3D VECTORS ===
    vectors3d = [
        ("AccG", acsys.CS.AccG),
        ("LocalAngularVelocity", acsys.CS.LocalAngularVelocity),
        ("LocalVelocity", acsys.CS.LocalVelocity),
        ("Velocity", acsys.CS.Velocity),
        ("SpeedTotal", acsys.CS.SpeedTotal),
        ("WorldPosition", acsys.CS.WorldPosition),
        ("WheelAngularSpeed", acsys.CS.WheelAngularSpeed),
    ]

    for name, cs_id in vectors3d:
        r.append(probe("Vec3." + name, lambda cid=cs_id: ac.getCarState(car, cid)))

    # === 4D VECTORS (per-tire) ===
    vectors4d_names = [
        "SlipAngle", "SlipRatio", "Load", "CamberRad",
        "CurrentTyresCoreTemp", "LastTyresTemp",
        "DynamicPressure", "SuspensionTravel", "TyreDirtyLevel",
        "Mz", "NdSlip", "TyreSlip", "DY", "TyreRadius",
        "TyreLoadedRadius",
    ]

    for name in vectors4d_names:
        if hasattr(acsys.CS, name):
            r.append(probe("Vec4." + name, lambda n=name: ac.getCarState(car, getattr(acsys.CS, n))))
        else:
            r.append(("Vec4." + name, "MISSING", "attribute not found on acsys.CS"))

    # === PER-WHEEL 3D VECTORS (with optional tire param) ===
    per_wheel_names = [
        "TyreContactPoint", "TyreContactNormal",
        "TyreHeadingVector", "TyreRightVector",
    ]
    wheel_ids = [
        ("FL", acsys.WHEELS.FL),
        ("FR", acsys.WHEELS.FR),
        ("RL", acsys.WHEELS.RL),
        ("RR", acsys.WHEELS.RR),
    ]

    for name in per_wheel_names:
        if hasattr(acsys.CS, name):
            for wname, wid in wheel_ids:
                r.append(probe(
                    "PerWheel.{}.{}".format(name, wname),
                    lambda n=name, w=wid: ac.getCarState(car, getattr(acsys.CS, n), w)
                ))
        else:
            r.append(("PerWheel." + name, "MISSING", "attribute not found on acsys.CS"))

    # === AERO (with index) ===
    for idx, aero_name in [(0, "DragCoeff"), (1, "LiftFront"), (2, "LiftRear")]:
        if hasattr(acsys.CS, "Aero"):
            r.append(probe(
                "Aero.{}".format(aero_name),
                lambda i=idx: ac.getCarState(car, acsys.CS.Aero, i)
            ))
        else:
            r.append(("Aero." + aero_name, "MISSING", "acsys.CS.Aero not found"))

    # === UNDOCUMENTED / EXTRA IDENTIFIERS TO TRY ===
    extras = [
        "ThermalState", "Aero", "RideHeight",
        "TyreWear", "BrakeTemperature", "EngineTorque",
        "EngineMaxTorque", "MaxRPM", "MaxSpeed",
        "Turbo", "ERSRecovery", "ERSDelivery",
        "ERSHeatCharging", "ERSCurrentKJ", "ERSMaxJ",
        "DRSAvailable", "DRSEnabled", "KERSCharge",
        "KERSInput", "P2PStatus", "P2PActivations",
    ]

    for name in extras:
        if hasattr(acsys.CS, name):
            r.append(probe("Extra." + name, lambda n=name: ac.getCarState(car, getattr(acsys.CS, n))))
        else:
            r.append(("Extra." + name, "MISSING", "not on acsys.CS"))

    # === OTHER AC FUNCTIONS ===
    r.append(probe("Func.getDriverName", lambda: ac.getDriverName(car)))
    r.append(probe("Func.getCarName", lambda: ac.getCarName(car)))
    r.append(probe("Func.getTrackName", lambda: ac.getTrackName(car)))
    r.append(probe("Func.getTrackConfiguration", lambda: ac.getTrackConfiguration(car)))
    r.append(probe("Func.getFocusedCar", lambda: ac.getFocusedCar()))
    r.append(probe("Func.getCarBallast", lambda: ac.getCarBallast(car)))
    r.append(probe("Func.getCarMinHeight", lambda: ac.getCarMinHeight(car)))

    # Try some undocumented functions
    undoc_funcs = [
        "isAcLive", "isCarInPitlane", "getCarSkin",
        "getDriverNationCode", "getTrackLength",
        "getWindSpeed", "getWindDirection", "isAIControlled",
    ]
    for fname in undoc_funcs:
        if hasattr(ac, fname):
            r.append(probe("Func." + fname, lambda f=fname: getattr(ac, f)(car) if f not in ["isAcLive", "getWindSpeed", "getWindDirection"] else getattr(ac, f)()))
        else:
            r.append(("Func." + fname, "MISSING", "not on ac module"))

    # === WRITE RESULTS ===
    results = r

    working = sum(1 for _, t, _ in r if t != "ERROR" and t != "MISSING")
    errors = sum(1 for _, t, _ in r if t == "ERROR")
    missing = sum(1 for _, t, _ in r if t == "MISSING")

    ac.setText(status_label, "Done: {} working, {} errors, {} missing. Check api_results.txt".format(working, errors, missing))

    # Write to file
    try:
        with open(log_path, "w") as f:
            f.write("=== AC API PROBE RESULTS ===\n\n")

            f.write("--- WORKING ({}) ---\n".format(working))
            for name, t, preview in r:
                if t != "ERROR" and t != "MISSING":
                    f.write("  [{}] {} = {}\n".format(t, name, preview))

            f.write("\n--- ERRORS ({}) ---\n".format(errors))
            for name, t, preview in r:
                if t == "ERROR":
                    f.write("  {} : {}\n".format(name, preview))

            f.write("\n--- MISSING ({}) ---\n".format(missing))
            for name, t, preview in r:
                if t == "MISSING":
                    f.write("  {} : {}\n".format(name, preview))

        ac.log("[" + app + "] Results written to " + log_path)
    except Exception as e:
        ac.log("[" + app + "] Failed to write results: " + str(e))
