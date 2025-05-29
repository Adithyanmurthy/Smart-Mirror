import cv2
import mediapipe as mp
import numpy as np

class PoseDetector:
    """Class for detecting and tracking body pose landmarks using MediaPipe."""
    
    def __init__(self, static_mode=False, model_complexity=1, smooth_landmarks=True, 
                 min_detection_confidence=0.5, min_tracking_confidence=0.5):
        """
        Initialize the pose detector with MediaPipe.
        
        Args:
            static_mode (bool): Whether to treat frames as static images or video.
            model_complexity (int): Model complexity (0=Lite, 1=Full, 2=Heavy).
            smooth_landmarks (bool): Whether to filter landmarks to reduce jitter.
            min_detection_confidence (float): Minimum confidence for detection.
            min_tracking_confidence (float): Minimum confidence for tracking.
        """
        self.static_mode = static_mode
        self.model_complexity = model_complexity
        self.smooth_landmarks = smooth_landmarks
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        
        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self._init_pose()
        
        # Drawing utilities
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
    
    def _init_pose(self):
        """
        Initialize the MediaPipe pose processor with error handling.
        
        Returns:
            MediaPipe pose processor
        """
        try:
            return self.mp_pose.Pose(
                static_image_mode=self.static_mode,
                model_complexity=self.model_complexity,
                smooth_landmarks=self.smooth_landmarks,
                min_detection_confidence=self.min_detection_confidence,
                min_tracking_confidence=self.min_tracking_confidence
            )
        except Exception as e:
            print(f"Error initializing MediaPipe Pose: {e}")
            # Fallback to simpler model if initialization fails
            return self.mp_pose.Pose(
                static_image_mode=self.static_mode,
                model_complexity=0,  # Lite model as fallback
                smooth_landmarks=self.smooth_landmarks,
                min_detection_confidence=0.3,
                min_tracking_confidence=0.3
            )
    
    def detect_pose(self, frame):
        """
        Detect pose landmarks in a frame with error handling.
        
        Args:
            frame (numpy.ndarray): BGR image/frame
            
        Returns:
            tuple: (processed frame with landmarks drawn, landmarks if detected or None)
        """
        if frame is None:
            return None, None
        
        try:
            # Create a copy of the frame to avoid modifying the original
            img = frame.copy()
            
            # Convert BGR to RGB (MediaPipe requires RGB input)
            rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Process the frame to find pose landmarks
            results = self.pose.process(rgb_frame)
            
            # If landmarks detected, draw them on the frame and extract coordinates
            if results.pose_landmarks:
                # Draw pose landmarks
                self.mp_drawing.draw_landmarks(
                    img,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                )
                
                # Convert landmarks to numpy array for easier processing
                landmarks = []
                for landmark in results.pose_landmarks.landmark:
                    # Append (x, y, z, visibility) for each landmark
                    landmarks.append([
                        landmark.x, 
                        landmark.y, 
                        landmark.z, 
                        landmark.visibility
                    ])
                
                return img, np.array(landmarks)
            
            # Return the frame and None if no landmarks detected
            return img, None
        
        except Exception as e:
            print(f"Error in pose detection: {e}")
            # Return original frame if processing fails
            return frame, None
    
    def get_landmark_coordinates(self, landmarks, idx, frame_width, frame_height):
        """
        Get the pixel coordinates of a specific landmark.
        
        Args:
            landmarks (numpy.ndarray): Array of landmarks
            idx (int): Index of the landmark to get
            frame_width (int): Width of the frame
            frame_height (int): Height of the frame
            
        Returns:
            tuple: (x, y) coordinates in pixels or None if invalid
        """
        try:
            if landmarks is not None and 0 <= idx < len(landmarks):
                x = int(landmarks[idx][0] * frame_width)
                y = int(landmarks[idx][1] * frame_height)
                return (x, y)
        except (IndexError, TypeError) as e:
            print(f"Error getting landmark coordinates: {e}")
        
        return None
    
    def get_visibility(self, landmarks, idx):
        """
        Get the visibility score of a specific landmark.
        
        Args:
            landmarks (numpy.ndarray): Array of landmarks
            idx (int): Index of the landmark to check
            
        Returns:
            float: Visibility score (0-1) or 0 if no landmarks or error
        """
        try:
            if landmarks is not None and 0 <= idx < len(landmarks):
                return landmarks[idx][3]
        except (IndexError, TypeError) as e:
            print(f"Error getting landmark visibility: {e}")
        
        return 0