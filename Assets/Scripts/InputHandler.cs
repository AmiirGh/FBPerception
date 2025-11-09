using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class InputHandler : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        Debug.Log($"sstart");
    }

    // Update is called once per frame
    void Update()
    {
        
        
        if (OVRInput.GetDown(OVRInput.Button.One))
        {
            Debug.Log("A/X button pressed");
        }
        Vector2 thumbstick = OVRInput.Get(OVRInput.Axis2D.PrimaryThumbstick);
        if(thumbstick.magnitude > 0.1f)
        {
            Debug.Log($"Thumbstick: {thumbstick}");
        }
        Debug.Log($"Thumbsticck: {thumbstick}");
        
    }

    public void LogGenerator()
    {
        Debug.Log("Primary 1 is pressed");
    }
}
