using UnityEngine;

public class VisualFeedback : MonoBehaviour
{
    public DynamicObstacleSpawner dynamicObstacleSpawner;
    public Vector3 circlePosition = new Vector3(0,0,0);


    void Start()
    {
    }

    // Update is called once per frame
    void Update()
    {
        circlePosition = new Vector3(dynamicObstacleSpawner.dynamicObstaclePos.x, dynamicObstacleSpawner.dynamicObstaclePos.z, transform.position.z);
        

    }
}
