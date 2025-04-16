//
//  CameraWindow.swift
//  HandKeyboard
//
//  Created on 4/13/25.
//

import SwiftUI
import AVFoundation

// Window to display camera feed and hand tracking for debugging
struct CameraWindow: View {
    var handTracker: HandTracker
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Text("Camera Feed - Debug Window")
                    .font(.headline)
                
                Spacer()
                
                // Camera selector - simplified
                Picker("", selection: Binding(
                    get: { 
                        // Current camera ID or empty string if none
                        handTracker.selectedCamera?.uniqueID ?? "" 
                    },
                    set: { newID in
                        // Find and switch to the selected camera
                        if let camera = handTracker.availableCameras.first(where: { $0.uniqueID == newID }) {
                            handTracker.switchCamera(to: camera)
                        }
                    }
                )) {
                    // Create picker items for each camera
                    ForEach(handTracker.availableCameras, id: \.uniqueID) { camera in
                        Text(camera.localizedName).tag(camera.uniqueID)
                    }
                }
                .frame(width: 160)
                
                // Refresh cameras button
                Button(action: { handTracker.findAvailableCameras() }) {
                    Image(systemName: "arrow.triangle.2.circlepath")
                }
                .buttonStyle(.borderless)
                
                // Close button
                Button(action: {
                    appState.isCameraWindowOpen = false
                }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.red)
                }
                .buttonStyle(.borderless)
            }
            .padding([.horizontal, .top], 8)
            
            // Combined view with camera and hand landmarks overlay
            ZStack {
                // Live camera feed
                CameraPreviewView(session: handTracker.captureSession)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                
                // Hand landmark visualization overlay
                HandVisualizationView(
                    leftHandLandmarks: handTracker.leftHandLandmarks,
                    rightHandLandmarks: handTracker.rightHandLandmarks
                )
                .allowsHitTesting(false)
            }
            
            // Debug information and controls
            VStack(spacing: 4) {
                // Current gesture info
                HStack(spacing: 8) {
                    // Left hand
                    HStack {
                        Circle()
                            .fill(handTracker.leftHandDetected ? Color.green : Color.gray)
                            .frame(width: 8, height: 8)
                        
                        Text("Left: \(handTracker.leftHandKey) (\(handTracker.leftHandGesture.rawValue))")
                            .font(.caption)
                    }
                    
                    Spacer()
                    
                    // Right hand
                    HStack {
                        Text("Right: \(handTracker.rightHandKey) (\(handTracker.rightHandGesture.rawValue))")
                            .font(.caption)
                        
                        Circle()
                            .fill(handTracker.rightHandDetected ? Color.blue : Color.gray)
                            .frame(width: 8, height: 8)
                    }
                }
                .padding(.horizontal, 8)
                .padding(.top, 6)
                
                // Camera dimensions and processing info
                Text("Camera: \(handTracker.selectedCamera?.localizedName ?? "None") (\(Int(handTracker.videoDimensions.width))×\(Int(handTracker.videoDimensions.height)))")
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, alignment: .center)
                    .padding(.bottom, 4)
            }
            .background(Color.black.opacity(0.1))
        }
    }
}