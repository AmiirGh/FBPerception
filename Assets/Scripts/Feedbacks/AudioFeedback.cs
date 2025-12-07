 using UnityEngine;
 using System.IO.Ports;
using System;
using System.Threading;
public class AudioFeedback : MonoBehaviour
{
    [SerializeField]
    private DynamicObstacleSpawner dynamicObstacleSpawner;
    SerialPort serial = new SerialPort("COM7", 9600);
    float timer = 0;
    private int prevTrialNumber = -1;
    private int currentTrialNumber = 0;
    void Start()
    {
        
        serial.Open();
        serial.ReadTimeout = 100;
    }

    // Update is called once per frame
    void Update()
    {
        currentTrialNumber = dynamicObstacleSpawner.trialNumber;
        if (currentTrialNumber > prevTrialNumber)
        {
            prevTrialNumber = currentTrialNumber;
            if (serial.IsOpen)
            {
                int level = dynamicObstacleSpawner.level;
                int degree = dynamicObstacleSpawner.degreeInt;
                string data = level + "," + degree;
                Debug.Log($"dataaa: {data}");
                serial.WriteLine(data);
            }
        }

    }
    private void OnApplicationQuit()
    {
        serial.Close();
    }
   
}
