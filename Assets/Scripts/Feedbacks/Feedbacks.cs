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
            //int fbModality = UnityEngine.Random.Range((int)FbModality.visual, (int)FbModality.haptic+1); // V: 1, A: 2, H:3   So this random generates a feeddback between audio and haptic
            int fbModality = GetFeedbackModality();

            //fbModality = (int)FbModality.visual;
            if (dynamicObstacleSpawner.isDynamicObstaclePresent)
            {
                if (fbModality == 1) feedbackModality = "visual";
                else if (fbModality == 2) feedbackModality = "audio";
                else if (fbModality == 3) feedbackModality = "haptic";
                else feedbackModality = "-";
            }
            else feedbackModality = "-";


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
    /// returns feedback modality based on the excel values
    /// </summary>
    /// <returns></returns>
    private int GetFeedbackModality()
    {
        int fbmodality = (int)FbModality.invalid;
        string fbModalityString = dynamicObstacleSpawner.allTrials[dynamicObstacleSpawner.intervalNumber - 1].feedbackModality;
        if      (fbModalityString == "Visual") 
            fbmodality = (int)FbModality.visual;
        else if (fbModalityString == "Audio") 
            fbmodality = (int)FbModality.audio;
        else if (fbModalityString == "Haptic") 
            fbmodality = (int)FbModality.haptic;
        return fbmodality;

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
        haptic = 3,
        invalid = 4
    }
}
