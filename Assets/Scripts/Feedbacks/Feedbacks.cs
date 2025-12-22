using UnityEngine;

public class Feedbacks : MonoBehaviour
{
    [SerializeField] DynamicObstacleSpawner dynamicObstacleSpawner;
    private int prevIntervalNumber;
    private int prevTrialNumber;
    public int extraFbModality; // extra means other than visual
    void Start()
    {
        
    }


    // Update is called once per frame
    void Update()
    {
        if (IsNewTrialStarted())
        {
            extraFbModality = UnityEngine.Random.Range((int)FbModality.audio, (int)FbModality.haptic+1); // V: 1, A: 2, H:3   So this random generates a feeddback between audio and haptic
            //extraFbModality = 2;
        }
    }

    /// <summary>
    /// Simply checks if a new trial is started
    /// </summary>
    /// <returns></returns>
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


    public enum FbModality
    {
        visual = 1,
        audio = 2,
        haptic = 3
    }
}
