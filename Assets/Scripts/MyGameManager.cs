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
    public int experimentPhase = 0; // Experiment has 3 phases. each 12 minutes
    private bool isExperimentStarted = false;
    public float timestamp;
    public float generationRate = 0; // static obstacle generation rate per second
    public float forwardSpeed = 0; // the uva forward speed in z direction
    public float sObstacleGenExactOnPlayerProb = 0; // The probability to generate the static obstacles at the exact player x,y
    private bool isPaused = false;

    private int experimentType = 0; // Experiment types are range from 1 to 6.  1: easy,hard,expert | 2: hard,easy,expert | ... | 3: expert,hard,easy

    void Start()
    {
        experimentPhase = 0;
        experimentType = 1; // 1 or 2 or 3 or ... or 6. Change this number before each participant starts.
        //sObstacleGenExactOnUvaProb = 0.1f;

    }


    void Update()
    {
        CheckBreakTimes();
        UpdateHeadRotation();
        Debug.Log($"Int nu: {dynamicObstacleSpawner.intervalNumber}, Type:{experimentType}, Phase:{experimentPhase}, forspeed: {forwardSpeed}, genrate: {generationRate}, Genonplayerprob: {sObstacleGenExactOnPlayerProb}");
    }

    private void UpdateHeadRotation()
    {
        Vector3 rot = centerEyeAnchorTransform.localEulerAngles;

        // Convert 0-360 range to -180 to 180 range
        float x = (rot.x > 180) ? rot.x - 360 : rot.x;
        float y = (rot.y > 180) ? rot.y - 360 : rot.y;
        float z = (rot.z > 180) ? rot.z - 360 : rot.z;
    }


    /// <summary>
    /// Checks the interval number and pauses the game for the breaks
    /// </summary>
    private void CheckBreakTimes()
    {
        if (experimentPhase == 0)
        {
            experimentPhase = 1;
            (forwardSpeed, generationRate, sObstacleGenExactOnPlayerProb) = GetGenerationRateForwardSpeed(experimentType, experimentPhase);
        }

        else if (experimentPhase == 1 && dynamicObstacleSpawner.intervalNumber > 72) //72
        {
            EditorApplication.isPaused = true;
            experimentPhase = 2;
            (forwardSpeed, generationRate, sObstacleGenExactOnPlayerProb) = GetGenerationRateForwardSpeed(experimentType, experimentPhase);
        }
        else if (experimentPhase == 2 && dynamicObstacleSpawner.intervalNumber > 144) // 144
        {
            EditorApplication.isPaused = true;
            experimentPhase = 3;
            (forwardSpeed, generationRate, sObstacleGenExactOnPlayerProb) = GetGenerationRateForwardSpeed(experimentType, experimentPhase);
        }

        else if (experimentPhase == 3 && dynamicObstacleSpawner.intervalNumber > 216) // 216
        {
            Time.timeScale = 0f;
            Application.Quit();
        }
    }

    /// <summary>
    /// based on the experient type (the order of the easy, hard, expert modes)
    /// </summary>
    /// <param name="experimentType"></param>  indicates the order of the easy, hard, expert which adds up t0 6 types
    /// <param name="experimentPhase"></param> indicates the phase which we have 3, each 12 minutes
    /// <returns>forwardSpeed & generationRate</returns>
    Tuple<float, float, float> GetGenerationRateForwardSpeed(int experimentType, int experimentPhase)
    {
        Tuple<float, float, float> genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.invalid, (float)generationRates.invalid, (float)sObstacleGenExactOnUvaProbs.invalid); // genration rate and forward speed tuple

        if (experimentType == 1)
        { // easy, hard, expert
            if      (experimentPhase == 1) genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.easy, (float)generationRates.easy, (float)(int)sObstacleGenExactOnUvaProbs.easy / 1000);
            else if (experimentPhase == 2) genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.hard, (float)generationRates.hard, (float)(int)sObstacleGenExactOnUvaProbs.hard / 1000);
            else if (experimentPhase == 3) genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.expert, (float)generationRates.expert, (float)(int)sObstacleGenExactOnUvaProbs.expert / 1000);
            else                           genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.invalid, (float)generationRates.invalid, (float)(int)sObstacleGenExactOnUvaProbs.invalid / 1000);
        }
        else if (experimentType == 2)
        { // hard, easy, expert
            if      (experimentPhase == 1) genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.hard, (float)generationRates.hard, (float)(int)sObstacleGenExactOnUvaProbs.hard / 1000);
            else if (experimentPhase == 2) genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.easy, (float)generationRates.easy, (float)(int)sObstacleGenExactOnUvaProbs.easy / 1000);
            else if (experimentPhase == 3) genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.expert, (float)generationRates.expert, (float)(int)sObstacleGenExactOnUvaProbs.expert / 1000);
            else                           genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.invalid, (float)generationRates.invalid, (float)(int)sObstacleGenExactOnUvaProbs.invalid / 1000);
        }
        else if (experimentType == 3)
        { // expert, hard, easy
            if      (experimentPhase == 1) genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.expert, (float)generationRates.expert, (float)(int)sObstacleGenExactOnUvaProbs.expert / 1000);
            else if (experimentPhase == 2) genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.hard, (float)generationRates.hard, (float)(int)sObstacleGenExactOnUvaProbs.hard / 1000);
            else if (experimentPhase == 3) genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.easy, (float)generationRates.easy, (float)(int)sObstacleGenExactOnUvaProbs.easy / 1000);
            else                           genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.invalid, (float)generationRates.invalid, (float)(int)sObstacleGenExactOnUvaProbs.invalid / 1000);
        }
        else if (experimentType == 4)
        { // easy, expert, hard
            if      (experimentPhase == 1) genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.easy, (float)generationRates.easy, (float)(int)sObstacleGenExactOnUvaProbs.easy / 1000);
            else if (experimentPhase == 2) genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.expert, (float)generationRates.expert, (float)(int)sObstacleGenExactOnUvaProbs.expert / 1000);
            else if (experimentPhase == 3) genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.hard, (float)generationRates.hard, (float)(int)sObstacleGenExactOnUvaProbs.hard / 1000);
            else                           genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.invalid, (float)generationRates.invalid, (float)(int)sObstacleGenExactOnUvaProbs.invalid / 1000);
        }
        else if (experimentType == 5)
        { // hard, expert, easy
            if      (experimentPhase == 1) genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.hard, (float)generationRates.hard, (float)(int)sObstacleGenExactOnUvaProbs.hard / 1000);
            else if (experimentPhase == 2) genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.expert, (float)generationRates.expert, (float)(int)sObstacleGenExactOnUvaProbs.expert / 1000);
            else if (experimentPhase == 3) genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.easy, (float)generationRates.easy, (float)(int)sObstacleGenExactOnUvaProbs.easy / 1000);
            else                           genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.invalid, (float)generationRates.invalid, (float)(int)sObstacleGenExactOnUvaProbs.invalid / 1000);
        }
        else if (experimentType == 6)
        { // expert, easy, hard
            if      (experimentPhase == 1) genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.expert, (float)generationRates.expert, (float)(int)sObstacleGenExactOnUvaProbs.expert / 1000);
            else if (experimentPhase == 2) genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.easy, (float)generationRates.easy, (float)(int)sObstacleGenExactOnUvaProbs.easy / 1000);
            else if (experimentPhase == 3) genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.hard, (float)generationRates.hard, (float)(int)sObstacleGenExactOnUvaProbs.hard / 1000);
            else                           genrateForspeedGenonplayerprob = Tuple.Create((float)forwardSpeeds.invalid, (float)generationRates.invalid, (float)(int)sObstacleGenExactOnUvaProbs.invalid / 1000);
        }

        return genrateForspeedGenonplayerprob;
    }
    
    public enum forwardSpeeds
    {
        easy = 15,
        hard = 23,
        expert = 30,
        invalid = 0
    }
    public enum generationRates
    {
        easy = 15,
        hard = 23,
        expert = 30,
        invalid = 0
    }

    public enum sObstacleGenExactOnUvaProbs
    { // it will be devided by 1000
        easy = 50,
        hard = 60,
        expert = 70,
        invalid = 0
    }

}