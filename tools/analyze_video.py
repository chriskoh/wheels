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
    """Extract frames from video using ffmpeg."""
    pattern = os.path.join(output_dir, "frame_%04d.jpg")
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vf", "fps={}".format(fps),
        "-q:v", "2",
        pattern,
        "-y"
    ]
    print("Extracting frames at {} fps...".format(fps))
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
            "showing a DriftCoach HUD app. The HUD has these elements:\n"
            "- DRIFT ANGLE: big number showing body slip angle in degrees\n"
            "- State: GRIP / INITIATING / DRIFTING / SPINNING\n"
            "- COUNTER: steering counter-steer feedback\n"
            "- YAW: rotation rate\n"
            "- THROTTLE: a horizontal bar meter with a green target zone in center, "
            "needle moves left (need more throttle) or right (need less throttle)\n"
            "- Stats: max angle, longest drift, drift count, spin count\n\n"
            "Analyze these frames in sequence and describe:\n"
            "1. What the driver is doing (drifting, donuts, straight driving, etc)\n"
            "2. How the HUD elements are behaving - are they readable? responsive?\n"
            "3. Specifically for the THROTTLE meter: is the needle too twitchy? "
            "does it spend most time on one side? is the green zone appropriately sized?\n"
            "4. For the DRIFT ANGLE: do the numbers look reasonable for what the car is doing?\n"
            "5. Any issues with readability, colors, or layout\n"
            "6. Specific recommendations for threshold/range adjustments\n\n"
            "Be specific with numbers and observations. This will be used to tune the app."
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
    parser.add_argument("--fps", type=int, default=2, help="Frames per second to extract (default: 2)")
    parser.add_argument("--max-frames", type=int, default=30, help="Max frames to send to Claude (default: 30)")
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
            with open(args.output, "w") as f:
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
