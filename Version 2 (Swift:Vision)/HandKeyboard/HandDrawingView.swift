//
//  HandDrawingView.swift
//  HandKeyboard
//
//  Created on 4/13/25.
//

import SwiftUI
import AppKit

// Custom view that draws hand landmarks
class HandDrawingView: NSView {
    var leftHandLandmarks: [CGPoint] = []
    var rightHandLandmarks: [CGPoint] = []
    
    override func draw(_ dirtyRect: NSRect) {
        super.draw(dirtyRect)
        
        guard let context = NSGraphicsContext.current?.cgContext else { return }
        
        // Draw left hand landmarks in green
        if !leftHandLandmarks.isEmpty {
            drawHandLandmarks(context, points: leftHandLandmarks, color: NSColor.green.cgColor)
        }
        
        // Draw right hand landmarks in blue
        if !rightHandLandmarks.isEmpty {
            drawHandLandmarks(context, points: rightHandLandmarks, color: NSColor.blue.cgColor)
        }
    }
    
    private func drawHandLandmarks(_ context: CGContext, points: [CGPoint], color: CGColor) {
        context.setLineWidth(2.0)
        context.setStrokeColor(color)
        context.setFillColor(color)
        
        // Draw dots for each landmark point
        for point in points {
            // Skip invalid points
            if point.x.isZero && point.y.isZero {
                continue
            }
            
            // Applying transformations:
            // 1. Mirror horizontally (1-x) for a natural mirror view
            // 2. Flip vertically (1-y) to match Vision's top-left origin 
            let adjustedPoint = CGPoint(
                x: (1 - point.x) * bounds.width, 
                y: (1 - point.y) * bounds.height
            )
            
            // Draw a small circle at each point
            context.addArc(center: adjustedPoint, radius: 3, startAngle: 0, endAngle: 2 * .pi, clockwise: false)
            context.drawPath(using: .fillStroke)
        }
        
        // Only draw connections if we have enough points for a hand
        if points.count >= 21 {
            drawHandConnections(context, points: points, color: color)
        }
    }
    
    private func drawHandConnections(_ context: CGContext, points: [CGPoint], color: CGColor) {
        context.setLineWidth(1.5)
        context.setStrokeColor(color)
        
        // Transform all points with mirroring and flipping
        let adjustedPoints = points.map { 
            CGPoint(
                x: (1 - $0.x) * bounds.width,
                y: (1 - $0.y) * bounds.height
            )
        }
        
        // Connect thumb
        if let wrist = getValidPoint(adjustedPoints, index: 0),
           let thumbCMC = getValidPoint(adjustedPoints, index: 1),
           let thumbMP = getValidPoint(adjustedPoints, index: 2),
           let thumbIP = getValidPoint(adjustedPoints, index: 3),
           let thumbTip = getValidPoint(adjustedPoints, index: 4) {
            
            drawLine(context, from: wrist, to: thumbCMC)
            drawLine(context, from: thumbCMC, to: thumbMP)
            drawLine(context, from: thumbMP, to: thumbIP)
            drawLine(context, from: thumbIP, to: thumbTip)
        }
        
        // Connect index finger
        connectFinger(context, points: adjustedPoints, baseIndex: 5)
        
        // Connect middle finger
        connectFinger(context, points: adjustedPoints, baseIndex: 9)
        
        // Connect ring finger
        connectFinger(context, points: adjustedPoints, baseIndex: 13)
        
        // Connect pinky finger
        connectFinger(context, points: adjustedPoints, baseIndex: 17)
        
        // Connect palm
        if let wrist = getValidPoint(adjustedPoints, index: 0),
           let indexBase = getValidPoint(adjustedPoints, index: 5),
           let middleBase = getValidPoint(adjustedPoints, index: 9),
           let ringBase = getValidPoint(adjustedPoints, index: 13),
           let pinkyBase = getValidPoint(adjustedPoints, index: 17) {
            
            drawLine(context, from: wrist, to: indexBase)
            drawLine(context, from: indexBase, to: middleBase)
            drawLine(context, from: middleBase, to: ringBase)
            drawLine(context, from: ringBase, to: pinkyBase)
            drawLine(context, from: pinkyBase, to: wrist)
        }
    }
    
    private func getValidPoint(_ points: [CGPoint], index: Int) -> CGPoint? {
        guard index < points.count else { return nil }
        let point = points[index]
        return (point.x.isZero && point.y.isZero) ? nil : point
    }
    
    private func connectFinger(_ context: CGContext, points: [CGPoint], baseIndex: Int) {
        if let base = getValidPoint(points, index: baseIndex),
           let knuckle = getValidPoint(points, index: baseIndex + 1),
           let middle = getValidPoint(points, index: baseIndex + 2),
           let tip = getValidPoint(points, index: baseIndex + 3) {
            
            drawLine(context, from: base, to: knuckle)
            drawLine(context, from: knuckle, to: middle)
            drawLine(context, from: middle, to: tip)
        }
    }
    
    private func drawLine(_ context: CGContext, from: CGPoint, to: CGPoint) {
        context.beginPath()
        context.move(to: from)
        context.addLine(to: to)
        context.strokePath()
    }
}