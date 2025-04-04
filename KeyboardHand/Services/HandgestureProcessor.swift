//
//  HandgestureProcessor.swift
//  KeyboardHand
//
//  Created by C171017 on 4/3/25.
//

// Services/HandGestureProcessor.swift
import Vision
import CoreImage

class HandGestureProcessor {
    private let handPoseRequest = VNDetectHumanHandPoseRequest()
    private let keyboardController = KeyboardController()
    private var previousGesture: HandGesture?
    
    init() {
        handPoseRequest.maximumHandCount = 2
    }
    
    func processFrame(pixelBuffer: CVPixelBuffer) {
        let handler = VNImageRequestHandler(cvPixelBuffer: pixelBuffer, options: [:])
        
        do {
            try handler.perform([handPoseRequest])
            processHandPoseResults()
        } catch {
            print("Failed to perform hand pose detection: \(error)")
        }
    }
    
    private func processHandPoseResults() {
        guard let observations = handPoseRequest.results else { return }
        
        for observation in observations {
            let handGesture = detectGesture(from: observation)
            
            // Only trigger input if gesture is different from previous one
            if let gesture = handGesture, gesture != previousGesture {
                keyboardController.executeKeyboardCommand(for: gesture)
                previousGesture = gesture
            }
        }
    }
    
    private func detectGesture(from observation: VNHumanHandPoseObservation) -> HandGesture? {
        // Determine if it's left or right hand based on thumb position
        let handedness: HandGesture.Handedness
        
        if let thumbTip = try? observation.recognizedPoint(.thumbTip) {
            handedness = thumbTip.x < 0.5 ? .left : .right
        } else {
            return nil
        }
        
        // Detect which finger is pinching with thumb
        var pinchingFinger: HandGesture.PinchingFinger?
        
        if let thumbTip = try? observation.recognizedPoint(.thumbTip),
           let indexTip = try? observation.recognizedPoint(.indexTip) {
            let distance = distance(thumbTip, indexTip)
            if distance < 0.05 && indexTip.confidence > 0.9 && thumbTip.confidence > 0.9 {
                pinchingFinger = .index
            }
        }
        
        if pinchingFinger == nil,
           let thumbTip = try? observation.recognizedPoint(.thumbTip),
           let middleTip = try? observation.recognizedPoint(.middleTip) {
            let distance = distance(thumbTip, middleTip)
            if distance < 0.05 && middleTip.confidence > 0.9 && thumbTip.confidence > 0.9 {
                pinchingFinger = .middle
            }
        }
        
        if pinchingFinger == nil,
           let thumbTip = try? observation.recognizedPoint(.thumbTip),
           let ringTip = try? observation.recognizedPoint(.ringTip) {
            let distance = distance(thumbTip, ringTip)
            if distance < 0.05 && ringTip.confidence > 0.9 && thumbTip.confidence > 0.9 {
                pinchingFinger = .ring
            }
        }
        
        if pinchingFinger == nil,
           let thumbTip = try? observation.recognizedPoint(.thumbTip),
           let littleTip = try? observation.recognizedPoint(.littleTip) {
            let distance = distance(thumbTip, littleTip)
            if distance < 0.05 && littleTip.confidence > 0.9 && thumbTip.confidence > 0.9 {
                pinchingFinger = .little
            }
        }
        
        guard let pinchingFinger = pinchingFinger else {
            return nil // No pinch detected
        }
        
        // Detect palm orientation
        let palmOrientation = detectPalmOrientation(from: observation)
        
        return HandGesture(handedness: handedness, pinchingFinger: pinchingFinger, palmOrientation: palmOrientation)
    }
    
    private func detectPalmOrientation(from observation: VNHumanHandPoseObservation) -> HandGesture.PalmOrientation {
        guard let wrist = try? observation.recognizedPoint(.wrist),
              let middleMCP = try? observation.recognizedPoint(.middleMCP) else {
            return .unknown
        }
        
        // If wrist is higher than middle finger MCP, palm is facing down
        if wrist.y - middleMCP.y > 0.1 {
            return .down
        }
        
        // If middle finger MCP is higher than wrist, palm is facing up
        if middleMCP.y - wrist.y > 0.1 {
            return .up
        }
        
        // Otherwise, assume the palm is facing each other (sideways)
        return .facingEachOther
    }
    
    private func distance(_ a: VNRecognizedPoint, _ b: VNRecognizedPoint) -> CGFloat {
        return sqrt(pow(a.x - b.x, 2) + pow(a.y - b.y, 2))
    }
}
