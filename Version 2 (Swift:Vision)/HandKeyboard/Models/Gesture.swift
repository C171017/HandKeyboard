//
//  Gesture.swift
//  HandKeyboard
//
//  Created on 4/13/25.
//

import Foundation

/// Defines all supported hand gestures
enum HandGesture: String {
    case none = "None"              // No gesture detected
    case thumbIndex = "ThumbIndex"  // Thumb touching index finger
    case thumbMiddle = "ThumbMiddle" // Thumb touching middle finger
    case thumbRing = "ThumbRing"     // Thumb touching ring finger
    case thumbPinky = "ThumbPinky"   // Thumb touching pinky finger
}

/// Configuration for gesture detection
struct GestureConfig {
    /// Distance threshold for pinch detection - smaller values require closer finger proximity
    static let pinchThreshold: CGFloat = 0.01
    
    /// Confidence threshold for landmark detection
    static let confidenceThreshold: Float = 0.5
}
