 using UnityEngine;
 using System.IO.Ports;
using System;
public class AudioFeedback : MonoBehaviour
{
    [SerializeField]
    private DynamicObstacleSpawner dynamicObstacleSpawner;
    SerialPort serial = new SerialPort("COM6", 9600);
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
            // --- Reading ---
            //string data = serial.ReadLine();
            //int val = int.Parse(data);
            //Debug.Log($"port received data: {val}");
            int level = dynamicObstacleSpawner.level;
            serial.Write(level.ToString());

        }

    }
    private void OnApplicationQuit()
    {
        serial.Close();
    }
   
}
