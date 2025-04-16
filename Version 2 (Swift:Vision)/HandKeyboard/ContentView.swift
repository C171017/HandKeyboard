//
//  ContentView.swift
//  HandKeyboard
//
//  Created by C171017 on 4/12/25.
//

import SwiftUI
import AVFoundation

struct ContentView: View {
    @ObservedObject private var handTracker: HandTracker
    @EnvironmentObject private var appState: AppState
    
    init(handTracker: HandTracker) {
        self.handTracker = handTracker
    }
    
    var body: some View {
        VStack(spacing: 12) {
            // Minimal camera controls
            HStack {
                Button(action: { 
                    if handTracker.isRunning {
                        handTracker.stopCapture()
                    } else {
                        handTracker.startCapture()
                    }
                }) {
                    Label(
                        handTracker.isRunning ? "Stop Camera" : "Start Camera",
                        systemImage: handTracker.isRunning ? "stop.fill" : "play.fill"
                    )
                    .foregroundColor(handTracker.isRunning ? .red : .green)
                }
                
                Spacer()
                
                // Camera window toggle
                Button(action: {
                    // Simply toggle the state - WindowManager will handle the actual window
                    print("Button clicked - current state: \(
appState.isCameraWindowOpen)")
                    appState.isCameraWindowOpen.toggle()
                    print("Button clicked - new state: \(appState.isCameraWindowOpen)")
                    
                    // Force the window manager to act
                    if appState.isCameraWindowOpen {
                        appState.windowManager.openDebugWindowIfNeeded()
                    } else {
                        appState.windowManager.closeDebugWindow()
                    }
                }) {
                    Label(
                        appState.isCameraWindowOpen ? "Hide Camera Window" : "Show Camera Window",
                        systemImage: "rectangle.on.rectangle"
                    )
                    .foregroundColor(appState.isCameraWindowOpen ? .blue : .primary)
                }
            }
            .padding(.horizontal, 4)
            
            // Main visualization view with camera aspect ratio
            HandVisualizationView(
                leftHandLandmarks: handTracker.leftHandLandmarks,
                rightHandLandmarks: handTracker.rightHandLandmarks
            )
            .aspectRatio(
                CGSize(
                    width: handTracker.videoDimensions.width,
                    height: handTracker.videoDimensions.height
                ),
                contentMode: .fit
            )
            .background(Color.black.opacity(0.1))
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(Color.gray.opacity(0.2), lineWidth: 1)
            )
            .overlay(
                Group {
                    if !handTracker.isRunning {
                        VStack {
                            Image(systemName: "video.slash")
                                .font(.system(size: 30))
                                .foregroundColor(.gray)
                            Text("Camera Off")
                                .font(.headline)
                                .foregroundColor(.gray)
                                .padding(.top, 4)
                        }
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                        .background(Color.black.opacity(0.3))
                    }
                }
            )
            
            // Status bar showing hand detection and keystrokes
            HStack {
                // Left hand status
                HandStatusIndicator(
                    isDetected: handTracker.leftHandDetected,
                    gesture: handTracker.leftHandGesture,
                    keyPressed: handTracker.leftHandKey,
                    isLeftHand: true
                )
                
                Spacer()
                
                // Right hand status
                HandStatusIndicator(
                    isDetected: handTracker.rightHandDetected,
                    gesture: handTracker.rightHandGesture,
                    keyPressed: handTracker.rightHandKey,
                    isLeftHand: false
                )
            }
            .padding(8)
            .background(Color.gray.opacity(0.05))
            .cornerRadius(8)
            .frame(height: 30)
        }
        .padding()
    }
}

// Hand status indicator for status bar
struct HandStatusIndicator: View {
    var isDetected: Bool
    var gesture: HandGesture
    var keyPressed: String
    var isLeftHand: Bool
    
    var body: some View {
        HStack(spacing: 8) {
            // Hand indicator
            Circle()
                .fill(isDetected ? Color.green : Color.gray)
                .frame(width: 10, height: 10)
            
            // Status text
            if isDetected {
                Text(gesture == .none ? "No gesture" : "\(isLeftHand ? "Left" : "Right"): \(keyPressed)")
                    .foregroundColor(gesture == .none ? .gray : .primary)
                    .font(.system(size: 12))
            } else {
                Text("\(isLeftHand ? "Left" : "Right") hand not detected")
                    .foregroundColor(.gray)
                    .font(.system(size: 12))
            }
        }
    }
}

// Use HandVisualizationView from HandVisualizationView.swift
