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


### Project README

Not sure where's the problem... Z axis doesn't seem to work

#### Version 1
A simple demo built with Python, allowing users to scroll pages by activating and deactivating a fist gesture. Designed to facilitate hands-free reading by eliminating reliance on mouse and keyboard inputs. This version was lost along with my previous laptop.

#### Version 2 (Previous repo deleted)
Developed using Swift and Apple's Vision framework, this iteration aimed at becoming a general solution for a new gesture-based typing method. Throughout development, the exact mechanism underwent several iterations. Ultimately, this version was abandoned due to challenges arising from processing 2D images without LiDAR or TrueDepth sensors, which frequently led to inaccurate gesture recognition and unintended actions.

## 🎬 Demo

[![Watch the demo](https://img.youtube.com/vi/eBK7kDqg1JQ/hqdefault.jpg)](https://youtube.com/shorts/eBK7kDqg1JQ)

#### Version 3 (In Progress)
Currently rebuilding the project in Python using MediaPipe, which features simulated pseudo-3D processing capabilities to improve gesture recognition accuracy.

#### Version 4 (Planning Stage)
Exploring the development of a dedicated Meta Quest application for enhanced spatial gesture interaction.
