//
//  AppState.swift
//  HandKeyboard
//
//  Created on 4/13/25.
//

import SwiftUI
import AppKit
import Combine

// Minimal app state class - only contains what's needed for core functionality
class AppState: ObservableObject {
    static let shared = AppState()
    
    init() {
        print("AppState initialized")
    }
}