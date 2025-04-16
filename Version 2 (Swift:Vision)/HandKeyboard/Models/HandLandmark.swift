//
//  HandLandmark.swift
//  HandKeyboard
//
//  Created on 4/13/25.
//

import Foundation
import Vision

/// Represents hand chirality (left or right hand)
enum HandType: String {
    case left = "Left"
    case right = "Right"
    case unknown = "Unknown"
}

/// Represents a single hand landmark point with position and confidence
struct HandLandmark {
    let position: CGPoint
    let confidence: Float
    
    /// Creates an invalid/empty landmark
    static func empty() -> HandLandmark {
        return HandLandmark(position: CGPoint.zero, confidence: 0)
    }
    
    /// Indicates if this is a valid landmark with sufficient confidence
    var isValid: Bool {
        return confidence >= GestureConfig.confidenceThreshold && 
               !(position.x.isZero && position.y.isZero)
    }
}

/// Collection of landmarks forming a complete hand
struct HandLandmarks {
    let points: [HandLandmark]
    let handType: HandType
    
    init(points: [HandLandmark] = [], handType: HandType = .unknown) {
        self.points = points
        self.handType = handType
    }
    
    /// Creates empty landmarks collection with placeholders
    static func empty() -> HandLandmarks {
        return HandLandmarks(
            points: Array(repeating: HandLandmark.empty(), count: 21),
            handType: .unknown
        )
    }
    
    /// Get the raw points for drawing
    var drawPoints: [CGPoint] {
        return points.map { $0.position }
    }
    
    /// Landmark indices for common hand points
    struct Index {
        static let wrist = 0
        
        // Thumb points
        static let thumbCMC = 1
        static let thumbMP = 2
        static let thumbIP = 3
        static let thumbTip = 4
        
        // Index finger points
        static let indexMCP = 5
        static let indexPIP = 6
        static let indexDIP = 7
        static let indexTip = 8
        
        // Middle finger points
        static let middleMCP = 9
        static let middlePIP = 10
        static let middleDIP = 11
        static let middleTip = 12
        
        // Ring finger points
        static let ringMCP = 13
        static let ringPIP = 14
        static let ringDIP = 15
        static let ringTip = 16
        
        // Pinky finger points
        static let pinkyMCP = 17
        static let pinkyPIP = 18
        static let pinkyDIP = 19
        static let pinkyTip = 20
    }
}