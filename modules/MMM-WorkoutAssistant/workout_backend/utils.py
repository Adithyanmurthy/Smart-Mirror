import numpy as np
import cv2
import mediapipe as mp

def calculate_angle(a, b, c):
    """
    Calculate the angle between three points (in degree).
    
    Args:
        a (tuple/list/array): First point coordinates (x, y)
        b (tuple/list/array): Middle point coordinates (x, y)
        c (tuple/list/array): Last point coordinates (x, y)
        
    Returns:
        float: Angle in degrees
    """
    try:
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        # Check for valid inputs
        if (np.array_equal(a, b) or np.array_equal(b, c) or 
            np.isnan(a).any() or np.isnan(b).any() or np.isnan(c).any()):
            return 0.0
        
        # Create vectors from points
        ba = a - b
        bc = c - b
        
        # Check for zero vectors
        if np.all(ba == 0) or np.all(bc == 0):
            return 0.0
        
        # Calculate cosine of angle using dot product
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        
        # Handle numerical errors
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
        
        # Calculate angle in degrees
        angle = np.degrees(np.arccos(cosine_angle))
        
        # If calculation produces NaN, return default value
        if np.isnan(angle):
            return 0.0
            
        return angle
    
    except Exception as e:
        print(f"Error calculating angle: {e}")
        return 0.0

def get_landmark_positions(landmarks):
    """
    Extract key landmark positions from MediaPipe landmarks.
    
    Args:
        landmarks (numpy.ndarray): Array of landmarks from MediaPipe
        
    Returns:
        dict: Dictionary of key positions or empty dict if error
    """
    try:
        if landmarks is None or len(landmarks) == 0:
            return {}
        
        # MediaPipe pose indices
        mp_pose = mp.solutions.pose.PoseLandmark
        
        # Create a dict to store positions
        positions = {}
        
        # Define landmark mappings
        landmark_map = {
            "nose": mp_pose.NOSE.value,
            "left_eye": mp_pose.LEFT_EYE.value,
            "right_eye": mp_pose.RIGHT_EYE.value,
            "left_shoulder": mp_pose.LEFT_SHOULDER.value,
            "right_shoulder": mp_pose.RIGHT_SHOULDER.value,
            "left_elbow": mp_pose.LEFT_ELBOW.value,
            "right_elbow": mp_pose.RIGHT_ELBOW.value,
            "left_wrist": mp_pose.LEFT_WRIST.value,
            "right_wrist": mp_pose.RIGHT_WRIST.value,
            "left_hip": mp_pose.LEFT_HIP.value,
            "right_hip": mp_pose.RIGHT_HIP.value,
            "left_knee": mp_pose.LEFT_KNEE.value,
            "right_knee": mp_pose.RIGHT_KNEE.value,
            "left_ankle": mp_pose.LEFT_ANKLE.value,
            "right_ankle": mp_pose.RIGHT_ANKLE.value,
        }
        
        # Extract positions with error checking
        for name, idx in landmark_map.items():
            if 0 <= idx < len(landmarks):
                # Only use x,y coordinates (first 2 elements)
                positions[name] = landmarks[idx][:2]
            else:
                # Use a default position if landmark is missing
                positions[name] = np.array([0.0, 0.0])
        
        # Calculate midpoints for easier reference
        if all(k in positions for k in ["left_shoulder", "right_shoulder"]):
            positions["neck"] = (positions["left_shoulder"] + positions["right_shoulder"]) / 2
            positions["shoulder_center"] = (positions["left_shoulder"] + positions["right_shoulder"]) / 2
        else:
            positions["neck"] = np.array([0.5, 0.2])  # Default neck position
            positions["shoulder_center"] = np.array([0.5, 0.2])
            
        if all(k in positions for k in ["left_hip", "right_hip"]):
            positions["hip_center"] = (positions["left_hip"] + positions["right_hip"]) / 2
        else:
            positions["hip_center"] = np.array([0.5, 0.5])  # Default hip position
            
        if all(k in positions for k in ["left_knee", "right_knee"]):
            positions["knee_center"] = (positions["left_knee"] + positions["right_knee"]) / 2
        else:
            positions["knee_center"] = np.array([0.5, 0.7])  # Default knee position
            
        if all(k in positions for k in ["left_ankle", "right_ankle"]):
            positions["ankle_center"] = (positions["left_ankle"] + positions["right_ankle"]) / 2
        else:
            positions["ankle_center"] = np.array([0.5, 0.9])  # Default ankle position
        
        return positions
    
    except Exception as e:
        print(f"Error extracting landmark positions: {e}")
        return {}

def draw_feedback(frame, landmarks, feedback):
    """
    Draw feedback on the frame based on pose analysis.
    
    Args:
        frame (numpy.ndarray): Video frame
        landmarks (numpy.ndarray): Pose landmarks
        feedback (str): Feedback message
        
    Returns:
        numpy.ndarray: Frame with feedback visualization
    """
    try:
        if frame is None or not feedback or landmarks is None:
            return frame
        
        height, width, _ = frame.shape
        
        # Draw feedback text at the top of the frame
        cv2.putText(
            frame,
            feedback,
            (int(width * 0.1), int(height * 0.1)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2,
            cv2.LINE_AA
        )
        
        # Get positions for visual cues
        positions = get_landmark_positions(landmarks)
        if not positions:
            return frame
        
        # Draw visual cues based on feedback type
        
        # Knee alignment feedback (squats and lunges)
        if "knee" in feedback.lower() and "aligned" in feedback.lower():
            # Draw line from hip to knee to ankle to show alignment
            for side in ["left", "right"]:
                if all(k in positions for k in [f"{side}_hip", f"{side}_knee", f"{side}_ankle"]):
                    hip = (int(positions[f"{side}_hip"][0] * width), int(positions[f"{side}_hip"][1] * height))
                    knee = (int(positions[f"{side}_knee"][0] * width), int(positions[f"{side}_knee"][1] * height))
                    ankle = (int(positions[f"{side}_ankle"][0] * width), int(positions[f"{side}_ankle"][1] * height))
                    
                    # Draw corrective alignment line
                    cv2.line(frame, hip, ankle, (0, 255, 0), 2)
                    
                    # Draw current alignment line
                    cv2.line(frame, hip, knee, (0, 0, 255), 2)
                    cv2.line(frame, knee, ankle, (0, 0, 255), 2)
        
        # Back alignment feedback
        elif "back" in feedback.lower() and "straight" in feedback.lower():
            # Draw line along spine to show alignment
            if all(k in positions for k in ["hip_center", "shoulder_center"]):
                hip_center = (int(positions["hip_center"][0] * width), int(positions["hip_center"][1] * height))
                shoulder_center = (int(positions["shoulder_center"][0] * width), int(positions["shoulder_center"][1] * height))
                
                # Draw corrective straight line
                cv2.line(frame, (hip_center[0], hip_center[1]), (hip_center[0], shoulder_center[1]), (0, 255, 0), 2)
                
                # Draw current spine line
                cv2.line(frame, hip_center, shoulder_center, (0, 0, 255), 2)
        
        # Depth feedback (squats, push-ups, lunges)
        elif any(word in feedback.lower() for word in ["deeper", "lower", "depth"]):
            # Draw target depth line
            if "squat" in feedback.lower() and "knee_center" in positions:
                knee_center = (int(positions["knee_center"][0] * width), int(positions["knee_center"][1] * height))
                target_depth = (knee_center[0], knee_center[1] + int(height * 0.1))
                cv2.line(frame, (knee_center[0] - 50, target_depth[1]), (knee_center[0] + 50, target_depth[1]), (0, 255, 0), 2)
            
            elif "push" in feedback.lower() and "shoulder_center" in positions:
                shoulder_center = (int(positions["shoulder_center"][0] * width), int(positions["shoulder_center"][1] * height))
                target_depth = (shoulder_center[0], shoulder_center[1] + int(height * 0.05))
                cv2.line(frame, (shoulder_center[0] - 50, target_depth[1]), (shoulder_center[0] + 50, target_depth[1]), (0, 255, 0), 2)
        
        # Arm movement feedback (bicep curls)
        elif "arm" in feedback.lower() and "still" in feedback.lower():
            # Draw lines showing proper arm position
            for side in ["left", "right"]:
                if f"{side}_shoulder" in positions:
                    shoulder = (int(positions[f"{side}_shoulder"][0] * width), int(positions[f"{side}_shoulder"][1] * height))
                    
                    # Draw vertical line from shoulder to indicate proper position
                    cv2.line(frame, shoulder, (shoulder[0], shoulder[1] + 100), (0, 255, 0), 2)
        
        # For jumping jacks - arm height
        elif "arm" in feedback.lower() and "higher" in feedback.lower():
            if all(k in positions for k in ["left_shoulder", "right_shoulder"]):
                left_shoulder = (int(positions["left_shoulder"][0] * width), int(positions["left_shoulder"][1] * height))
                right_shoulder = (int(positions["right_shoulder"][0] * width), int(positions["right_shoulder"][1] * height))
                
                # Draw target arm position
                cv2.line(frame, left_shoulder, (left_shoulder[0] - 50, left_shoulder[1] - 100), (0, 255, 0), 2)
                cv2.line(frame, right_shoulder, (right_shoulder[0] + 50, right_shoulder[1] - 100), (0, 255, 0), 2)
        
        return frame
    
    except Exception as e:
        print(f"Error drawing feedback: {e}")
        return frame

def calculate_stats(rep_count, elapsed_time):
    """
    Calculate workout statistics.
    
    Args:
        rep_count (int): Number of repetitions
        elapsed_time (float): Elapsed time in seconds
        
    Returns:
        tuple: (estimated calories burned, average reps per minute)
    """
    try:
        # Very rough estimation (don't take these values too seriously)
        # Actual calorie burn depends on many factors like weight, exercise type, intensity, etc.
        
        # Estimate calories burned (rough approximation)
        calories_per_rep = 0.3  # Very approximate
        estimated_calories = rep_count * calories_per_rep
        
        # Calculate average reps per minute
        minutes = max(elapsed_time / 60, 0.01)  # Avoid division by zero
        avg_reps_per_min = rep_count / minutes
        
        return estimated_calories, avg_reps_per_min
    
    except Exception as e:
        print(f"Error calculating stats: {e}")
        return 0, 0