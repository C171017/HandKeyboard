//
//  HandKeyboardApp.swift
//  HandKeyboard
//
//  Created by C171017 on 4/12/25.
//

import SwiftUI
import AppKit
import AVFoundation

// App delegate for handling core functionality
class AppDelegate: NSObject {
    static let shared = AppDelegate()
    
    // Shared hand tracker instance
    let handTracker = HandTracker()
    
    // Setup app
    func setup() {
        // Request accessibility permissions for keyboard control
        let options: NSDictionary = [kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String: true]
        _ = AXIsProcessTrustedWithOptions(options)
        
        // Initialize hand tracker
        self.handTracker.findAvailableCameras()
        self.handTracker.startCapture()
    }
}

@main
struct HandKeyboardApp: App {
    // Initialize the AppDelegate
    @NSApplicationDelegateAdaptor private var appDelegateAdaptor: AppDelegateAdaptor
    
    init() {
        // Setup happens in AppDelegate
    }
    
    var body: some Scene {
        // Minimal window just to keep the app running
        WindowGroup {
            Text("Hand Keyboard Running")
                .frame(width: 300, height: 100)
                .onAppear {
                    // Start camera
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                        AppDelegate.shared.handTracker.startCapture()
                    }
                }
                .onDisappear {
                    AppDelegate.shared.handTracker.stopCapture()
                }
        }
        .windowStyle(.titleBar)
    }
}

// Adapter to use AppDelegate with SwiftUI App protocol
class AppDelegateAdaptor: NSObject, NSApplicationDelegate {
    // Expose the handTracker
    var handTracker: HandTracker { AppDelegate.shared.handTracker }
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        print("Application did finish launching")
        
        // Initialize the app
        AppDelegate.shared.setup()
        
        print("App delegate setup complete")
    }
}