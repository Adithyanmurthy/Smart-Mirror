import cv2
import numpy as np
import time
import argparse
import base64
import json
import sys
from pose_detection import PoseDetector
from exercise_predictor import ExercisePredictor
from utils import draw_feedback, calculate_stats

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera_index", type=int, default=0)
    parser.add_argument("--exercise_type", type=str, default="Automatic Detection")
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Initialize components
    pose_detector = PoseDetector()
    exercise_predictor = ExercisePredictor()
    
    # Initialize session state
    rep_count = 0
    start_time = time.time()
    feedback = []
    exercise_history = []
    current_exercise = "None detected"
    
    # Camera setup
    cap = cv2.VideoCapture(args.camera_index)
    if not cap.isOpened():
        send_message("ERROR", {"message": f"Could not open camera {args.camera_index}"})
        return
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                send_message("ERROR", {"message": "Could not read frame from camera"})
                time.sleep(1)
                continue
            
            # Process frame
            frame = cv2.flip(frame, 1)
            frame, landmarks = pose_detector.detect_pose(frame)
            
            if landmarks is not None and len(landmarks) > 0:
                # Predict exercise type if in auto mode
                if args.exercise_type == "Automatic Detection":
                    current_exercise = exercise_predictor.predict_exercise(landmarks)
                else:
                    current_exercise = args.exercise_type
                
                # Count repetitions and get feedback
                rep_count, new_feedback = exercise_predictor.count_repetitions(landmarks, current_exercise)
                
                if new_feedback and new_feedback not in feedback:
                    feedback.append(new_feedback)
                
                # Draw feedback cues
                frame = draw_feedback(frame, landmarks, new_feedback)
                
                # Check for exercise completion
                if rep_count > 0 and rep_count % 10 == 0 and current_exercise not in exercise_history:
                    next_exercise = exercise_predictor.suggest_next_exercise(current_exercise)
                    feedback.append(f"Great job! Try {next_exercise} next")
                    exercise_history.append(current_exercise)
            
            # Calculate stats
            elapsed_time = time.time() - start_time
            calories, avg_reps_per_min = calculate_stats(rep_count, elapsed_time)
            
            # Convert frame to base64 for web transport
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Prepare message
            message = {
                "frame": f"data:image/jpeg;base64,{frame_base64}",
                "repCount": rep_count,
                "exercise": current_exercise,
                "feedback": feedback[-3:],  # Last 3 feedback items
                "stats": {
                    "calories": calories,
                    "repsPerMin": avg_reps_per_min
                }
            }
            
            send_message("VIDEO_FRAME", message)
            
            # Limit frame rate
            time.sleep(0.05)
    
    except Exception as e:
        send_message("ERROR", {"message": str(e)})
    finally:
        cap.release()

def send_message(message_type, payload):
    """Send a message to the Node.js process"""
    message = json.dumps({"type": message_type, "payload": payload})
    print(message)
    sys.stdout.flush()

if __name__ == "__main__":
    main()