using System.Collections;
using System.Collections.Generic;
using System.Threading;
using UnityEngine;

public class droneMovementController2 : MonoBehaviour
{

    private Rigidbody rb;
    public float forceMagnitude = 10f;
    public float dampingFactor = 0.9f; // How much to reduce velocity each frame when not actively moving (0.9 means 10% reduction)
                                       // F = ma =>  deltaV = (forceMagnitude / mass ) Time.fixedDeltaTime
    public float stopThreshold = 0.1f;
    
    private float timer = 0.0f;
    private float logInterval = 2.0f;
    private bool timerComplete = false;


    private float maxVelocity = 10.0f;

    void Start()
    {
        rb = GetComponent<Rigidbody>();
    }

    void FixedUpdate()
    {
        timer += Time.deltaTime;

        if (LogVelocities(timer, logInterval)) { timer = 0; }

        MoveBy("metaController");

        ClampVelocities();        
    }






    /// <summary>
    /// every interval seconds logs the velocities
    /// </summary>
    /// <param name="timer"></param>
    /// <param name="logInterval"></param> 
    /// <returns></returns>
    private bool LogVelocities(float timer, float logInterval)
    {
        if (timer >= logInterval)
        {
            Debug.Log($"drone vel total: {rb.linearVelocity}");
            Debug.Log($"drone vel x: {rb.linearVelocity.x}");
            Debug.Log($"drone vel y: {rb.linearVelocity.y}");
            Debug.Log($"drone vel z: {rb.linearVelocity.z}");
            return true;
        }
        return false;
    }


    /// <summary>
    /// Decides which controller type must be used. keboard or meta controllers
    /// controllerType must be keyboard or metaController
    /// </summary>
    /// <param name="controllerType"></param>
    private void MoveBy(string controllerType)
    {
        if (controllerType == "metaController")
        {
            MoveByMetaController();
        }
        if (controllerType == "keyboard")
        {
            MoveByKeyboard();
        }
    }

    /// <summary>
    /// Moves the drone using meta controllers
    /// </summary>
    private void MoveByMetaController()
    {
        Vector3 forceDirection = Vector3.zero;

        Vector2 rightThumbstick = OVRInput.Get(OVRInput.Axis2D.SecondaryThumbstick);
        Vector2 leftThumbstick  = OVRInput.Get(OVRInput.Axis2D.PrimaryThumbstick);
        Debug.Log($"left thumb x is: {leftThumbstick.x}");
        Debug.Log($"right thumb y is: {rightThumbstick.y}");
        
        
        // right/ left
        if (Mathf.Abs(leftThumbstick.x) > stopThreshold) { forceDirection += leftThumbstick.x * (Vector3.right); }
        else
        {
            if (Mathf.Abs(rb.linearVelocity.x) > stopThreshold) { rb.linearVelocity = new Vector3(rb.linearVelocity.x * dampingFactor, rb.linearVelocity.y, rb.linearVelocity.z); }
            else { rb.linearVelocity = new Vector3(0, rb.linearVelocity.y, rb.linearVelocity.z); }
        }

        // forward/backward
        if (Mathf.Abs(leftThumbstick.y) > stopThreshold) { forceDirection += leftThumbstick.y * (Vector3.forward); }
        else
        {
            if (Mathf.Abs(rb.linearVelocity.z) > stopThreshold) { rb.linearVelocity = new Vector3(rb.linearVelocity.x, rb.linearVelocity.y, rb.linearVelocity.z * dampingFactor); }
            else { rb.linearVelocity = new Vector3(rb.linearVelocity.x, rb.linearVelocity.y, 0); }
        }

        // forward/backward
        if (Mathf.Abs(rightThumbstick.y) > stopThreshold) { forceDirection += rightThumbstick.y * (Vector3.up); }
        else
        {
            if (Mathf.Abs(rb.linearVelocity.y) > stopThreshold) { rb.linearVelocity = new Vector3(rb.linearVelocity.x, rb.linearVelocity.y * dampingFactor, rb.linearVelocity.z); }
            else { rb.linearVelocity = new Vector3(rb.linearVelocity.x, 0, rb.linearVelocity.z); }
        }




        Debug.Log($"Force direction: {forceDirection}");
        if (forceDirection != Vector3.zero) { rb.AddForce(forceDirection.normalized * forceMagnitude, ForceMode.Force); }
    }

    /// <summary>
    /// Moves the drone using keboard
    /// </summary>
    private void MoveByKeyboard()
    {
        Vector3 forceDirection = Vector3.zero;

        // up/down
        if (Input.GetKey(KeyCode.E)) { forceDirection += Vector3.up; }
        else if (Input.GetKey(KeyCode.Q)) { forceDirection += Vector3.down; }
        else
        {
            if (Mathf.Abs(rb.linearVelocity.y) > stopThreshold) { rb.linearVelocity = new Vector3(rb.linearVelocity.x, rb.linearVelocity.y * dampingFactor, rb.linearVelocity.z); }
            else { rb.linearVelocity = new Vector3(rb.linearVelocity.x, 0, rb.linearVelocity.z); }
        }

        // right/left
        if (Input.GetKey(KeyCode.A)) { forceDirection += Vector3.left; }
        else if (Input.GetKey(KeyCode.D)) { forceDirection += Vector3.right; }
        else
        {
            if (Mathf.Abs(rb.linearVelocity.x) > stopThreshold) { rb.linearVelocity = new Vector3(rb.linearVelocity.x * dampingFactor, rb.linearVelocity.y, rb.linearVelocity.z); }
            else { rb.linearVelocity = new Vector3(0, rb.linearVelocity.y, rb.linearVelocity.z); }
        }

        // forward/backward
        if (Input.GetKey(KeyCode.W)) { forceDirection += Vector3.forward; }
        else if (Input.GetKey(KeyCode.S)) { forceDirection += Vector3.back; }
        else
        {
            if (Mathf.Abs(rb.linearVelocity.z) > stopThreshold) { rb.linearVelocity = new Vector3(rb.linearVelocity.x, rb.linearVelocity.y, rb.linearVelocity.z * dampingFactor); }
            else { rb.linearVelocity = new Vector3(rb.linearVelocity.x, rb.linearVelocity.y, 0); }
        }

        if (forceDirection != Vector3.zero) { rb.AddForce(forceDirection.normalized * forceMagnitude, ForceMode.Force); }
    }

    
    private void ClampVelocities()
    {
        Vector3 rbVelocity = rb.linearVelocity;
        if (Mathf.Abs(rbVelocity.x) >= maxVelocity) { rbVelocity.x = maxVelocity * Mathf.Sign(rbVelocity.x); }
        if (Mathf.Abs(rbVelocity.z) >= maxVelocity) { rbVelocity.z = maxVelocity * Mathf.Sign(rbVelocity.z); }
        if (Mathf.Abs(rbVelocity.y) >= maxVelocity) { rbVelocity.y = maxVelocity * Mathf.Sign(rbVelocity.y); }

        if (rb.linearVelocity.magnitude >= maxVelocity) { rb.linearVelocity = Vector3.ClampMagnitude(rb.linearVelocity, maxVelocity); }
    }
}
