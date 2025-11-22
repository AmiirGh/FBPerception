using System.Collections;
using UnityEngine;

public class DynamicObstacleSpawner : MonoBehaviour
{
    [SerializeField]
    private GameObject dynamicObstacle;
    [SerializeField]
    private Transform UVATransform;
    private GameObject currentDynamicObstacle;
    private Vector3 dynamicObstaclePos = new Vector3(0, 0, 0);
    private float timer = 0;
    private int degree = 0;
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

            if (currentDynamicObstacle != null) Destroy(currentDynamicObstacle);

            degree = 10 * Random.Range(1, 37);
            dynamicObstaclePos = new Vector3(distanceRadius*Mathf.Cos(degree * Mathf.PI/180.0f),
                                             UVATransform.position.y,
                                             distanceRadius * Mathf.Sin(degree * Mathf.PI / 180.0f));
            currentDynamicObstacle = Instantiate(dynamicObstacle, UVATransform.position, Quaternion.identity);
            MoveDynamicObstacle();
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
            currentDynamicObstacle.transform.position = UVATransform.position + dynamicObstaclePos;
            yield return null;
        }
    }
}
