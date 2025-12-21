using UnityEngine;

public class Feedbacks : MonoBehaviour
{
    [SerializeField] DynamicObstacleSpawner dynamicObstacleSpawner;
    private int prevIntervalNumber;
    private int prevTriallNumber;
    public int extraFbModality; // extra means other than visual
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (IsNewTrialStarted())
        {
            extraFbModality = UnityEngine.Random.Range(1, 3); // V: 1, A: 2, H:3   So this random generates a feeddback between audio and haptic
            
           
        }
    }

    private bool IsNewTrialStarted()
    {
        if (prevTriallNumber < dynamicObstacleSpawner.trialNumber)
        {
            prevTriallNumber = dynamicObstacleSpawner.trialNumber;
            return true;
        }
        else 
            return false;
    }
}
