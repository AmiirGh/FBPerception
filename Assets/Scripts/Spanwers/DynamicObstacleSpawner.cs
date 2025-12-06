using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DynamicObstacleSpawner : MonoBehaviour
{
    [SerializeField]
    private GameObject dynamicObstacle;
    [SerializeField]
    private Transform UVATransform;

    public float degree = 0;
    public int degreeInt = 0;
    public int level = 0;
    private GameObject currentDynamicObstacle;
    public Vector3 dynamicObstaclePos = new Vector3(0, 0, 0);
    private float timer = 0;
    
    private float distanceRadius = 10.0f;
    private List<float> distanceRadii = new List<float> { 12, 8, 4 };
    private float appearanceDuration = 10.0f;
    void Start()
    {
        
    }

    void Update()
    {
        timer += Time.deltaTime;
        if (timer >= appearanceDuration)
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

        (degreeInt, degree, level) = GetDegreeLevel();
        dynamicObstaclePos = new Vector3(distanceRadii[level] * Mathf.Cos(degree),
                                         UVATransform.position.y,
                                         distanceRadii[level] * Mathf.Sin(degree));
        currentDynamicObstacle = Instantiate(dynamicObstacle, UVATransform.position, Quaternion.identity);
    }

    /// <summary>
    /// returns random values for degree (pi/4, pi/2, 3pi/4, ...) and level (1, 2, 3)
    /// </summary>
    /// <returns></returns>
    Tuple<int, float, int> GetDegreeLevel()
    {
        int degreeInFuncInt = UnityEngine.Random.Range(0, 8);
        float degreeInFunc = Mathf.PI / 4 * degreeInFuncInt; // in radians
        
        int levelInFunc = UnityEngine.Random.Range(0, 3);
        Debug.Log($"LevelFunc: {levelInFunc}");
        return Tuple.Create(degreeInFuncInt, degreeInFunc, levelInFunc);
    }

}
