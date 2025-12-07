 using UnityEngine;
 using System.IO.Ports;
using System;
public class AudioFeedback : MonoBehaviour
{
    [SerializeField]
    private DynamicObstacleSpawner dynamicObstacleSpawner;
    SerialPort serial = new SerialPort("COM7", 9600);
    void Start()
    {
        serial.Open();
        serial.ReadTimeout = 100;
    }

    // Update is called once per frame
    void Update()
    {
        if (serial.IsOpen)
        {
            int level = dynamicObstacleSpawner.level;
            string test = level.ToString();
            serial.Write(test);
            Debug.Log($"sentLevel {test}");

        }

    }
    private void OnApplicationQuit()
    {
        serial.Close();
    }
   
}
