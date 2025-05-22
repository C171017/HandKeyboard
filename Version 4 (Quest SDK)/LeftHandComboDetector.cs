using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR.Hands;
using UnityEngine.XR;
using UnityEngine.XR.Management;
using UnityEngine.SubsystemsImplementation; // ← also needed sometimes

public class LeftHandComboDetector : MonoBehaviour
{
    [SerializeField] private float detectionRadius = 0.025f;  // adjustable in Inspector

    private XRHandSubsystem handSubsystem;
    private Dictionary<XRHandJointID, bool> wasTouching = new();

    public TypingConsoleUI consoleUI;


    private Dictionary<XRHandJointID, char> keyMappings = new()
{
    { XRHandJointID.IndexProximal, 'A' },
    { XRHandJointID.IndexDistal, 'B' },
    { XRHandJointID.IndexTip, 'C' },

    { XRHandJointID.MiddleProximal, 'D' },
    { XRHandJointID.MiddleDistal, 'E' },
    { XRHandJointID.MiddleTip, 'F' },

    { XRHandJointID.RingProximal, 'G' },
    { XRHandJointID.RingDistal, 'H' },
    { XRHandJointID.RingTip, 'I' },

    { XRHandJointID.LittleProximal, 'J' },
    { XRHandJointID.LittleDistal, 'K' },
    { XRHandJointID.LittleTip, 'L' }
};


    // 12 joint targets (3 from each non-thumb finger)
    private XRHandJointID[] jointTargets = new XRHandJointID[]
    {
        XRHandJointID.IndexProximal,
        XRHandJointID.IndexDistal,
        XRHandJointID.IndexTip,

        XRHandJointID.MiddleProximal,
        XRHandJointID.MiddleDistal,
        XRHandJointID.MiddleTip,

        XRHandJointID.RingProximal,
        XRHandJointID.RingDistal,
        XRHandJointID.RingTip,

        XRHandJointID.LittleProximal,
        XRHandJointID.LittleDistal,
        XRHandJointID.LittleTip,
    };

    void Start()
    {

        // inside Start()
        List<XRHandSubsystem> handSubsystems = new List<XRHandSubsystem>();
        SubsystemManager.GetInstances(handSubsystems);

        if (handSubsystems.Count > 0)
        {
            handSubsystem = handSubsystems[0];
        }


        if (handSubsystem == null)
        {
            Debug.LogError("No XRHandSubsystem found.");
            enabled = false;
            return;
        }

        // Init state tracker
        foreach (var joint in jointTargets)
        {
            wasTouching[joint] = false;
        }
    }

    void Update()
    {
        if (!handSubsystem.leftHand.isTracked) return;

        var hand = handSubsystem.leftHand;
        var thumbTip = hand.GetJoint(XRHandJointID.ThumbTip);

        if (!thumbTip.TryGetPose(out Pose thumbPose)) return;

        foreach (var jointID in jointTargets)
        {
            var targetJoint = hand.GetJoint(jointID);

            if (!targetJoint.TryGetPose(out Pose targetPose)) continue;

            float distance = Vector3.Distance(thumbPose.position, targetPose.position);

            bool touching = distance < detectionRadius;

            // Only trigger on first contact
            if (touching && !wasTouching[jointID])
            {
                char typedChar = keyMappings[jointID];
                Debug.Log($"[LEFT] Typed: {typedChar}");
                if (consoleUI != null)
                {
                    consoleUI.Append(typedChar);
                }


                wasTouching[jointID] = true;
            }
            else if (!touching && wasTouching[jointID])
            {
                wasTouching[jointID] = false;
            }
        }
    }
}
