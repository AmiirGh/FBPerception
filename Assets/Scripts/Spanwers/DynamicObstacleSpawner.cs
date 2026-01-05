using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public class DynamicObstacleSpawner : MonoBehaviour
{
    [SerializeField]
    private GameObject dynamicObstacle;
    [SerializeField]
    private Transform UVATransform;

    public float degreeRad = 0; // degree in radian (0, 2*pi)
    public float degreeDeg = 0; // degree in degree (0,360)
    public int degreeInt = 0;
    public int level = 0;
    public int degree = 0;
    private GameObject currentDynamicObstacle;
    public Vector3 dynamicObstaclePos = new Vector3(0, 0, 0);
    private float timer = 0;
    public int trialNumber = 0; // Is ++ when a new obstacle is generated
    public int intervalNumber = 0; // is ++ when a new interval (after intervalDuration time) is started
    private float distanceRadius = 10.0f;
    private List<float> distanceRadii = new List<float> { 4, 8, 12 };
    public bool isDynamicObstaclePresent = false;
    public float dynamicObstaclePresenceDuration;
    private float intervalDuration = 10.0f;

    public enum ditances
    {
        near = 1,
        mid = 2,
        far = 3,
        invalid = 4
    }

    [System.Serializable]
    public class TrialData
    {
        public int degree;
        public string feedbackModality;
        public string level;
    }
    public List<TrialData> allTrials = new List<TrialData>();
    void Start()
    {
        dynamicObstaclePresenceDuration = 2.0f;
        string inputFileName = "unshuffled_patterns.csv";
        string outputFileName = "shuffled_patterns.csv";

        string inputPath = Path.Combine(Application.dataPath, inputFileName);
        string outputPath = Path.Combine(Application.dataPath, outputFileName);


        if (ReadCSV(inputPath))
        {
            ShuffleTrials();

            WriteCSV(outputPath);

            if (allTrials.Count >= 10)
            {
                Debug.Log($"<color=green>New 10th Row (Shuffled):</color> {allTrials[9].degree}, {allTrials[9].feedbackModality}, {allTrials[9].level}");
            }
        }
    }

    void Update()
    {
        timer += Time.deltaTime;
        if (timer >= intervalDuration)
        {

            StartCoroutine(GenerateNewInterval());
            timer = 0;
            intervalNumber++;
        }
        if(!isDynamicObstaclePresent)
        {
            degree = 0;
            level = 0;
        }
    }
    void LateUpdate()
    {
        if (currentDynamicObstacle != null)
        {
            currentDynamicObstacle.transform.position = UVATransform.position + new Vector3(dynamicObstaclePos.x, 0, dynamicObstaclePos.z);
        }
    }

    /// <summary>
    /// This  method starts a new interval (every intervalDuration seconds)
    /// then generates a random number to randomize the time when a new dynamic obstacle is actually generated.
    /// </summary>
    /// <returns></returns>
    IEnumerator GenerateNewInterval()
    {
        float spawnAfter = UnityEngine.Random.Range(0.0f, 4.0f);
        yield return new WaitForSeconds(spawnAfter);
        GenerateDynamicObstacle();
        trialNumber++;
        isDynamicObstaclePresent = true;
        yield return new WaitForSeconds(dynamicObstaclePresenceDuration);
        if (currentDynamicObstacle != null) Destroy(currentDynamicObstacle);
        isDynamicObstaclePresent = false;
    } 

    /// <summary>
    /// Spawns dynamic obstacle
    /// </summary>
    void GenerateDynamicObstacle()
    {
        (level, degree) = GetDegreeLevel();
        dynamicObstaclePos = new Vector3(distanceRadii[level-1] * Mathf.Cos(DegreeToRad(degree)),
                                         UVATransform.position.y,
                                         distanceRadii[level-1] * Mathf.Sin(DegreeToRad(degree)));
        currentDynamicObstacle = Instantiate(dynamicObstacle, UVATransform.position, Quaternion.identity);
    }


    public float DegreeToRad(int degree)
    {
        float rad = 0;
        if (degree == 1)      rad = 2 * Mathf.PI / 4;
        else if (degree == 2) rad = 1 * Mathf.PI / 4;
        else if (degree == 3) rad = 0 * Mathf.PI / 4;
        else if (degree == 4) rad = 7 * Mathf.PI / 4;
        else if (degree == 5) rad = 6 * Mathf.PI / 4;
        else if (degree == 6) rad = 5 * Mathf.PI / 4;
        else if (degree == 7) rad = 4 * Mathf.PI / 4;
        else if (degree == 8) rad = 3 * Mathf.PI / 4;
        return rad;
    }


    /// <summary>
    /// based on the trial number, returns the degree, level
    /// </summary>
    /// <returns></returns>
    Tuple<int, int> GetDegreeLevel()
    {
        int level = (int)ditances.invalid;
        if      (allTrials[intervalNumber-1].level == "far")  level = (int)ditances.far;
        else if (allTrials[intervalNumber-1].level == "mid")  level = (int)ditances.mid;
        else if (allTrials[intervalNumber-1].level == "near") level = (int)ditances.near;
        int degree = allTrials[intervalNumber-1].degree;
        string fbModality = allTrials[intervalNumber - 1].feedbackModality;
        return Tuple.Create(level, degree);
    }




    /// <summary>
    /// returns random values for degree (pi/4, pi/2, 3pi/4, ...) and level (1, 2, 3)
    /// This method is deprecated since now the degrees and values are generated using the allTrials
    /// </summary>
    /// <returns></returns>
    Tuple<int, float, float, int> GetDegreeLevel_Old()
    {
        int degreeInFuncInt = UnityEngine.Random.Range(0, 8);
        float degreeInFuncDeg = degreeInFuncInt * 45.0f; // in degree
        float degreeInFuncRad = Mathf.PI / 4 * degreeInFuncInt; // in radians
        int levelInFunc = UnityEngine.Random.Range(0, 3);
        Debug.Log($"LevelFunc: {levelInFunc}");
        return Tuple.Create(degreeInFuncInt, degreeInFuncRad, degreeInFuncDeg, levelInFunc);
    }


    /// <summary>
    /// Reads the unshuffled patterns (3*3*8*3 rows)
    /// </summary>
    /// <param name="path"></param>
    /// <returns>if it could read succesfully</returns>
    ///

    bool ReadCSV(string path)
    {
        if (!File.Exists(path))
        {
            Debug.LogError("Could not find file at: " + path);
            return false;
        }

        string[] lines = File.ReadAllLines(path);
        allTrials.Clear();
        for (int i = 1; i < lines.Length; i++)
        {
            if (string.IsNullOrWhiteSpace(lines[i])) continue;

            string[] cells = lines[i].Split(',');

            TrialData newTrial = new TrialData();
            newTrial.degree = int.Parse(cells[0]);
            newTrial.feedbackModality = cells[1];
            newTrial.level = cells[2];

            allTrials.Add(newTrial);
        }
        Debug.Log($"Read {allTrials.Count} rows from {path}");
        return true;
    }

    /// <summary>
    /// Shuffles the data immediately after run
    /// </summary>
    void ShuffleTrials()
    {
        for (int i = 0; i < allTrials.Count; i++)
        {
            TrialData temp = allTrials[i];
            int randomIndex = UnityEngine.Random.Range(i, allTrials.Count);
            allTrials[i] = allTrials[randomIndex];
            allTrials[randomIndex] = temp;
        }
        Debug.Log("Data has been shuffled.");
    }
    /// <summary>
    /// After shuffling, writes the values on a new CSV file. and saves the shuffled data on allTrial. From now on, ONLY allTrials are used
    /// </summary>
    /// <param name="path"></param>
    void WriteCSV(string path)
    {
        using (StreamWriter writer = new StreamWriter(path))
        {
            writer.WriteLine("Degree,Feedback_Modality,Level");

            foreach (TrialData trial in allTrials)
            {
                string line = $"{trial.degree},{trial.feedbackModality},{trial.level}";
                writer.WriteLine(line);
            }
        }
        Debug.Log($"Successfully created shuffled file at: {path}");
    }

}
