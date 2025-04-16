//
//  KeySimulator.swift
//  HandKeyboard
//
//  Created by Claude AI on 4/12/25.
//

import Foundation
import Carbon.HIToolbox
import AppKit

// This class handles translating string key names to actual keyboard events
class KeySimulator {
    
    // Dictionary that maps key names to macOS key codes
    static let keyCodeMap: [String: Int] = [
        // Letter keys (primary use case for this simplified version)
        "a": kVK_ANSI_A,
        "b": kVK_ANSI_B,
        "c": kVK_ANSI_C,
        "d": kVK_ANSI_D,
        "e": kVK_ANSI_E,
        "f": kVK_ANSI_F,
        "g": kVK_ANSI_G,
        "h": kVK_ANSI_H
    ]
    
    // Simulate a key press for a given key name
    static func simulateKeyPress(for keyName: String) {
        // Look up the key code in our map
        guard let keyCode = keyCodeMap[keyName] else {
            print("Unknown key: \(keyName)")
            return
        }
        
        // Create a shared event source
        guard let source = CGEventSource(stateID: .hidSystemState) else {
            print("Failed to create event source")
            return
        }
        
        // Create key down and key up events
        guard let keyDownEvent = CGEvent(keyboardEventSource: source, virtualKey: CGKeyCode(keyCode), keyDown: true),
              let keyUpEvent = CGEvent(keyboardEventSource: source, virtualKey: CGKeyCode(keyCode), keyDown: false) else {
            print("Failed to create keyboard events")
            return
        }
        
        // Target frontmost application if available
        if let targetPID = NSWorkspace.shared.frontmostApplication?.processIdentifier {
            keyDownEvent.postToPid(targetPID)
            usleep(20000) // 20ms delay
            keyUpEvent.postToPid(targetPID)
        } else {
            // Fallback to system tap
            keyDownEvent.post(tap: .cghidEventTap)
            usleep(20000) // 20ms delay
            keyUpEvent.post(tap: .cghidEventTap)
        }
    }
}