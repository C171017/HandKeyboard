//
//  CameraPreviewView.swift
//  HandKeyboard
//
//  Created on 4/13/25.
//

import SwiftUI
import AVFoundation

struct CameraPreviewView: NSViewRepresentable {
    var session: AVCaptureSession
    
    func makeNSView(context: Context) -> NSView {
        let view = CameraView()
        view.wantsLayer = true
        view.layer?.backgroundColor = NSColor.black.cgColor
        
        // Create and configure preview layer
        let previewLayer = AVCaptureVideoPreviewLayer(session: session)
        previewLayer.videoGravity = .resizeAspectFill
        
        // Apply mirroring once the connection is available
        if let connection = previewLayer.connection {
            connection.automaticallyAdjustsVideoMirroring = false
            connection.isVideoMirrored = true // Mirror for more natural camera view
        }
        
        view.previewLayer = previewLayer
        view.layer?.addSublayer(previewLayer)
        
        return view
    }
    
    func updateNSView(_ nsView: NSView, context: Context) {
        if let cameraView = nsView as? CameraView {
            // Make sure we update the session on the preview layer
            if cameraView.previewLayer?.session !== session {
                cameraView.previewLayer?.session = session
            }
            
            // Update frame
            cameraView.updateLayerFrame()
        }
    }
    
    // Custom view class that manages the preview layer
    class CameraView: NSView {
        var previewLayer: AVCaptureVideoPreviewLayer?
        
        override func layout() {
            super.layout()
            updateLayerFrame()
        }
        
        func updateLayerFrame() {
            if let layer = previewLayer {
                CATransaction.begin()
                CATransaction.setDisableActions(true)
                layer.frame = bounds
                CATransaction.commit()
            }
        }
    }
}

// Use CameraWindow from CameraWindow.swift