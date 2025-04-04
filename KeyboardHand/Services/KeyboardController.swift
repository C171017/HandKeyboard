//
//  KeyboardController.swift
//  KeyboardHand
//
//  Created by C171017 on 4/3/25.
//

// Services/KeyboardController.swift
import Carbon

class KeyboardController {
    // Mapping from gestures to key codes
    private let gestureToKeyMapping: [HandGesture: Int] = [
        // Left hand, palm up
        HandGesture(handedness: .left, pinchingFinger: .index, palmOrientation: .up): kVK_ANSI_A,
        HandGesture(handedness: .left, pinchingFinger: .middle, palmOrientation: .up): kVK_ANSI_S,
        HandGesture(handedness: .left, pinchingFinger: .ring, palmOrientation: .up): kVK_ANSI_D,
        HandGesture(handedness: .left, pinchingFinger: .little, palmOrientation: .up): kVK_ANSI_F,
        
        // Left hand, palm down
        HandGesture(handedness: .left, pinchingFinger: .index, palmOrientation: .down): kVK_ANSI_G,
        HandGesture(handedness: .left, pinchingFinger: .middle, palmOrientation: .down): kVK_ANSI_H,
        HandGesture(handedness: .left, pinchingFinger: .ring, palmOrientation: .down): kVK_ANSI_J,
        HandGesture(handedness: .left, pinchingFinger: .little, palmOrientation: .down): kVK_ANSI_K,
        
        // Left hand, palms facing each other
        HandGesture(handedness: .left, pinchingFinger: .index, palmOrientation: .facingEachOther): kVK_ANSI_L,
        HandGesture(handedness: .left, pinchingFinger: .middle, palmOrientation: .facingEachOther): kVK_ANSI_Z,
        HandGesture(handedness: .left, pinchingFinger: .ring, palmOrientation: .facingEachOther): kVK_ANSI_X,
        HandGesture(handedness: .left, pinchingFinger: .little, palmOrientation: .facingEachOther): kVK_ANSI_C,
        
        // Right hand, palm up
        HandGesture(handedness: .right, pinchingFinger: .index, palmOrientation: .up): kVK_ANSI_V,
        HandGesture(handedness: .right, pinchingFinger: .middle, palmOrientation: .up): kVK_ANSI_B,
        HandGesture(handedness: .right, pinchingFinger: .ring, palmOrientation: .up): kVK_ANSI_N,
        HandGesture(handedness: .right, pinchingFinger: .little, palmOrientation: .up): kVK_ANSI_M,
        
        // Right hand, palm down
        HandGesture(handedness: .right, pinchingFinger: .index, palmOrientation: .down): kVK_ANSI_1,
        HandGesture(handedness: .right, pinchingFinger: .middle, palmOrientation: .down): kVK_ANSI_2,
        HandGesture(handedness: .right, pinchingFinger: .ring, palmOrientation: .down): kVK_ANSI_3,
        HandGesture(handedness: .right, pinchingFinger: .little, palmOrientation: .down): kVK_ANSI_4,
        
        // Right hand, palms facing each other
        HandGesture(handedness: .right, pinchingFinger: .index, palmOrientation: .facingEachOther): kVK_ANSI_5,
        HandGesture(handedness: .right, pinchingFinger: .middle, palmOrientation: .facingEachOther): kVK_ANSI_6,
        HandGesture(handedness: .right, pinchingFinger: .ring, palmOrientation: .facingEachOther): kVK_ANSI_7,
        HandGesture(handedness: .right, pinchingFinger: .little, palmOrientation: .facingEachOther): kVK_ANSI_8
    ]
    
    func executeKeyboardCommand(for gesture: HandGesture) {
        guard let keyCode = gestureToKeyMapping[gesture] else {
            print("No mapping for gesture: \(gesture)")
            return
        }
        
        simulateKeyPress(keyCode: keyCode)
    }
    
    private func simulateKeyPress(keyCode: Int) {
        let source = CGEventSource(stateID: .combinedSessionState)
        
        // Key down
        if let keyDownEvent = CGEvent(keyboardEventSource: source, virtualKey: CGKeyCode(keyCode), keyDown: true) {
            keyDownEvent.post(tap: .cghidEventTap)
        }
        
        // Small delay
        usleep(10000) // 10ms
        
        // Key up
        if let keyUpEvent = CGEvent(keyboardEventSource: source, virtualKey: CGKeyCode(keyCode), keyDown: false) {
            keyUpEvent.post(tap: .cghidEventTap)
        }
    }
}
