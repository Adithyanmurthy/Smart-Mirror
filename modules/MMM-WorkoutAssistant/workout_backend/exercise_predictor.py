import numpy as np
import time
from utils import calculate_angle, get_landmark_positions

class ExercisePredictor:
    """Class for predicting exercise type and counting repetitions based on pose."""
    
    def __init__(self):
        # Track the repetition state
        self.rep_count = 0
        self.is_in_start_position = False
        self.is_in_end_position = False
        self.last_rep_time = time.time()
        self.current_exercise = None
        self.last_prediction = None
        self.prediction_confidence = 0
        
        # Thresholds for different exercises (angles in degrees)
        self.thresholds = {
            "Squats": {
                "knee_angle_min": 70,      # Knee bent during squat
                "knee_angle_max": 160,     # Knee extended at top
                "hip_angle_min": 50,       # Hip angle during squat
                "hip_angle_max": 160       # Hip extended at top
            },
            "Push-ups": {
                "elbow_angle_min": 70,     # Elbow bent during push-up
                "elbow_angle_max": 160,    # Elbow extended at top
                "shoulder_angle_min": 30,  # Shoulder angle during push-up
                "shoulder_angle_max": 90   # Shoulder angle at top
            },
            "Jumping Jacks": {
                "arm_spread_min": 20,      # Arms down
                "arm_spread_max": 140,     # Arms up
                "leg_spread_min": 10,      # Legs together
                "leg_spread_max": 50       # Legs apart
            },
            "Lunges": {
                "front_knee_min": 70,      # Front knee bent
                "front_knee_max": 160,     # Knee extended
                "back_knee_min": 70,       # Back knee bent
                "back_knee_max": 160       # Both knees extended
            },
            "Bicep Curls": {
                "elbow_angle_min": 45,     # Elbow fully bent
                "elbow_angle_max": 160     # Elbow extended
            }
        }
        
        # Feature Windows for exercise prediction
        self.window_size = 30
        self.feature_window = []
        
        # Prediction smoothing
        self.prediction_history = []
        self.history_size = 5
    
    def predict_exercise(self, landmarks):
        """
        Predicts the current exercise based on body landmarks and movement patterns.
        
        Args:
            landmarks (numpy.ndarray): Body landmarks from pose detection
            
        Returns:
            str: Predicted exercise type
        """
        # Validate input
        if landmarks is None or len(landmarks) == 0:
            return "No pose detected"
        
        try:
            # Add current landmark to our feature window
            self.feature_window.append(landmarks)
            
            # Keep window size fixed
            if len(self.feature_window) > self.window_size:
                self.feature_window.pop(0)
            
            # Need enough frames to make a prediction
            if len(self.feature_window) < 5:
                return "Warming up..."
            
            # Extract key joint positions
            positions = get_landmark_positions(landmarks)
            if not positions:
                return "Pose incomplete"
            
            # Calculate joint angles for classification
            right_knee_angle = calculate_angle(
                positions.get("right_hip", [0, 0]), 
                positions.get("right_knee", [0, 0]), 
                positions.get("right_ankle", [0, 0])
            )
            
            left_knee_angle = calculate_angle(
                positions.get("left_hip", [0, 0]), 
                positions.get("left_knee", [0, 0]), 
                positions.get("left_ankle", [0, 0])
            )
            
            right_elbow_angle = calculate_angle(
                positions.get("right_shoulder", [0, 0]), 
                positions.get("right_elbow", [0, 0]), 
                positions.get("right_wrist", [0, 0])
            )
            
            left_elbow_angle = calculate_angle(
                positions.get("left_shoulder", [0, 0]), 
                positions.get("left_elbow", [0, 0]), 
                positions.get("left_wrist", [0, 0])
            )
            
            right_shoulder_angle = calculate_angle(
                positions.get("right_hip", [0, 0]), 
                positions.get("right_shoulder", [0, 0]), 
                positions.get("right_elbow", [0, 0])
            )
            
            left_shoulder_angle = calculate_angle(
                positions.get("left_hip", [0, 0]), 
                positions.get("left_shoulder", [0, 0]), 
                positions.get("left_elbow", [0, 0])
            )
            
            # Calculate arm and leg spread for jumping jacks
            arm_spread = calculate_angle(
                positions.get("left_wrist", [0, 0]),
                positions.get("neck", [0, 0]),
                positions.get("right_wrist", [0, 0])
            )
            
            leg_spread = calculate_angle(
                positions.get("left_ankle", [0, 0]),
                positions.get("hip_center", [0, 0]),
                positions.get("right_ankle", [0, 0])
            )
            
            # Simple heuristic classification based on key angles and positions
            # Check for characteristic movement patterns
            prediction = None
            confidence = 0
            
            # SQUAT check
            if (right_knee_angle < 120 and left_knee_angle < 120 and 
                positions.get("hip_center", [0, 0])[1] > positions.get("knee_center", [0, 0])[1] and
                arm_spread < 100):
                prediction = "Squats"
                confidence = 0.7
            
            # PUSH-UP check (look for horizontal body and bent elbows)
            elif (abs(positions.get("shoulder_center", [0, 0])[1] - positions.get("ankle_center", [0, 0])[1]) < 0.15 and
                  right_elbow_angle < 120 and left_elbow_angle < 120):
                prediction = "Push-ups"
                confidence = 0.8
            
            # JUMPING JACK check
            elif (arm_spread > 100 and leg_spread > 30):
                prediction = "Jumping Jacks"
                confidence = 0.9
            
            # LUNGE check
            elif ((right_knee_angle < 120 and left_knee_angle > 150) or 
                  (left_knee_angle < 120 and right_knee_angle > 150)):
                prediction = "Lunges"
                confidence = 0.7
            
            # BICEP CURL check
            elif ((right_elbow_angle < 100 and right_shoulder_angle < 60) or
                  (left_elbow_angle < 100 and left_shoulder_angle < 60)):
                prediction = "Bicep Curls"
                confidence = 0.8
            
            # Apply prediction smoothing
            if prediction:
                self.prediction_history.append(prediction)
                if len(self.prediction_history) > self.history_size:
                    self.prediction_history.pop(0)
                
                # Count occurrences of each exercise in history
                prediction_counts = {}
                for pred in self.prediction_history:
                    prediction_counts[pred] = prediction_counts.get(pred, 0) + 1
                
                # Find most common prediction
                most_common = max(prediction_counts.items(), key=lambda x: x[1])
                
                # If prediction is consistent enough, update current exercise
                if most_common[1] >= 3:  # At least 3 out of 5 frames predict the same exercise
                    self.current_exercise = most_common[0]
                    self.prediction_confidence = most_common[1] / len(self.prediction_history)
            
            # Default - if we can't classify confidently
            if not self.current_exercise:
                self.current_exercise = "Movement detected"
            
            return self.current_exercise
        
        except Exception as e:
            print(f"Error in exercise prediction: {e}")
            # Return last valid prediction or default
            return self.current_exercise if self.current_exercise else "Movement detected"
    
    def count_repetitions(self, landmarks, exercise_type):
        """
        Count repetitions for a specific exercise.
        
        Args:
            landmarks (numpy.ndarray): Body landmarks from pose detection
            exercise_type (str): Type of exercise to count
            
        Returns:
            tuple: (rep_count, feedback_string or None)
        """
        if landmarks is None or len(landmarks) == 0:
            return self.rep_count, None
        
        feedback = None
        
        try:
            # Extract positions of key joints
            positions = get_landmark_positions(landmarks)
            if not positions:
                return self.rep_count, None
            
            # Handle different exercises
            if exercise_type == "Squats":
                feedback = self._count_squats(positions)
            
            elif exercise_type == "Push-ups":
                feedback = self._count_pushups(positions)
            
            elif exercise_type == "Jumping Jacks":
                feedback = self._count_jumping_jacks(positions)
                
            elif exercise_type == "Lunges":
                feedback = self._count_lunges(positions)
                
            elif exercise_type == "Bicep Curls":
                feedback = self._count_bicep_curls(positions)
        
        except Exception as e:
            print(f"Error in rep counting: {e}")
        
        # Return the current rep count and any feedback
        return self.rep_count, feedback
    
    def _count_squats(self, positions):
        """Count squat repetitions and provide feedback."""
        try:
            # Calculate key angles
            right_knee_angle = calculate_angle(
                positions.get("right_hip", [0, 0]), 
                positions.get("right_knee", [0, 0]), 
                positions.get("right_ankle", [0, 0])
            )
            
            left_knee_angle = calculate_angle(
                positions.get("left_hip", [0, 0]), 
                positions.get("left_knee", [0, 0]), 
                positions.get("left_ankle", [0, 0])
            )
            
            hip_angle = calculate_angle(
                positions.get("shoulder_center", [0, 0]),
                positions.get("hip_center", [0, 0]),
                positions.get("knee_center", [0, 0])
            )
            
            # Average left and right knee angles
            knee_angle = (right_knee_angle + left_knee_angle) / 2
            
            thresholds = self.thresholds["Squats"]
            
            # Detect start position (standing)
            if not self.is_in_start_position and knee_angle > thresholds["knee_angle_max"] - 10:
                self.is_in_start_position = True
                self.is_in_end_position = False
            
            # Detect end position (squatting)
            elif self.is_in_start_position and not self.is_in_end_position and knee_angle < thresholds["knee_angle_min"] + 10:
                self.is_in_end_position = True
            
            # Count rep when returning to start from end
            elif self.is_in_start_position and self.is_in_end_position and knee_angle > thresholds["knee_angle_max"] - 20:
                self.rep_count += 1
                self.is_in_start_position = True
                self.is_in_end_position = False
                self.last_rep_time = time.time()
            
            # Generate feedback based on form
            feedback = None
            
            # Check if knees are going too far forward
            knee_x = positions.get("knee_center", [0, 0])[0]
            ankle_x = positions.get("ankle_center", [0, 0])[0]
            
            if knee_angle < 100 and (knee_x - ankle_x) > 0.1:
                feedback = "Keep knees behind toes during squat"
            
            # Check if back is not straight
            if hip_angle < 120:
                feedback = "Keep your back straight"
            
            # Check if squat is deep enough when in end position
            if self.is_in_end_position and knee_angle > 100:
                feedback = "Try to squat deeper"
            
            return feedback
        
        except Exception as e:
            print(f"Error counting squats: {e}")
            return None
    
    def _count_pushups(self, positions):
        """Count push-up repetitions and provide feedback."""
        try:
            # Calculate elbow angles
            right_elbow_angle = calculate_angle(
                positions.get("right_shoulder", [0, 0]), 
                positions.get("right_elbow", [0, 0]), 
                positions.get("right_wrist", [0, 0])
            )
            
            left_elbow_angle = calculate_angle(
                positions.get("left_shoulder", [0, 0]), 
                positions.get("left_elbow", [0, 0]), 
                positions.get("left_wrist", [0, 0])
            )
            
            # Average the angles
            elbow_angle = (right_elbow_angle + left_elbow_angle) / 2
            
            # Calculate back angle (should be straight)
            back_angle = calculate_angle(
                positions.get("shoulder_center", [0, 0]),
                positions.get("hip_center", [0, 0]),
                positions.get("ankle_center", [0, 0])
            )
            
            thresholds = self.thresholds["Push-ups"]
            
            # Detect start position (arms extended)
            if not self.is_in_start_position and elbow_angle > thresholds["elbow_angle_max"] - 10:
                self.is_in_start_position = True
                self.is_in_end_position = False
            
            # Detect end position (arms bent)
            elif self.is_in_start_position and not self.is_in_end_position and elbow_angle < thresholds["elbow_angle_min"] + 10:
                self.is_in_end_position = True
            
            # Count rep when returning to start from end
            elif self.is_in_start_position and self.is_in_end_position and elbow_angle > thresholds["elbow_angle_max"] - 20:
                self.rep_count += 1
                self.is_in_start_position = True
                self.is_in_end_position = False
                self.last_rep_time = time.time()
            
            # Generate feedback based on form
            feedback = None
            
            # Check if back is not straight
            if back_angle < 160 or back_angle > 200:
                feedback = "Keep your back straight"
            
            # Check if push-up depth is sufficient
            if self.is_in_end_position and elbow_angle > 100:
                feedback = "Try to lower your chest more"
            
            return feedback
        
        except Exception as e:
            print(f"Error counting push-ups: {e}")
            return None
    
    def _count_jumping_jacks(self, positions):
        """Count jumping jack repetitions and provide feedback."""
        try:
            # Calculate arm spread
            arm_spread = calculate_angle(
                positions.get("left_wrist", [0, 0]),
                positions.get("neck", [0, 0]),
                positions.get("right_wrist", [0, 0])
            )
            
            # Calculate leg spread
            leg_spread = calculate_angle(
                positions.get("left_ankle", [0, 0]),
                positions.get("hip_center", [0, 0]),
                positions.get("right_ankle", [0, 0])
            )
            
            thresholds = self.thresholds["Jumping Jacks"]
            
            # Detect start position (arms and legs together)
            if not self.is_in_start_position and arm_spread < thresholds["arm_spread_min"] + 20 and leg_spread < thresholds["leg_spread_min"] + 10:
                self.is_in_start_position = True
                self.is_in_end_position = False
            
            # Detect end position (arms and legs spread)
            elif self.is_in_start_position and not self.is_in_end_position and arm_spread > thresholds["arm_spread_max"] - 20 and leg_spread > thresholds["leg_spread_max"] - 10:
                self.is_in_end_position = True
            
            # Count rep when returning to start from end
            elif self.is_in_start_position and self.is_in_end_position and arm_spread < thresholds["arm_spread_min"] + 30 and leg_spread < thresholds["leg_spread_min"] + 20:
                self.rep_count += 1
                self.is_in_start_position = True
                self.is_in_end_position = False
                self.last_rep_time = time.time()
            
            # Generate feedback based on form
            feedback = None
            
            # Check if arms aren't raised high enough
            if self.is_in_end_position and arm_spread < 120:
                feedback = "Raise your arms higher"
            
            # Check if legs aren't spread enough
            if self.is_in_end_position and leg_spread < 30:
                feedback = "Spread your legs wider"
            
            return feedback
        
        except Exception as e:
            print(f"Error counting jumping jacks: {e}")
            return None
            
    def _count_lunges(self, positions):
        """Count lunge repetitions and provide feedback."""
        try:
            # Calculate knee angles
            right_knee_angle = calculate_angle(
                positions.get("right_hip", [0, 0]), 
                positions.get("right_knee", [0, 0]), 
                positions.get("right_ankle", [0, 0])
            )
            
            left_knee_angle = calculate_angle(
                positions.get("left_hip", [0, 0]), 
                positions.get("left_knee", [0, 0]), 
                positions.get("left_ankle", [0, 0])
            )
            
            thresholds = self.thresholds["Lunges"]
            
            # Detect start position (standing straight)
            if not self.is_in_start_position and right_knee_angle > thresholds["front_knee_max"] - 20 and left_knee_angle > thresholds["back_knee_max"] - 20:
                self.is_in_start_position = True
                self.is_in_end_position = False
            
            # Detect end position (one knee bent for lunge)
            elif self.is_in_start_position and not self.is_in_end_position and (
                (right_knee_angle < thresholds["front_knee_min"] + 20 and left_knee_angle < thresholds["back_knee_min"] + 20) or
                (left_knee_angle < thresholds["front_knee_min"] + 20 and right_knee_angle < thresholds["back_knee_min"] + 20)):
                self.is_in_end_position = True
            
            # Count rep when returning to start from end
            elif self.is_in_start_position and self.is_in_end_position and right_knee_angle > thresholds["front_knee_max"] - 30 and left_knee_angle > thresholds["back_knee_max"] - 30:
                self.rep_count += 1
                self.is_in_start_position = True
                self.is_in_end_position = False
                self.last_rep_time = time.time()
            
            # Generate feedback based on form
            feedback = None
            
            # Check if front knee is aligned with ankle
            right_knee_x = positions.get("right_knee", [0, 0])[0]
            right_ankle_x = positions.get("right_ankle", [0, 0])[0]
            left_knee_x = positions.get("left_knee", [0, 0])[0]
            left_ankle_x = positions.get("left_ankle", [0, 0])[0]
            
            if right_knee_angle < 100 and abs(right_knee_x - right_ankle_x) > 0.1:
                feedback = "Keep your right knee aligned with your ankle"
            
            if left_knee_angle < 100 and abs(left_knee_x - left_ankle_x) > 0.1:
                feedback = "Keep your left knee aligned with your ankle"
            
            # Check if lunge is deep enough
            if self.is_in_end_position and min(right_knee_angle, left_knee_angle) > 100:
                feedback = "Lower your body more for a deeper lunge"
            
            return feedback
            
        except Exception as e:
            print(f"Error counting lunges: {e}")
            return None
            
    def _count_bicep_curls(self, positions):
        """Count bicep curl repetitions and provide feedback."""
        try:
            # Calculate elbow angles
            right_elbow_angle = calculate_angle(
                positions.get("right_shoulder", [0, 0]), 
                positions.get("right_elbow", [0, 0]), 
                positions.get("right_wrist", [0, 0])
            )
            
            left_elbow_angle = calculate_angle(
                positions.get("left_shoulder", [0, 0]), 
                positions.get("left_elbow", [0, 0]), 
                positions.get("left_wrist", [0, 0])
            )
            
            # Take minimum angle (either arm might be curling)
            elbow_angle = min(right_elbow_angle, left_elbow_angle)
            
            # Calculate shoulder angles (to detect swinging)
            right_shoulder_angle = calculate_angle(
                positions.get("right_hip", [0, 0]), 
                positions.get("right_shoulder", [0, 0]), 
                positions.get("right_elbow", [0, 0])
            )
            
            left_shoulder_angle = calculate_angle(
                positions.get("left_hip", [0, 0]), 
                positions.get("left_shoulder", [0, 0]), 
                positions.get("left_elbow", [0, 0])
            )
            
            thresholds = self.thresholds["Bicep Curls"]
            
            # Detect start position (arms extended)
            if not self.is_in_start_position and elbow_angle > thresholds["elbow_angle_max"] - 20:
                self.is_in_start_position = True
                self.is_in_end_position = False
            
            # Detect end position (arms bent)
            elif self.is_in_start_position and not self.is_in_end_position and elbow_angle < thresholds["elbow_angle_min"] + 10:
                self.is_in_end_position = True
            
            # Count rep when returning to start from end
            elif self.is_in_start_position and self.is_in_end_position and elbow_angle > thresholds["elbow_angle_max"] - 30:
                self.rep_count += 1
                self.is_in_start_position = True
                self.is_in_end_position = False
                self.last_rep_time = time.time()
            
            # Generate feedback based on form
            feedback = None
            
            # Check if shoulders are swinging (means using momentum)
            shoulder_angle = min(right_shoulder_angle, left_shoulder_angle)
            if shoulder_angle < 70:
                feedback = "Keep your upper arms still, avoid swinging"
            
            # Check if curls are complete
            if self.is_in_end_position and elbow_angle > 70:
                feedback = "Try to curl all the way up"
            
            return feedback
            
        except Exception as e:
            print(f"Error counting bicep curls: {e}")
            return None
    
    def suggest_next_exercise(self, current_exercise):
        """
        Suggest the next exercise based on the current one.
        
        Args:
            current_exercise (str): Current exercise type
            
        Returns:
            str: Suggested next exercise
        """
        exercise_progression = {
            "Squats": "Lunges",
            "Lunges": "Push-ups",
            "Push-ups": "Bicep Curls",
            "Bicep Curls": "Jumping Jacks",
            "Jumping Jacks": "Squats"
        }
        
        # Default to squats if current exercise not in progression
        return exercise_progression.get(current_exercise, "Squats")