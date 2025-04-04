//
//  ContentView.swift
//  KeyboardHand
//
//  Created by C171017 on 4/3/25.
//

// ContentView.swift
import SwiftUI

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        VStack {
            Text("Hand Gesture Keyboard")
                .font(.title)
                .padding()
            
            Button(action: {
                appState.toggleCapture()
            }) {
                Text(appState.isCapturing ? "Stop Capturing" : "Start Capturing")
                    .padding()
                    .background(appState.isCapturing ? Color.red : Color.green)
                    .foregroundColor(.white)
                    .cornerRadius(10)
            }
            
            if appState.isCapturing {
                Text("Status: Active")
                    .foregroundColor(.green)
                    .padding()
            } else {
                Text("Status: Inactive")
                    .foregroundColor(.red)
                    .padding()
            }
        }
        .frame(width: 300, height: 200)
    }
}
