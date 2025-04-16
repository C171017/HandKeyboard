//
//  HandVisualizationView.swift
//  HandKeyboard
//
//  Created on 4/13/25.
//

import SwiftUI
import AppKit

// Hand visualization view
struct HandVisualizationView: NSViewRepresentable {
    var leftHandLandmarks: [CGPoint]
    var rightHandLandmarks: [CGPoint]
    
    func makeNSView(context: Context) -> NSView {
        let view = HandDrawingView()
        view.wantsLayer = true
        view.layer?.backgroundColor = NSColor.black.withAlphaComponent(0.1).cgColor
        return view
    }
    
    func updateNSView(_ nsView: NSView, context: Context) {
        if let view = nsView as? HandDrawingView {
            view.leftHandLandmarks = leftHandLandmarks
            view.rightHandLandmarks = rightHandLandmarks
            view.needsDisplay = true
        }
    }
}