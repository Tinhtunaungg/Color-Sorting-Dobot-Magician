import cv2
import numpy as np

# Define refined color ranges in HSV space for red, green, blue, and yellow
color_ranges = {
    'r': [(0, 120, 70), (10, 255, 255)],   # Red
    'g': [(35, 100, 100), (85, 255, 255)],    # Green
    'b': [(90, 100, 100), (130, 255, 255)],   # Blue
    'y': [(20, 100, 100), (30, 255, 255)]   # Yellow
}

def detect_color_objects(frame, color_abbreviation, lower_bound, upper_bound):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_frame, np.array(lower_bound), np.array(upper_bound))

    # Apply Gaussian Blur to smoothen edges using a 5x5 kernel
    # mask = cv2.GaussianBlur(mask, (5, 5), 0)

    # Define a 3x3 kernel for morphological operations
    kernel = np.ones((9, 9), np.uint8)

    # Apply morphological operations using the defined kernel
    # mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.erode(mask, kernel, iterations=2)
    # mask = cv2.dilate(mask, kernel, iterations=2)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    objects_positions = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 500:  # Area threshold to filter out small objects
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h

            # Additional filtering based on aspect ratio (optional)
            if 0.75 <= aspect_ratio <= 1.25:  # Filter to keep nearly square shapes
                cx, cy = x + w // 2, y + h // 2

                # Check if the object is in the left half of the frame
                if cx < frame.shape[1] // 2:
                    # Append the detected object's position and color abbreviation
                    objects_positions.append((cx, cy, color_abbreviation))
                    cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Draw bounding box
                    cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
                    cv2.putText(frame, f'{color_abbreviation.upper()} ({cx},{cy})',
                                (cx + 10, cy),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                                (255, 255, 255), 2)

    return objects_positions, mask

def combine_masks(masks):
    if not masks:
        return None
    combined_mask = masks[0]
    for mask in masks[1:]:
        combined_mask = cv2.bitwise_or(combined_mask, mask)
    return combined_mask

def main():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detected_objects = []
        masks = []

        for color_abbreviation, (lower_bound, upper_bound) in color_ranges.items():
            objects, mask = detect_color_objects(frame, color_abbreviation, lower_bound, upper_bound)
            detected_objects.extend(objects)
            masks.append(mask)

        # Combine all masks
        combined_mask = combine_masks(masks)

        # Sort detected objects by y-coordinate (cy) in descending order (bottom to top)
        detected_objects.sort(key=lambda pos: pos[1], reverse=True)

        # Limit to four objects and collect the color abbreviations in order
        color_order = [color_abbreviation for _, _, color_abbreviation in detected_objects[:4]]

        # Output the colors of the cubes on the left side (bottom to top) as a single string
        if color_order:
            print(",".join(color_order))

        cv2.imshow('Color Detection', frame)
        if combined_mask is not None:
            cv2.imshow('Combined Mask', combined_mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()