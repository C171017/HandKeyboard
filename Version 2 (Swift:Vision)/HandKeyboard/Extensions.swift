//
//  Extensions.swift
//  HandKeyboard
//
//  Created on 4/13/25.
//

import Foundation
import CoreGraphics

// Add isZero property to CGFloat for more readable code
extension CGFloat {
    var isZero: Bool {
        return self == 0.0
    }
}

// Add convenience methods for CGPoint
extension CGPoint {
    func distance(to point: CGPoint) -> CGFloat {
        return sqrt(pow(x - point.x, 2) + pow(y - point.y, 2))
    }
}