//
//  HandGesture.swift
//  KeyboardHand
//
//  Created by C171017 on 4/3/25.
//

// Models/HandGesture.swift
import Foundation

struct HandGesture: Equatable, Hashable {
    enum Handedness: Hashable {
        case left
        case right
    }
    
    enum PinchingFinger: Hashable {
        case index
        case middle
        case ring
        case little
    }
    
    enum PalmOrientation: Hashable {
        case up
        case down
        case facingEachOther
        case unknown
    }
    
    let handedness: Handedness
    let pinchingFinger: PinchingFinger
    let palmOrientation: PalmOrientation
    
    // Swift can automatically synthesize Hashable conformance
    // for structs when all stored properties are Hashable
    // But if you need to provide a custom implementation:
    /*
    func hash(into hasher: inout Hasher) {
        hasher.combine(handedness)
        hasher.combine(pinchingFinger)
        hasher.combine(palmOrientation)
    }
    */
}
