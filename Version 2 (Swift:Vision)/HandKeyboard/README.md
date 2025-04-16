# HandKeyboard

A macOS application that uses the Vision framework to detect hand gestures and map them to keyboard inputs.

## Features

- Uses the macOS camera to capture video
- Processes video using Vision framework's hand pose detection
- Recognizes finger pinch combinations (thumb to other fingers)
- Maps each pinch gesture to a specific keystroke:
  - Thumb-Index: Space
  - Thumb-Middle: Enter
  - Thumb-Ring: Delete
  - Thumb-Pinky: Escape
- Displays visual feedback of detected hand landmarks
- Shows the currently detected gesture and mapped key

## Requirements

- macOS 11.0+
- Xcode 14.0+
- Swift 5.5+
- Mac with camera

## Usage

1. Launch the application
2. Grant camera permission when prompted
3. Position your hand in front of the camera
4. Perform pinch gestures to trigger keystrokes

## Project Structure

The app follows MVVM architecture with clear separation of concerns:

### Models
- `Gesture.swift`: Defines hand gesture types and configuration
- `HandLandmark.swift`: Represents hand landmark points
- `KeyMapping.swift`: Maps gestures to keyboard actions

### Services
- `CameraService.swift`: Manages camera setup and frame capture
- `VisionService.swift`: Handles computer vision processing
- `GestureRecognitionService.swift`: Detects gestures from hand landmarks
- `KeyboardService.swift`: Simulates keyboard inputs
- `PermissionsService.swift`: Manages system permissions

### ViewModels
- `HandTrackingViewModel.swift`: Coordinates between services and UI

### Views
- `MainView.swift`: Primary container view
- `CameraPreviewView.swift`: Shows camera feed
- `HandLandmarkView.swift`: Visualizes hand points
- `GestureStatusView.swift`: Shows gesture and key information
- `CameraSettingsView.swift`: Manages camera selection
- `PermissionView.swift`: Handles permission UI

### Utils
- `AppConfig.swift`: Global configuration and constants

## Adding More Gestures

To add more gestures, modify the `HandGesture` enum in `Gesture.swift` and update the mapping in `KeyMapping.swift`.

## Implementation Details

The app is built using:
- SwiftUI for the user interface
- AVFoundation for camera access
- Vision framework for hand pose detection
- Carbon framework for triggering keyboard events