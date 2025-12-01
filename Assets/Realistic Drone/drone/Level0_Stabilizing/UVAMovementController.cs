using System.Collections;
using System.Collections.Generic;
using System.Threading;
using Unity.VisualScripting;
using UnityEngine;

public class UVAMovementController : MonoBehaviour
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
    private float upSpeed = 15.0f;
    private float rightSpeed = 15.0f;
    private float forwardSpeed = 15.0f;
    public float xRange = 6.0f;
    public float yRange = 6.0f;
    private float dragFactor = 5.0f;
    void Start()
    {
        
        rb = GetComponent<Rigidbody>();
    }

    void Update()
    {
        timer += Time.deltaTime;

        //MoveBy("metaController");
        MoveBy("keyboard");

        ClampPosition();  
    }



    void ClampPosition()
    {
        Vector3 pos = rb.position;

        if (pos.x > xRange)
        {
            pos.x = xRange;
            rb.linearVelocity = new Vector3(0, rb.linearVelocity.y, rb.linearVelocity.z);
        }
        else if (pos.x < -xRange)
        {
            pos.x = -xRange;
            rb.linearVelocity = new Vector3(0, rb.linearVelocity.y, rb.linearVelocity.z);
        }

        if (pos.y > yRange)
        {
            pos.y = yRange;
            rb.linearVelocity = new Vector3(rb.linearVelocity.x, 0, rb.linearVelocity.z);
        }
        else if (pos.y < -yRange)
        {
            pos.y = -yRange;
            rb.linearVelocity = new Vector3(rb.linearVelocity.x, 0, rb.linearVelocity.z);
        }

        rb.position = pos;
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
        Vector2 rightThumbstick = OVRInput.Get(OVRInput.Axis2D.SecondaryThumbstick);
        Vector2 leftThumbstick = OVRInput.Get(OVRInput.Axis2D.PrimaryThumbstick);
        Debug.Log($"right thumb x is: {rightThumbstick.x}");
        Debug.Log($"right thumb y is: {rightThumbstick.y}");

        if (Mathf.Abs(leftThumbstick.x) > stopThreshold) rb.AddForce(transform.right * leftThumbstick.x * rightSpeed);
        else
        {
            rb.AddForce(-rb.linearVelocity.x * dragFactor, 0, 0);
        }

        if (Mathf.Abs(rightThumbstick.y) > stopThreshold) rb.AddForce(transform.up * rightThumbstick.y * upSpeed);
        else
        {
            rb.AddForce(0, -rb.linearVelocity.y * dragFactor, 0);
        }
        Vector3 currentVelocity = rb.linearVelocity;
        currentVelocity.z = forwardSpeed;
        rb.linearVelocity = currentVelocity;
    }

    /// <summary>
    /// Moves the drone using keboard
    /// </summary>
    private void MoveByKeyboard()
    {

        float horizontalInput = Input.GetAxis("Horizontal");
        float verticalInput   = Input.GetAxis("Vertical");

        if (Mathf.Abs(verticalInput) > stopThreshold)
        {
            rb.AddForce(transform.up * verticalInput * upSpeed);
        }
        else
        {
            rb.AddForce(0, -rb.linearVelocity.y * dragFactor, 0);
        }

        if (Mathf.Abs(horizontalInput) > stopThreshold)
        {
            rb.AddForce(transform.right * horizontalInput * rightSpeed);
        }
        else
        {
            rb.AddForce(-rb.linearVelocity.x * dragFactor, 0, 0);
        }

        Vector3 currentVelocity = rb.linearVelocity;
        currentVelocity.z = forwardSpeed;
        rb.linearVelocity = currentVelocity;
    }

    /// <summary>
    /// Prevent from over speeding
    /// </summary>
    private void ClampVelocities()
    {
        Vector3 rbVelocity = rb.linearVelocity;
        if (Mathf.Abs(rbVelocity.x) >= maxVelocity) { rbVelocity.x = maxVelocity * Mathf.Sign(rbVelocity.x); }
        if (Mathf.Abs(rbVelocity.z) >= maxVelocity) { rbVelocity.z = maxVelocity * Mathf.Sign(rbVelocity.z); }
        if (Mathf.Abs(rbVelocity.y) >= maxVelocity) { rbVelocity.y = maxVelocity * Mathf.Sign(rbVelocity.y); }

        if (rb.linearVelocity.magnitude >= maxVelocity) { rb.linearVelocity = Vector3.ClampMagnitude(rb.linearVelocity, maxVelocity); }
    }
}
