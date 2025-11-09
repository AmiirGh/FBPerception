using UnityEngine;

public class CubeMovement : MonoBehaviour
{
    // Public variables appear in the Inspector for easy tuning
    [Header("Movement Parameters")]
    public float speed = 2.0f;           // Controls how fast the angle (and thus movement) changes
    public float radius = 7.0f;          // The radius of the circle
    public Vector3 centerPoint;          // The center point of the circle

    private float currentAngle;          // The current angle in radians

    void Start()
    {
        // Initialize the center point to the object's starting position
        // so it rotates around where it was placed in the scene.
        centerPoint = new Vector3(0, 0, 0);

        // Set the initial angle to 0
        currentAngle = 0f;
    }

    void Update()
    {
        // 1. Increment the angle over time
        // Time.deltaTime ensures the speed is frame-rate independent.
        // The angle is in radians because Mathf.Cos/Sin use radians.
        currentAngle += speed * Time.deltaTime;

        // 2. Calculate the new X and Z positions using trigonometry
        // Mathf.Cos is for the X-axis
        float x = centerPoint.x + radius * Mathf.Cos(currentAngle);

        // Mathf.Sin is for the Z-axis (the forward/backward direction)
        float z = centerPoint.z + radius * Mathf.Sin(currentAngle);

        // 3. Keep the Y position constant (assuming level movement)
        float y = transform.position.y;

        // 4. Apply the new position to the cube
        transform.position = new Vector3(x, y, z);
    }
}