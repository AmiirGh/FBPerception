using UnityEngine;

public class Feedbacks : MonoBehaviour
{
    [SerializeField] DynamicObstacleSpawner dynamicObstacleSpawner;
    private int prevIntervalNumber;
    private int prevTrialNumber;
    public string feedbackModality; // extra means other than visual
    void Start()
    {
        
    }


    // Update is called once per frame
    void Update()
    {
        if (IsNewTrialStarted())
        {
            int fbModality = UnityEngine.Random.Range((int)FbModality.visual, (int)FbModality.haptic+1); // V: 1, A: 2, H:3   So this random generates a feeddback between audio and haptic
            switch (fbModality)
            {
                case 1:
                    feedbackModality = "visual";
                    break;
                case 2:
                    feedbackModality = "audio";
                    break;
                case 3:
                    feedbackModality = "haptic";
                    break;
                default:
                    feedbackModality = "-";
                    break;
            }
            Debug.Log($"feedback modality {feedbackModality}");
        }
        else 
        {
            if (dynamicObstacleSpawner.isDynamicObstaclePresent)
            {
                //do nothing
            }
            else
            {
                feedbackModality = "-";
            }
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
