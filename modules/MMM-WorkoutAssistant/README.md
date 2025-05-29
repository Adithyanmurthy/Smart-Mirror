# Smart Mirror Workout Assistant

A computer vision-powered workout assistant that helps users track exercises, count repetitions, and improve form in real-time.

## Features

- **Real-Time Pose Detection**: Uses MediaPipe to track full-body landmarks
- **Exercise Recognition**: Automatically identifies common exercises (squats, push-ups, etc.)
- **Rep Counting**: Tracks and counts exercise repetitions
- **Form Feedback**: Provides real-time guidance on improving exercise form
- **Visual Overlay**: Shows skeleton tracking and feedback directly on video
- **Exercise Suggestions**: Recommends new exercises based on user performance

## Project Structure

```
smart_mirror/
├── app.py                    # Streamlit web application
├── pose_detection.py         # Body landmark detection with MediaPipe
├── exercise_predictor.py     # Movement analysis and exercise classification
├── utils.py                  # Helper functions for angle calculation and feedback
├── requirements.txt          # Required Python packages
└── README.md                 # This file
```

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/smart-mirror.git
   cd smart-mirror
   ```

2. Create a virtual environment (recommended):

   ```
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:

   ```
   streamlit run app.py
   ```

2. Allow camera access when prompted by your browser.

3. Position yourself so your full body is visible to the camera.

4. Start exercising! The system will automatically:
   - Detect your body pose
   - Identify the exercise you're performing
   - Count repetitions
   - Provide form feedback

## Troubleshooting Camera Issues

If you encounter camera access problems:

1. **Camera Permissions**: Ensure your browser has permission to access your camera.

2. **Multiple Cameras**: If you have multiple cameras, the app will detect them and let you select which one to use.

3. **Camera Selection**: If a selected camera fails to open, the app will automatically fall back to the default camera (camera 0).

4. **Camera Not Found**: If no camera is found, check your connections and ensure your camera is not being used by another application.

5. **Reconnecting**: If the camera connection is lost during usage, the app will attempt to reconnect automatically.

6. **Browser Support**: For best results, use a modern browser like Chrome, Firefox, or Edge.

## Supported Exercises

- Squats
- Push-ups
- Jumping Jacks
- Lunges
- Bicep Curls

## Form Feedback

The system provides real-time feedback on your exercise form, including:

- **Squats**: Knee alignment, squat depth, back posture
- **Push-ups**: Arm position, body alignment, depth
- **Jumping Jacks**: Arm and leg extension
- **Lunges**: Knee alignment, depth
- **Bicep Curls**: Arm position, range of motion

## Requirements

- Python 3.8+
- Webcam/camera
- Sufficient lighting for pose detection
- Enough space to perform exercises with full body visibility

## Hardware Recommendations

- **Minimum**: Any computer with a webcam and Python support
- **Recommended**: Raspberry Pi 4 (4GB+) with camera module or USB webcam
- **Display**: Any monitor/display for the "mirror" interface

## Performance Notes

- For better performance on Raspberry Pi, you may need to reduce the camera resolution
- CPU usage can be high due to real-time pose estimation
- Ensure good lighting for better pose detection accuracy

## Future Improvements

- Add user profiles and progress tracking
- Implement workout routines and guided sessions
- Add more exercise types and advanced form analysis
- Improve UI with customizable themes

## License

MIT License - See LICENSE file for details.

## Credits

This project uses:

- [MediaPipe](https://google.github.io/mediapipe/) for pose estimation
- [Streamlit](https://streamlit.io/) for the web interface
- [OpenCV](https://opencv.org/) for image processing
