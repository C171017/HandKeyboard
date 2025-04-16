//
//  HandGestureTracker.swift
//  HandKeyboard
//
//  Created on 4/12/25.
//

import Foundation
import Vision
import AVFoundation
import Combine

// Main class for hand tracking and gesture recognition
class HandGestureTracker: NSObject, ObservableObject {
    // State properties
    @Published var leftHandDetected: Bool = false
    @Published var rightHandDetected: Bool = false
    @Published var leftHandGesture: HandGesture = .none
    @Published var rightHandGesture: HandGesture = .none
    @Published var leftHandKey: String = "None"
    @Published var rightHandKey: String = "None"
    
    // Camera selection
    @Published var availableCameras: [AVCaptureDevice] = []
    @Published var selectedCamera: AVCaptureDevice?
    @Published var isRunning: Bool = false
    
    // Key mapping for both hands
    private let leftHandKeyMapping: [HandGesture: String] = [
        .thumbIndex: "a",
        .thumbMiddle: "b",
        .thumbRing: "c",
        .thumbPinky: "d"
    ]
    
    private let rightHandKeyMapping: [HandGesture: String] = [
        .thumbIndex: "e",
        .thumbMiddle: "f",
        .thumbRing: "g",
        .thumbPinky: "h"
    ]
    
    // Camera handling
    let captureSession = AVCaptureSession()
    private var videoOutput = AVCaptureVideoDataOutput()
    
    // Vision request - setting to 2 hands for dual hand tracking
    private let handPoseRequest = VNDetectHumanHandPoseRequest()
    
    // Processing queue
    private let videoProcessingQueue = DispatchQueue(label: "VideoProcessingQueue")
    
    override init() {
        super.init()
        // Set to 2 hands to detect both left and right hands
        handPoseRequest.maximumHandCount = 2
        
        // Ensure we run camera discovery on the main thread
        DispatchQueue.main.async {
            self.findAvailableCameras()
        }
    }
    
    // Find all available cameras - simplified for better iPhone continuity camera support
    func findAvailableCameras() {
        // Include built-in cameras and iPhone Continuity Camera
        let deviceTypes: [AVCaptureDevice.DeviceType] = [
            .builtInWideAngleCamera,
            .continuityCamera,  // iPhone camera
            .external           // Other external cameras
        ]
        
        // Create discovery session
        let discoverySession = AVCaptureDevice.DiscoverySession(
            deviceTypes: deviceTypes,
            mediaType: .video,
            position: .unspecified
        )
        
        // Get and update available cameras
        let cameras = discoverySession.devices
        print("Found \(cameras.count) cameras: \(cameras.map { $0.localizedName }.joined(separator: ", "))")
        
        DispatchQueue.main.async {
            self.availableCameras = cameras
            
            // Select default camera if none selected
            if self.selectedCamera == nil, let defaultCamera = self.availableCameras.first {
                print("Selected default camera: \(defaultCamera.localizedName)")
                self.selectedCamera = defaultCamera
                self.setupCaptureSession()
                
                // Automatically start capture if this is initial setup
                if !self.isRunning && !self.captureSession.isRunning {
                    self.startCapture()
                }
            } else {
                print("No camera selected or no cameras available")
            }
        }
    }
    
    // Switch to a different camera - simplified and with better error handling
    func switchCamera(to camera: AVCaptureDevice) {
        print("Switching to camera: \(camera.localizedName)")
        
        // Stop the current session completely
        let wasRunning = isRunning
        if isRunning {
            captureSession.stopRunning()
            DispatchQueue.main.async {
                self.isRunning = false
            }
        }
        
        // Update selected camera
        DispatchQueue.main.async {
            self.selectedCamera = camera
        }
        
        // Set up with new camera
        setupCaptureSession()
        
        // Restart if needed
        if wasRunning {
            DispatchQueue.global(qos: .userInitiated).async {
                self.captureSession.startRunning()
                
                DispatchQueue.main.async {
                    self.isRunning = true
                    print("Camera started: \(camera.localizedName)")
                }
            }
        }
    }
    
    // Setup camera session with better error handling
    private func setupCaptureSession() {
        // Stop any running session
        if captureSession.isRunning {
            captureSession.stopRunning()
            DispatchQueue.main.async {
                self.isRunning = false
            }
        }
        
        // Reset and reconfigure
        captureSession.beginConfiguration()
        
        // Clear existing setup
        captureSession.inputs.forEach { captureSession.removeInput($0) }
        captureSession.outputs.forEach { captureSession.removeOutput($0) }
        
        // Set up with new camera
        guard let camera = selectedCamera else {
            print("Error: No camera selected")
            captureSession.commitConfiguration()
            return
        }
        
        print("Setting up camera: \(camera.localizedName)")
        
        do {
            // Add camera input
            let videoInput = try AVCaptureDeviceInput(device: camera)
            if captureSession.canAddInput(videoInput) {
                captureSession.addInput(videoInput)
            } else {
                print("Error: Cannot add camera input for \(camera.localizedName)")
                captureSession.commitConfiguration()
                return
            }
            
            // Add video output
            videoOutput.setSampleBufferDelegate(self, queue: videoProcessingQueue)
            if captureSession.canAddOutput(videoOutput) {
                captureSession.addOutput(videoOutput)
            }
            
            // Try to optimize camera settings - with careful error handling
            do {
                try camera.lockForConfiguration()
                
                // Check each camera capability before attempting to use it
                print("Camera capabilities:")
                print("- Auto exposure supported: \(camera.isExposureModeSupported(.continuousAutoExposure))")
                print("- Auto white balance supported: \(camera.isWhiteBalanceModeSupported(.continuousAutoWhiteBalance))")
                
                // Only try to set modes that are supported
                if camera.isExposureModeSupported(.continuousAutoExposure) {
                    camera.exposureMode = .continuousAutoExposure
                }
                
                if camera.isWhiteBalanceModeSupported(.continuousAutoWhiteBalance) {
                    camera.whiteBalanceMode = .continuousAutoWhiteBalance
                }
                
                camera.unlockForConfiguration()
            } catch {
                print("Warning: Could not configure camera settings: \(error.localizedDescription)")
                // Continue without camera configuration - basic functionality will still work
            }
            
            print("Camera setup complete: \(camera.localizedName)")
            
        } catch {
            print("Error setting up camera: \(error.localizedDescription)")
        }
        
        // Finish configuration
        captureSession.commitConfiguration()
    }
    
    // Start camera capture
    func startCapture() {
        // Prevent configuration conflicts
        guard !captureSession.isRunning else { return }
        
        DispatchQueue.global().async { [weak self] in
            self?.captureSession.startRunning()
            print("Hand gesture tracking started")
            
            DispatchQueue.main.async {
                self?.isRunning = true
            }
        }
    }
    
    // Stop camera capture
    func stopCapture() {
        // Prevent configuration conflicts
        guard captureSession.isRunning else { return }
        
        DispatchQueue.global().async { [weak self] in
            self?.captureSession.stopRunning()
            print("Hand gesture tracking stopped")
            
            DispatchQueue.main.async {
                self?.isRunning = false
            }
        }
    }
    
    // Process video frame
    private func processVideoFrame(_ sampleBuffer: CMSampleBuffer) {
        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        
        let handler = VNImageRequestHandler(cvPixelBuffer: pixelBuffer, options: [:])
        
        do {
            try handler.perform([handPoseRequest])
            processHandPoseResults()
        } catch {
            print("Hand detection error: \(error)")
        }
    }
    
    // Process hand detection results
    private func processHandPoseResults() {
        // Clear landmarks if no hands detected
        guard let results = handPoseRequest.results, !results.isEmpty else {
            DispatchQueue.main.async {
                // Reset all state if no hands detected
                self.leftHandDetected = false
                self.rightHandDetected = false
                self.leftHandGesture = .none
                self.leftHandKey = "None"
                self.rightHandGesture = .none
                self.rightHandKey = "None"
            }
            return
        }
        
        var leftHandFound = false
        var rightHandFound = false
        
        // Process each detected hand
        for observation in results {
            let handType = determineHandType(from: observation)
            
            if handType == .left {
                leftHandFound = true
                detectGesturesForHand(observation, isLeftHand: true)
            } else if handType == .right {
                rightHandFound = true
                detectGesturesForHand(observation, isLeftHand: false)
            }
        }
        
        // Update state on main thread
        DispatchQueue.main.async {
            // Update hand detection status
            self.leftHandDetected = leftHandFound
            self.rightHandDetected = rightHandFound
            
            // If hands aren't found, reset their state
            if !leftHandFound {
                self.leftHandGesture = .none
                self.leftHandKey = "None"
            }
            
            if !rightHandFound {
                self.rightHandGesture = .none
                self.rightHandKey = "None"
            }
        }
    }
    
    // Determine if this is a left or right hand
    private enum HandSide {
        case left
        case right
        case unknown
    }
    
    private func determineHandType(from observation: VNHumanHandPoseObservation) -> HandSide {
        guard let wrist = try? observation.recognizedPoint(.wrist),
              let thumbCMC = try? observation.recognizedPoint(.thumbCMC),
              let indexMCP = try? observation.recognizedPoint(.indexMCP),
              wrist.confidence > 0.5, thumbCMC.confidence > 0.5, indexMCP.confidence > 0.5 else {
            return .unknown
        }
        
        // Get vectors for cross product calculation
        let wristToIndex = CGPoint(
            x: indexMCP.location.x - wrist.location.x,
            y: indexMCP.location.y - wrist.location.y
        )
        
        let wristToThumb = CGPoint(
            x: thumbCMC.location.x - wrist.location.x,
            y: thumbCMC.location.y - wrist.location.y
        )
        
        // Cross product to determine chirality
        // If the z component is positive, thumb is to the right of fingers (left hand)
        // If the z component is negative, thumb is to the left of fingers (right hand)
        let crossProductZ = wristToIndex.x * wristToThumb.y - wristToIndex.y * wristToThumb.x
        
        return crossProductZ > 0 ? .left : .right
    }
    
    // Detect pinch gestures for a specific hand
    private func detectGesturesForHand(_ observation: VNHumanHandPoseObservation, isLeftHand: Bool) {
        guard let thumbTip = try? observation.recognizedPoint(.thumbTip),
              thumbTip.confidence > 0.3 else {
            return
        }
        
        var gestureDetected = false
        let pinchThreshold = GestureConfig.pinchThreshold
        var currentGesture: HandGesture = .none
        
        // Check each finger for pinch
        if let indexTip = try? observation.recognizedPoint(.indexTip), indexTip.confidence > 0.3 {
            let dist = distance(from: thumbTip.location, to: indexTip.location)
            
            if dist < pinchThreshold && !gestureDetected {
                gestureDetected = true
                currentGesture = .thumbIndex
            }
        }
        
        if let middleTip = try? observation.recognizedPoint(.middleTip), middleTip.confidence > 0.3 {
            let dist = distance(from: thumbTip.location, to: middleTip.location)
            
            if dist < pinchThreshold && !gestureDetected {
                gestureDetected = true
                currentGesture = .thumbMiddle
            }
        }
        
        if let ringTip = try? observation.recognizedPoint(.ringTip), ringTip.confidence > 0.3 {
            let dist = distance(from: thumbTip.location, to: ringTip.location)
            
            if dist < pinchThreshold && !gestureDetected {
                gestureDetected = true
                currentGesture = .thumbRing
            }
        }
        
        if let pinkyTip = try? observation.recognizedPoint(.littleTip), pinkyTip.confidence > 0.3 {
            let dist = distance(from: thumbTip.location, to: pinkyTip.location)
            
            if dist < pinchThreshold && !gestureDetected {
                gestureDetected = true
                currentGesture = .thumbPinky
            }
        }
        
        // Process detected gesture on main thread
        DispatchQueue.main.async {
            if isLeftHand {
                // Only trigger a key if the gesture has changed
                if currentGesture != self.leftHandGesture {
                    if currentGesture != .none {
                        let keyName = self.leftHandKeyMapping[currentGesture] ?? "None"
                        // Only simulate keypress if we have a valid key mapping
                        if keyName != "None" {
                            self.simulateKeypress(for: keyName, isLeftHand: true)
                        }
                        self.leftHandGesture = currentGesture
                        self.leftHandKey = keyName
                    } else if !gestureDetected && self.leftHandGesture != .none {
                        self.leftHandGesture = .none
                        self.leftHandKey = "None"
                    }
                }
            } else {
                // Only trigger a key if the gesture has changed
                if currentGesture != self.rightHandGesture {
                    if currentGesture != .none {
                        let keyName = self.rightHandKeyMapping[currentGesture] ?? "None"
                        // Only simulate keypress if we have a valid key mapping
                        if keyName != "None" {
                            self.simulateKeypress(for: keyName, isLeftHand: false)
                        }
                        self.rightHandGesture = currentGesture
                        self.rightHandKey = keyName
                    } else if !gestureDetected && self.rightHandGesture != .none {
                        self.rightHandGesture = .none
                        self.rightHandKey = "None"
                    }
                }
            }
        }
    }
    
    // Calculate distance between points
    private func distance(from point1: CGPoint, to point2: CGPoint) -> CGFloat {
        return point1.distance(to: point2)
    }
    
    // Simulate key press
    private func simulateKeypress(for key: String, isLeftHand: Bool) {
        print("Key pressed: \(key) (from \(isLeftHand ? "left" : "right") hand)")
        KeySimulator.simulateKeyPress(for: key)
    }
}

// Camera delegate
extension HandGestureTracker: AVCaptureVideoDataOutputSampleBufferDelegate {
    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        processVideoFrame(sampleBuffer)
    }
}