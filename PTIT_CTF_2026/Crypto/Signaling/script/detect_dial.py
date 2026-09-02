#!/usr/bin/env python3
"""
Analyze the 48 state frames to detect the rotary dial hand position.
The dial has numbers 0-9 and the hand points to different positions.
"""
import cv2
import numpy as np
import os
import glob

def find_dial_hand_angle(img):
    """
    Find the angle of the hand/pointer on the rotary dial.
    The hand appears to be a bright line or shape radiating from center.
    """
    h, w = img.shape[:2]

    # Center of the dial (approximately center of the image)
    cx, cy = w // 2, h // 2

    # Convert to HSV to find the hand color
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # The hand appears to be a yellow/orange color on a gray dial
    # Let's try to detect it by looking at the center region
    # Crop the dial area (center portion)
    r = min(h, w) // 3
    roi = img[cy-r:cy+r, cx-r:cx+r]
    roi_hsv = hsv[cy-r:cy+r, cx-r:cx+r]

    # The hand/pointer seems to be a distinctive color
    # Let's try detecting white/yellow/bright pixels in a radial pattern

    # Alternative: look at pixel values along radial lines from center
    # and find the brightest or most distinctive one

    # Actually, let's look at the image more carefully
    # The hand might be detected by edge detection or color segmentation

    # Try to find the hand by color - it appears to be yellow/orange
    # Yellow in HSV: H=20-30, S=100-255, V=100-255
    mask_yellow = cv2.inRange(roi_hsv,
                              np.array([15, 50, 150]),
                              np.array([35, 255, 255]))

    # Also try white/bright
    mask_bright = cv2.inRange(roi_hsv,
                               np.array([0, 0, 200]),
                               np.array([180, 30, 255]))

    mask = cv2.bitwise_or(mask_yellow, mask_bright)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    # Find the largest contour (likely the hand)
    largest = max(contours, key=cv2.contourArea)

    # Get the centroid
    M = cv2.moments(largest)
    if M["m00"] == 0:
        return None

    mx = int(M["m10"] / M["m00"])
    my = int(M["m01"] / M["m00"])

    # Calculate angle from center
    dx = mx - (r)  # relative to ROI center
    dy = my - (r)

    angle = np.degrees(np.arctan2(dy, dx))
    # Normalize to 0-360
    angle = (angle + 360) % 360

    return angle, (mx, my)


def find_hand_angle_hough(img):
    """
    Alternative approach: use line detection to find the hand.
    """
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    cx, cy = w // 2, h // 2

    # Edge detection
    edges = cv2.Canny(gray, 50, 150)

    # Mask out edges far from center (we only care about the dial area)
    mask = np.zeros_like(edges)
    r = min(h, w) // 3
    cv2.circle(mask, (cx, cy), r, 255, -1)
    edges = cv2.bitwise_and(edges, mask)

    # Hough lines
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)

    if lines is None:
        return None

    # Find lines that pass through or near center
    best_line = None
    best_dist = float('inf')

    for line in lines:
        x1, y1, x2, y2 = line[0]
        # Check if line is close to center
        # Distance from point to line
        dx = x2 - x1
        dy = y2 - y1
        length = np.sqrt(dx*dx + dy*dy)
        if length < 30:
            continue

        # Distance from center to line
        dist = abs(dy * cx - dx * cy + x2*y1 - y2*x1) / length

        if dist < best_dist:
            best_dist = dist
            best_line = (x1, y1, x2, y2)

    if best_line is None or best_dist > 30:
        return None

    x1, y1, x2, y2 = best_line
    # Angle of the line
    angle = np.degrees(np.arctan2(y2-y1, x2-x1))
    angle = (angle + 360) % 360

    return angle


def analyze_with_template(img_path, ref_img_path):
    """
    Compare with a reference image to detect rotation.
    """
    img = cv2.imread(img_path)
    ref = cv2.imread(ref_img_path)

    if img is None or ref is None:
        return None

    # Try template matching at different rotations
    h, w = img.shape[:2]
    cx, cy = w // 2, h // 2

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ref_gray = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)

    # Use phase correlation or feature matching
    # Actually, let's use a simpler approach: compare radial profiles

    return None


def get_radial_profile(img, cx, cy, r_min=50, r_max=300, n_angles=360):
    """
    Get the average pixel intensity at each angle around the center.
    This can detect the hand position as a peak.
    """
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    profile = np.zeros(n_angles)
    counts = np.zeros(n_angles)

    for y in range(max(0, cy-r_max), min(h, cy+r_max)):
        for x in range(max(0, cx-r_max), min(w, cx+r_max)):
            dx = x - cx
            dy = y - cy
            dist = np.sqrt(dx*dx + dy*dy)
            if r_min < dist < r_max:
                angle = np.degrees(np.arctan2(dy, dx))
                angle_idx = int((angle + 180) / 360 * n_angles) % n_angles
                profile[angle_idx] += gray[y, x]
                counts[angle_idx] += 1

    # Normalize
    mask = counts > 0
    profile[mask] /= counts[mask]

    return profile


def detect_hand_by_color_segmentation(img):
    """
    Detect the hand/pointer by looking for distinctive colored regions
    that extend from center outward.
    """
    h, w = img.shape[:2]
    cx, cy = w // 2, h // 2

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # The hand appears to be a yellow/orange color
    # Let's try a range
    lower = np.array([10, 80, 150])
    upper = np.array([40, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)

    # Also try to find a bright white/light colored hand
    mask2 = cv2.inRange(hsv, np.array([0, 0, 180]), np.array([180, 40, 255]))
    mask = cv2.bitwise_or(mask, mask2)

    # Dilate to connect nearby pixels
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=2)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    # For each contour, check if it extends from center outward
    best_contour = None
    best_score = -1

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 100:
            continue

        # Get centroid
        M = cv2.moments(cnt)
        if M["m00"] == 0:
            continue

        mx = M["m10"] / M["m00"]
        my = M["m01"] / M["m00"]

        # Distance from center
        dist = np.sqrt((mx - cx)**2 + (my - cy)**2)

        # Score: prefer contours that are far from center (hand extends outward)
        # but not too far
        if 30 < dist < min(h, w) // 3:
            score = area * dist
            if score > best_score:
                best_score = score
                best_contour = cnt

    if best_contour is None:
        return None

    M = cv2.moments(best_contour)
    mx = int(M["m10"] / M["m00"])
    my = int(M["m01"] / M["m00"])

    angle = np.degrees(np.arctan2(my - cy, mx - cx))
    angle = (angle + 360) % 360

    return angle


def main():
    states_dir = '/home/light/Workspace/CTF/PTIT_CTF_2026/Crypto/Signaling/script/states'

    # Get all state images
    state_files = sorted(glob.glob(os.path.join(states_dir, 'state_*.png')))
    print(f"Found {len(state_files)} state images")

    angles = []
    for sf in state_files:
        img = cv2.imread(sf)
        if img is None:
            print(f"Failed to read {sf}")
            continue

        # Try color-based detection
        angle = detect_hand_by_color_segmentation(img)

        if angle is None:
            # Fallback to Hough lines
            angle = find_hand_angle_hough(img)

        basename = os.path.basename(sf)
        if angle is not None:
            angles.append((basename, angle))
            print(f"{basename}: angle = {angle:.1f} degrees")
        else:
            angles.append((basename, None))
            print(f"{basename}: could not detect hand")

    # Now let's see if there's a pattern
    print("\n--- Angle analysis ---")
    valid_angles = [a for _, a in angles if a is not None]
    if valid_angles:
        print(f"Min angle: {min(valid_angles):.1f}")
        print(f"Max angle: {max(valid_angles):.1f}")
        print(f"Mean angle: {np.mean(valid_angles):.1f}")

        # Cluster angles to find discrete positions
        # A rotary phone has 10 positions (0-9)
        # Let's see what angles we get
        print("\nAll angles sorted:")
        for name, angle in sorted(angles, key=lambda x: x[1] if x[1] is not None else 999):
            if angle is not None:
                print(f"  {name}: {angle:.1f}")


if __name__ == '__main__':
    main()
