"""
Video analysis tool for DriftCoach HUD tuning.
Extracts frames from a gameplay video and sends them to Claude
for analysis of the HUD elements.

Usage:
    python analyze_video.py <video_file> [--fps 2] [--max-frames 30]

Requires:
    - ffmpeg installed and on PATH
    - pip install anthropic
    - ANTHROPIC_API_KEY environment variable set
"""

import argparse
import base64
import glob
import os
import shutil
import subprocess
import sys
import tempfile

try:
    import anthropic
except ImportError:
    print("Install anthropic: pip install anthropic")
    sys.exit(1)


def extract_frames(video_path, output_dir, fps=2):
    """Extract frames from video using ffmpeg, resized to fit API limits."""
    pattern = os.path.join(output_dir, "frame_%04d.jpg")
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vf", "fps={},scale='min(1920,iw)':min'(1080,ih)':force_original_aspect_ratio=decrease".format(fps),
        "-q:v", "2",
        pattern,
        "-y"
    ]
    print("Extracting frames at {} fps...".format(fps))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Try simpler scale filter if the first one fails
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", "fps={},scale=1280:-2".format(fps),
            "-q:v", "3",
            pattern,
            "-y"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("ffmpeg error:", result.stderr)
            sys.exit(1)

    frames = sorted(glob.glob(os.path.join(output_dir, "frame_*.jpg")))
    print("Extracted {} frames".format(len(frames)))
    return frames


def encode_frame(path):
    """Read and base64 encode an image file."""
    with open(path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def analyze_frames(frames, max_frames=30):
    """Send frames to Claude for analysis."""
    client = anthropic.Anthropic()

    # Limit frames
    if len(frames) > max_frames:
        step = len(frames) // max_frames
        frames = frames[::step][:max_frames]
        print("Using {} frames for analysis".format(len(frames)))

    # Build message content with frames
    content = []
    content.append({
        "type": "text",
        "text": (
            "These are sequential frames from an Assetto Corsa gameplay video "
            "showing a DriftCoach HUD app overlaid on the game. Your job is to "
            "evaluate whether the HUD accurately reflects what the car is doing.\n\n"
            "HUD elements:\n"
            "- DRIFT ANGLE: number showing body slip angle in degrees\n"
            "- State: GRIP / INITIATING / DRIFTING / SPINNING\n"
            "- COUNTER: steering counter-steer feedback\n"
            "- YAW: rotation rate\n"
            "- THROTTLE: horizontal bar meter with green target zone, needle moves "
            "left (drift dying, need more throttle) or right (angle growing, need less). "
            "There is a debug number 'THR: X' next to it showing the raw signal value. "
            "This THR number is displayed on the main HUD panel (the one that shows "
            "DRIFT ANGLE at the top). Look for 'THR:' followed by a number directly "
            "below the YAW line on that panel. "
            "Negative number = drift dying (needle should be left). Positive number = "
            "too much gas (needle should be right). ALWAYS report this THR number in your "
            "analysis, especially during problem moments. "
            "IMPORTANT: Focus on whether the THR NUMBER is correct for the situation, "
            "not the visual needle position — the number is more reliable than trying to "
            "read the small needle from video. A negative THR when the drift is dying is "
            "CORRECT. A positive THR when the angle is growing is CORRECT.\n"
            "- Stats: max angle, longest drift, drift count, spin count\n\n"
            "For each frame, observe the CAR'S ACTUAL BEHAVIOR (angle of the car body "
            "relative to direction of travel, whether it's sliding, spinning, gripping, "
            "whether the drift angle is increasing or decreasing, whether the car looks "
            "stable or unstable) and compare it to what the HUD is showing.\n\n"
            "Analyze and report:\n"
            "1. Does the DRIFT ANGLE number match how sideways the car actually looks? "
            "Are there moments where the car is clearly sideways but the number is low, "
            "or vice versa?\n"
            "2. Does the STATE label match what the car is doing? Is it saying GRIP when "
            "the car is clearly sliding? Is it saying DRIFTING when the car is straight?\n"
            "3. For the THROTTLE meter in DriftCoach: this is a HORIZONTAL bar. "
            "The needle moves LEFT when the drift is dying (angle shrinking or speed "
            "dropping) meaning the driver needs MORE throttle. The needle moves RIGHT "
            "when the angle is growing too fast meaning the driver needs LESS throttle. "
            "Center/green zone means throttle is good. "
            "There is also a separate VERTICAL ThrottleMeter app (tall narrow bar). "
            "On the vertical meter, needle UP means too much gas (need less), needle "
            "DOWN means drift dying (need more gas), green zone in the middle means good. "
            "Both meters should show the SAME data — if one says need more gas, the other "
            "should too. Check if they agree with each other.\n"
            "For both meters check: when the car is visibly slowing down or the drift is "
            "straightening out, does the needle indicate MORE gas needed (left on horizontal, "
            "down on vertical)? When the car is spinning out or angle growing rapidly, does "
            "it indicate LESS gas needed (right on horizontal, up on vertical)? "
            "A car at 89 degrees that has nearly stopped is a DYING drift that needs MORE "
            "gas. A car with stable angle and steady speed should be in the green zone. "
            "This is the most important element to evaluate.\n"
            "4. Does the COUNTER-STEER indicator match what the front wheels appear to be "
            "doing relative to the slide direction?\n"
            "5. Are there any moments where the HUD is giving WRONG advice — telling the "
            "driver to do the opposite of what they should?\n\n"
            "Focus on ACCURACY of the data, not appearance. Be very specific about which "
            "frames show mismatches between car behavior and HUD readings."
        )
    })

    for i, frame_path in enumerate(frames):
        data = encode_frame(frame_path)
        content.append({
            "type": "text",
            "text": "Frame {} of {}:".format(i + 1, len(frames))
        })
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": data
            }
        })

    print("Sending {} frames to Claude for analysis...".format(len(frames)))

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": content}]
    )

    return response.content[0].text


def main():
    parser = argparse.ArgumentParser(description="Analyze DriftCoach HUD from gameplay video")
    parser.add_argument("video", help="Path to video file")
    parser.add_argument("--fps", type=float, default=4, help="Frames per second to extract (default: 4)")
    parser.add_argument("--max-frames", type=int, default=60, help="Max frames to send to Claude (default: 60)")
    parser.add_argument("--output", default=None, help="Output file for analysis (default: print to console)")
    args = parser.parse_args()

    if not os.path.exists(args.video):
        print("Video not found:", args.video)
        sys.exit(1)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Set ANTHROPIC_API_KEY environment variable")
        sys.exit(1)

    # Extract frames to temp dir
    tmp_dir = tempfile.mkdtemp(prefix="dc_frames_")
    try:
        frames = extract_frames(args.video, tmp_dir, fps=args.fps)
        if not frames:
            print("No frames extracted")
            sys.exit(1)

        analysis = analyze_frames(frames, max_frames=args.max_frames)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(analysis)
            print("Analysis written to", args.output)
        else:
            print("\n" + "=" * 60)
            print("ANALYSIS")
            print("=" * 60)
            print(analysis)

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
