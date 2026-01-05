 using UnityEngine;
 using System.IO.Ports;
using System;
using System.Threading;
using static Feedbacks;
using Oculus.Interaction.Locomotion;
using System.Collections;

public class AudioFeedback : MonoBehaviour
{

    [SerializeField] private DynamicObstacleSpawner dynamicObstacleSpawner;

    [SerializeField] private Feedbacks feedbacks;
    SerialPort serial = new SerialPort("COM7", 9600);
    float timer = 0;
    private int prevTrialNumber = -1;
    private int currentTrialNumber = 0;
    void Start()
    {
        
        serial.Open();
        serial.ReadTimeout = 100;
    }

    void Update()
    {
        if (IsNewTrialStarted() && feedbacks.feedbackModality == "audio")
        { // a new trial is started and the fb modality is Audio
            if (dynamicObstacleSpawner.isDynamicObstaclePresent)
            {
                SendAudio();
                StartCoroutine(TurnBuzzersOff());
                
            }
        }
    }

    IEnumerator TurnBuzzersOff()
    {
        yield return new WaitForSeconds(dynamicObstacleSpawner.dynamicObstaclePresenceDuration);
        if (serial.IsOpen) 
        { 
            int level = 4; // invalid level to turn off
            string data = level + "," + dynamicObstacleSpawner.degree;
            serial.WriteLine(data);
        }
    }


    /// <summary>
    /// Sends level and degree so that the audio buzzers work
    /// </summary>
    private void SendAudio()
    {
        if (serial.IsOpen && dynamicObstacleSpawner.isDynamicObstaclePresent)
        { // Serial is open and the dynamic obstacle is now present
            int level = dynamicObstacleSpawner.level;
            float degree = dynamicObstacleSpawner.degree;
            string data = level + "," + degree;
            serial.WriteLine(data);
        }
    }

    public bool IsNewTrialStarted()
    {
        if (prevTrialNumber < dynamicObstacleSpawner.trialNumber)
        {
            prevTrialNumber = dynamicObstacleSpawner.trialNumber;
            return true;
        }
        else
            return false;
    }


    private void OnApplicationQuit()
    {
        serial.Close();
    }


   
}
