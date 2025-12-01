using System.Collections;
using UnityEngine;

public class DynamicObstacleSpawner : MonoBehaviour
{
    [SerializeField]
    private GameObject dynamicObstacle;
    [SerializeField]
    private Transform UVATransform;

    public float degree = 0;
    private GameObject currentDynamicObstacle;
    public Vector3 dynamicObstaclePos = new Vector3(0, 0, 0);
    private float timer = 0;
    
    private float distanceRadius = 10.0f;
    private float appearanceDuration = 5.0f;
    void Start()
    {
        
    }

    void Update()
    {
        timer += Time.deltaTime;
        if (timer >= 3)
        {
            timer = 0;
            GenerateDynamicObstacle();
        }
    }
    void LateUpdate()
    {
        if (currentDynamicObstacle != null)
        {
            currentDynamicObstacle.transform.position = UVATransform.position + new Vector3(dynamicObstaclePos.x, 0, dynamicObstaclePos.z);
        }
    }
    void GenerateDynamicObstacle()
    {
        if (currentDynamicObstacle != null) Destroy(currentDynamicObstacle);

        degree = Mathf.PI/4 * Random.Range(0, 8); // in radians
        dynamicObstaclePos = new Vector3(distanceRadius * Mathf.Cos(degree),
                                         UVATransform.position.y,
                                         distanceRadius * Mathf.Sin(degree));
        currentDynamicObstacle = Instantiate(dynamicObstacle, UVATransform.position, Quaternion.identity);
    }

}
