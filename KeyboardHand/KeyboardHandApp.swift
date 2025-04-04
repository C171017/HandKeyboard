//
//  KeyboardHandApp.swift
//  KeyboardHand
//
//  Created by C171017 on 4/3/25.
//

// KeyboardHandApp.swift
import SwiftUI

@main
struct KeyboardHandApp: App {
    @StateObject private var appState = AppState()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
        }
        .commands {
            CommandGroup(replacing: .newItem) {}
        }
    }
}

class AppState: ObservableObject {
    @Published var isCapturing = false
    let cameraManager = CameraManager()
    
    func toggleCapture() {
        isCapturing.toggle()
        
        if isCapturing {
            cameraManager.startCapture()
        } else {
            cameraManager.stopCapture()
        }
    }
}
