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

    public float degreeRad = 0; // degree in radian (0, 2*pi)
    public float degreeDeg = 0; // degree in degree (0,360)
    public int degreeInt = 0;
    public int level = 0;
    private GameObject currentDynamicObstacle;
    public Vector3 dynamicObstaclePos = new Vector3(0, 0, 0);
    private float timer = 0;
    public int trialNumber = 0; // Is ++ when a new obstacle is generated
    public int intervalNumber = 0; // is ++ when a new interval (after intervalDuration time) is started
    private float distanceRadius = 10.0f;
    private List<float> distanceRadii = new List<float> { 12, 8, 4 };
    public bool isDynamicObstaclePresent = false;
    public float dynamicObstaclePresenceDuration;
    private float intervalDuration = 10.0f;

    void Start()
    {
        dynamicObstaclePresenceDuration = 2.0f;
    }

    void Update()
    {
        timer += Time.deltaTime;
        if (timer >= intervalDuration)
        {

            StartCoroutine(GenerateNewInterval());
            timer = 0;
            intervalNumber++;
        }
    }
    void LateUpdate()
    {
        if (currentDynamicObstacle != null)
        {
            currentDynamicObstacle.transform.position = UVATransform.position + new Vector3(dynamicObstaclePos.x, 0, dynamicObstaclePos.z);
        }
    }

    /// <summary>
    /// This  method starts a new interval (every intervalDuration seconds)
    /// then generates a random number to randomize the time when a new dynamic obstacle is actually generated.
    /// </summary>
    /// <returns></returns>
    IEnumerator GenerateNewInterval()
    {
        float spawnAfter = UnityEngine.Random.Range(0.0f, 4.0f);
        yield return new WaitForSeconds(spawnAfter);
        GenerateDynamicObstacle();
        trialNumber++;
        isDynamicObstaclePresent = true;
        yield return new WaitForSeconds(dynamicObstaclePresenceDuration);
        if (currentDynamicObstacle != null) Destroy(currentDynamicObstacle);
        isDynamicObstaclePresent = false;
    } 

    /// <summary>
    /// Spawns dynamic obstacle
    /// </summary>
    void GenerateDynamicObstacle()
    {
        

        (degreeInt, degreeRad, degreeDeg, level) = GetDegreeLevel();
        dynamicObstaclePos = new Vector3(distanceRadii[level] * Mathf.Cos(degreeRad),
                                         UVATransform.position.y,
                                         distanceRadii[level] * Mathf.Sin(degreeRad));
        currentDynamicObstacle = Instantiate(dynamicObstacle, UVATransform.position, Quaternion.identity);
    }

    /// <summary>
    /// returns random values for degree (pi/4, pi/2, 3pi/4, ...) and level (1, 2, 3)
    /// </summary>
    /// <returns></returns>
    Tuple<int, float, float, int> GetDegreeLevel()
    {
        int degreeInFuncInt = UnityEngine.Random.Range(0, 8);
        float degreeInFuncDeg = degreeInFuncInt * 45.0f; // in degree
        float degreeInFuncRad = Mathf.PI / 4 * degreeInFuncInt; // in radians
        int levelInFunc = UnityEngine.Random.Range(0, 3);
        Debug.Log($"LevelFunc: {levelInFunc}");
        return Tuple.Create(degreeInFuncInt, degreeInFuncRad, degreeInFuncDeg, levelInFunc);
    }

}
