## 🎬 Demo (version 3)

[![Watch the demo](https://img.youtube.com/vi/eBK7kDqg1JQ/hqdefault.jpg)](https://youtube.com/shorts/eBK7kDqg1JQ)

## 🎬 Demo (version 4)

[![Watch the demo]()](https://youtube.com/shorts/r-O3qNZsaQk)

Hand-Gesture Keyboard · Next-Gen MR/VR Text-Input Prototype

Hands-only typing for smart glasses, MR headsets, and VR devices—no physical/virtual keyboard.

⸻

✨ Key Idea

Detect the 3-D relative positions of both-hand joints, map specific spatial “poses” to characters, and fire native keystrokes. This bypasses awkward VR virtual keyboards and be an alternative to speech input.

⸻

🚀 Project Timeline

Version	Tech Stack	Goal	Status
v1	Python + MediaPipe	One-hand fist toggle for auto-scroll	Demo lost with old laptop

v2	Swift + Apple Vision	Full gesture-typing prototype in 2-D	Abandoned – depth ambiguity without LiDAR/TrueDepth

v3 (Work in Progress)	Python + MediaPipe (pseudo-3-D)	Simulate depth, add debounce/cool-down, dual-range detection & smoothing	Active development

v4 (Planned)	Meta Quest hand-tracking SDK	Native Quest app, full 6-DoF gestures	Design phase



⸻

🛠️ Current Focus (v3)
	•	Pseudo-3-D coordinates: derive Z from landmark scale differences.
	•	Robustness: debounce timers, cool-down windows, dual in/out ranges, Gaussian smoothing.
	•	Keystroke mapper: configurable JSON mapping joint-combo → key.
	•	Cross-platform stub: WebSocket server broadcasts recognized keys to any client.

#### Version 1
A simple demo built with Python, allowing users to scroll pages by activating and deactivating a fist gesture. Designed to facilitate hands-free reading by eliminating reliance on mouse and keyboard inputs. This version was lost along with my previous laptop.

#### Version 2 (Previous repo deleted)
Developed using Swift and Apple's Vision framework, this iteration aimed at becoming a general solution for a new gesture-based typing method. Throughout development, the exact mechanism underwent several iterations. Ultimately, this version was abandoned due to challenges arising from processing 2D images without LiDAR or TrueDepth sensors, which frequently led to inaccurate gesture recognition and unintended actions.



#### Version 3 (In Progress)
Currently rebuilding the project in Python using MediaPipe, which features simulated pseudo-3D processing capabilities to improve gesture recognition accuracy.

#### Version 4 (In Progress)

## 📁 Project Structure

Place the following files inside `Assets/Scripts/`:

- `LeftHandComboDetector.cs` – Detects thumb contact on left-hand fingers and maps to letters A–L.
- `RightHandComboDetector.cs` – Detects thumb contact on right-hand fingers and maps to letters M–X.
- `TypingConsoleUI.cs` – A simple script that displays the typed characters on a TextMeshPro UI object.

---

## 🛠️ Setup Instructions (Unity 2022.3+)

### 1. ✅ Prerequisites
Make sure your project includes:
- **OpenXR Plugin** (`com.unity.xr.openxr`)
- **Meta XR SDK** packages (Core, Hands, Interaction, etc.)
- **XR Hands subsystem**
- **TextMeshPro** (import TMP Essentials)

---

### 2. 🧩 Scene Setup

#### A. XR Rig and Hand Trackers
1. Create an **XR Origin (XR Rig)** or **OVRCameraRig** (depending on setup)
2. Under the XR Rig, add two empty GameObjects:
   - `LeftHandTracker`
   - `RightHandTracker`
3. Attach the `LeftHandComboDetector` and `RightHandComboDetector` scripts to these objects respectively.

#### B. Typing Output (UI Console)
1. **Right-click in Hierarchy** → `UI > Canvas`
2. Set Canvas `Render Mode` to **World Space**
3. Inside Canvas:
   - Add `UI > Text - TextMeshPro`
   - Rename it to `TypingConsoleText`
   - Set font size (e.g., 36), color, alignment, and scale
4. Create an empty GameObject named **`TypingConsoleUI`**
   - Attach the `TypingConsoleUI.cs` script to it
   - Drag the `TypingConsoleText` object into the `textBox` field of the script

#### C. Connect Scripts
1. In the Inspector for both `LeftHandComboDetector` and `RightHandComboDetector`:
   - Drag the `TypingConsoleUI` GameObject into their `consoleUI` field

---

### 3. ✋ Enable Hand Tracking

1. Go to **Edit > Project Settings > XR Plug-in Management > OpenXR > Features**
2. Enable:
   - `Hand Tracking Subsystem`
   - `Meta Hand Tracking Aim`
   - `Meta XR Feature` (if available)

3. (Optional but recommended) **Add Hand Visualizer:**
   - Import the `HandVisualizer` sample from **XR Hands**
   - Attach it to `LeftHandVisualizer` and `RightHandVisualizer` GameObjects
   - Configure to show hand meshes and joints

---

### 4. ▶️ Test It

- Connect your Meta Quest using **Quest Link**
- Enter **Play Mode** in Unity
- Bring your **thumb to other finger joints**
- You should see `[LEFT] Typed: A`, etc., in the Console and live text in the Typing Console
