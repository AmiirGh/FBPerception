using UnityEngine;

public class MyGameManager : MonoBehaviour
{
    [SerializeField]
    private DynamicObstacleSpawner dynamicObstacleSpawner;
    [SerializeField] Transform centerEyeAnchorTransform;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (dynamicObstacleSpawner.intervalNumber > 216) // 8*3*3*9
        {
            Time.timeScale = 0f;
            Application.Quit();
        }
        Vector3 rot = centerEyeAnchorTransform.localEulerAngles;

        // Convert 0-360 range to -180 to 180 range
        float x = (rot.x > 180) ? rot.x - 360 : rot.x;
        float y = (rot.y > 180) ? rot.y - 360 : rot.y;
        float z = (rot.z > 180) ? rot.z - 360 : rot.z;

        Debug.Log($"Inspector-like Rotation: X:{x}, Y:{y}, Z:{z}");


    }
}
