using System.Collections;
using UnityEngine;

public class DynamicObstacleSpawner : MonoBehaviour
{
    [SerializeField]
    private GameObject dynamicObstacle;
    [SerializeField]
    private Transform UVATransform;

    public int degree = 0;
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
        if (currentDynamicObstacle != null) Debug.Log($"distance between obstacle and uva: {UVATransform.position - currentDynamicObstacle.transform.position}");
        timer += Time.deltaTime;
        if (timer >= 3)
        {
            timer = 0;

            if (currentDynamicObstacle != null) Destroy(currentDynamicObstacle);

            degree = 10 * Random.Range(1, 37);
            dynamicObstaclePos = new Vector3(distanceRadius*Mathf.Cos(degree * Mathf.PI/180.0f),
                                             UVATransform.position.y,
                                             distanceRadius * Mathf.Sin(degree * Mathf.PI / 180.0f));
            currentDynamicObstacle = Instantiate(dynamicObstacle, UVATransform.position, Quaternion.identity);
            //MoveDynamicObstacle();
        }
    }
    void LateUpdate()
    {
        // This runs every frame, AFTER the box (uva) has moved.
        if (currentDynamicObstacle != null)
        {
            currentDynamicObstacle.transform.position = UVATransform.position + new Vector3(dynamicObstaclePos.x, 0, dynamicObstaclePos.z);
        }
    }
    void MoveDynamicObstacle()
    {
        StartCoroutine(KeepConstantDistance());
    }
    IEnumerator KeepConstantDistance()
    {
        float elapsedTime = 0f;
        while (elapsedTime < appearanceDuration)
        {
            elapsedTime += Time.deltaTime;
            currentDynamicObstacle.transform.position = UVATransform.position + new Vector3(dynamicObstaclePos.x, 0, dynamicObstaclePos.z); 
            yield return null;
        }
    }
}
