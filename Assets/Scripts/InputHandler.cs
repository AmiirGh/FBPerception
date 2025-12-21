using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class InputHandler : MonoBehaviour
{

    public float keyboardHorizontal;
    public float keyboardVertical;
    public Vector2 rightThumbstick;
    public Vector2 leftThumbstick;

    public bool rightThumbstickButton;
    // Start is called before the first frame update
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {
        UpdateKeyboardInputs();
        UpdateMetaControllerInputs();
        
    }

    /// <summary>
    /// Update keyboard inputs
    /// </summary>
    void UpdateKeyboardInputs()
    {
        keyboardHorizontal = Input.GetAxis("Horizontal");
        keyboardVertical = Input.GetAxis("Vertical");
    }

    /// <summary>
    /// Updates meta controller inputs
    /// </summary>
    void UpdateMetaControllerInputs()
    {
        rightThumbstick = OVRInput.Get(OVRInput.Axis2D.SecondaryThumbstick);
        leftThumbstick = OVRInput.Get(OVRInput.Axis2D.PrimaryThumbstick);

        rightThumbstickButton = OVRInput.Get(OVRInput.Button.SecondaryThumbstick);
        Debug.Log($"rightThumbButton: {rightThumbstickButton}");
    }

}
