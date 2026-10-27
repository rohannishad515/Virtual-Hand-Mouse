import cv2
import mediapipe as mp
import pyautogui
import math


# setting up hand detector for up to 2 hands
base_options = mp.tasks.BaseOptions(
    model_asset_path="hand_landmarker.task"
)

options = mp.tasks.vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=mp.tasks.vision.RunningMode.VIDEO,
    num_hands=2
)

detector = mp.tasks.vision.HandLandmarker.create_from_options(options)


# opening camera
cap = cv2.VideoCapture(0)
timestamp = 0

if not cap.isOpened():
    print("Camera could not be opened.")
    exit()


# getting screen size
screen_width, screen_height = pyautogui.size()

cv2.namedWindow("Hand Gesture Mouse", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Hand Gesture Mouse", 1000, 700)


left_clicking = False
right_clicking = False
dragging = False

previous_y = None
previous_zoom_dist = None

# makes cursor movement smoother
smooth_x = 0
smooth_y = 0
smooth_factor = 0.25


while True:

    ret, frame = cap.read()

    if not ret:
        break

    # -------------------------------------------------------------
    # CAMERA MIRROR FIX: Frame ko horizontally flip karein
    # taaki left/right movement natural ho jaye
    # -------------------------------------------------------------
    frame = cv2.flip(frame, 1)

    gesture = "NO HAND"

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    timestamp += 1

    results = detector.detect_for_video(
        mp_image,
        timestamp
    )


    if results.hand_landmarks:

        # -------------------------------------------------------------
        # TWO HANDS ZOOM (Using ONLY ONE FINGER - Index Finger of both hands)
        # -------------------------------------------------------------
        if len(results.hand_landmarks) == 2:
            gesture = "BOTH HANDS ZOOM"

            if dragging:
                pyautogui.mouseUp()
                dragging = False

            left_clicking = False
            right_clicking = False
            previous_y = None

            # Get index fingertips (Landmark 8) for both hands directly
            hand1 = results.hand_landmarks[0]
            hand2 = results.hand_landmarks[1]

            idx1_x = int(hand1[8].x * frame.shape[1])
            idx1_y = int(hand1[8].y * frame.shape[0])

            idx2_x = int(hand2[8].x * frame.shape[1])
            idx2_y = int(hand2[8].y * frame.shape[0])

            # Highlight only the index fingertips on both hands
            cv2.circle(frame, (idx1_x, idx1_y), 12, (0, 0, 255), -1)
            cv2.circle(frame, (idx2_x, idx2_y), 12, (0, 0, 255), -1)

            # Draw a line connecting the two index fingers
            cv2.line(frame, (idx1_x, idx1_y), (idx2_x, idx2_y), (255, 255, 0), 2)

            # Distance between index fingertips
            two_hand_distance = math.hypot(idx2_x - idx1_x, idx2_y - idx1_y)

            if previous_zoom_dist is not None:
                zoom_diff = two_hand_distance - previous_zoom_dist

                # Fingers moving apart -> Zoom In
                if zoom_diff > 5:
                    pyautogui.hotkey('ctrl', '+')
                # Fingers moving closer -> Zoom Out
                elif zoom_diff < -5:
                    pyautogui.hotkey('ctrl', '-')

            previous_zoom_dist = two_hand_distance

        # -------------------------------------------------------------
        # SINGLE HAND MOUSE CONTROLS (Full 21 landmarks)
        # -------------------------------------------------------------
        elif len(results.hand_landmarks) == 1:
            previous_zoom_dist = None
            hand_landmarks = results.hand_landmarks[0]
            points = []

            for landmark in hand_landmarks:
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                points.append((x, y))

                cv2.circle(
                    frame,
                    (x, y),
                    5,
                    (0, 255, 0),
                    -1
                )

            connections = [
                (0,1), (1,2), (2,3), (3,4),
                (0,5), (5,6), (6,7), (7,8),
                (0,9), (9,10), (10,11), (11,12),
                (0,13), (13,14), (14,15), (15,16),
                (0,17), (17,18), (18,19), (19,20),
                (5,9), (9,13), (13,17)
            ]

            for start, end in connections:
                cv2.line(
                    frame,
                    points[start],
                    points[end],
                    (0, 255, 0),
                    2
                )

            thumb_x, thumb_y = points[4]
            index_x, index_y = points[8]
            middle_x, middle_y = points[12]

            thumb_index_distance = math.hypot(
                index_x - thumb_x,
                index_y - thumb_y
            )

            index_middle_distance = math.hypot(
                index_x - middle_x,
                index_y - middle_y
            )

            middle_extended = (
                middle_y < points[10][1]
            )

            # scroll
            if (
                middle_extended
                and index_middle_distance > 40
                and thumb_index_distance > 40
            ):

                gesture = "SCROLL"

                if previous_y is not None:
                    movement = previous_y - middle_y
                    if abs(movement) > 3:
                        pyautogui.scroll(int(movement / 3))

                previous_y = middle_y
                left_clicking = False
                right_clicking = False

            # drag
            elif (
                thumb_index_distance < 30
                and index_middle_distance > 40
            ):

                gesture = "DRAG"

                if not dragging:
                    pyautogui.mouseDown()
                    dragging = True

                mouse_x = int(index_x / frame.shape[1] * screen_width)
                mouse_y = int(index_y / frame.shape[0] * screen_height)

                smooth_x = smooth_x + (mouse_x - smooth_x) * smooth_factor
                smooth_y = smooth_y + (mouse_y - smooth_y) * smooth_factor

                pyautogui.moveTo(int(smooth_x), int(smooth_y))
                previous_y = None

            # right click
            elif (
                index_middle_distance < 30
                and thumb_index_distance > 40
            ):

                gesture = "RIGHT CLICK"

                if not right_clicking:
                    pyautogui.rightClick()
                    right_clicking = True

                left_clicking = False
                previous_y = None

            # left click
            elif (
                thumb_index_distance < 30
                and index_middle_distance < 40
            ):

                gesture = "LEFT CLICK"

                if not left_clicking:
                    pyautogui.click()
                    left_clicking = True

                right_clicking = False
                previous_y = None

            # normal cursor movement
            else:

                gesture = "MOVE"

                if dragging:
                    pyautogui.mouseUp()
                    dragging = False

                left_clicking = False
                right_clicking = False
                previous_y = None

                mouse_x = int(index_x / frame.shape[1] * screen_width)
                mouse_y = int(index_y / frame.shape[0] * screen_height)

                smooth_x = smooth_x + (mouse_x - smooth_x) * smooth_factor
                smooth_y = smooth_y + (mouse_y - smooth_y) * smooth_factor

                pyautogui.moveTo(int(smooth_x), int(smooth_y))

            # highlight index finger
            cv2.circle(
                frame,
                (index_x, index_y),
                10,
                (255, 0, 0),
                -1
            )


    else:

        previous_y = None
        previous_zoom_dist = None

        if dragging:

            pyautogui.mouseUp()
            dragging = False


    # show current gesture
    cv2.putText(
        frame,
        "Gesture: " + gesture,
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2
    )


    cv2.imshow(
        "Hand Gesture Mouse",
        frame
    )


    # press q or esc to close
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q") or key == 27:
        break


    # close using the X button
    if cv2.getWindowProperty(
        "Hand Gesture Mouse",
        cv2.WND_PROP_VISIBLE
    ) < 1:
        break


# cleanup
if dragging:
    pyautogui.mouseUp()

cap.release()
cv2.destroyAllWindows()
detector.close()
