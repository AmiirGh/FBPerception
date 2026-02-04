using System;
using UnityEditor;
using UnityEngine;

public class MyGameManager : MonoBehaviour
{
    [SerializeField]
    private DynamicObstacleSpawner dynamicObstacleSpawner;
    [SerializeField] private Transform centerEyeAnchorTransform;
    [SerializeField] private InputHandler inputHandler;
    private DateTime partStartTime;
    public float unityTimestamp = 0;
    public int experimentPartNumber = 1; // Experiment has 3 sections. 1, 2, 3 each 12 minutes
    private bool isExperimentStarted = false;
    public float timestamp;

    private bool isPaused = false;

    void Start()
    {
        experimentPartNumber = 1;
    }


    void Update()

    {
        CheckBreakTimes();
        UpdateHeadRotation();
    }

    private void UpdateHeadRotation()
    {
        Vector3 rot = centerEyeAnchorTransform.localEulerAngles;

        // Convert 0-360 range to -180 to 180 range
        float x = (rot.x > 180) ? rot.x - 360 : rot.x;
        float y = (rot.y > 180) ? rot.y - 360 : rot.y;
        float z = (rot.z > 180) ? rot.z - 360 : rot.z;

        Debug.Log($"Inspector-like Rotation: X:{x}, Y:{y}, Z:{z}");
    }


    /// <summary>
    /// Checks the interval number and pauses the game for the breaks
    /// </summary>
    private void CheckBreakTimes()
    {
        if (experimentPartNumber == 1 && dynamicObstacleSpawner.intervalNumber > 2) //72
        {
            EditorApplication.isPaused = true;
            experimentPartNumber = 2;
        }
        else if (experimentPartNumber == 2 && dynamicObstacleSpawner.intervalNumber > 4) // 144
        {
            EditorApplication.isPaused = true;
            experimentPartNumber = 3;
        }

        else if (experimentPartNumber == 3 && dynamicObstacleSpawner.intervalNumber > 6) // 216
        {
            Time.timeScale = 0f;
            Application.Quit();
        }
    }
}