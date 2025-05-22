using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR.Hands;
using UnityEngine.XR;
using UnityEngine.XR.Management;
using UnityEngine.SubsystemsImplementation; // ← also needed sometimes


public class RightHandComboDetector : MonoBehaviour
{
    [SerializeField] private float detectionRadius = 0.025f;

    private XRHandSubsystem handSubsystem;
    private Dictionary<XRHandJointID, bool> wasTouching = new();

    public TypingConsoleUI consoleUI;

    private Dictionary<XRHandJointID, char> keyMappings = new()
{
    { XRHandJointID.IndexProximal, 'M' },
    { XRHandJointID.IndexDistal, 'N' },
    { XRHandJointID.IndexTip, 'O' },

    { XRHandJointID.MiddleProximal, 'P' },
    { XRHandJointID.MiddleDistal, 'Q' },
    { XRHandJointID.MiddleTip, 'R' },

    { XRHandJointID.RingProximal, 'S' },
    { XRHandJointID.RingDistal, 'T' },
    { XRHandJointID.RingTip, 'U' },

    { XRHandJointID.LittleProximal, 'V' },
    { XRHandJointID.LittleDistal, 'W' },
    { XRHandJointID.LittleTip, 'X' }
};


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

        foreach (var joint in jointTargets)
        {
            wasTouching[joint] = false;
        }
    }

    void Update()
    {
        if (!handSubsystem.rightHand.isTracked) return;

        var hand = handSubsystem.rightHand;
        var thumbTip = hand.GetJoint(XRHandJointID.ThumbTip);

        if (!thumbTip.TryGetPose(out Pose thumbPose)) return;

        foreach (var jointID in jointTargets)
        {
            var targetJoint = hand.GetJoint(jointID);

            if (!targetJoint.TryGetPose(out Pose targetPose)) continue;

            float distance = Vector3.Distance(thumbPose.position, targetPose.position);
            bool touching = distance < detectionRadius;

            if (touching && !wasTouching[jointID])
            {
                char typedChar = keyMappings[jointID];
                Debug.Log($"[RIGHT] Typed: {typedChar}");
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
