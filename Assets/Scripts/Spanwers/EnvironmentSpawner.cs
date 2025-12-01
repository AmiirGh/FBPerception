using UnityEngine;

public class EnvironmentSpawner : MonoBehaviour
{
    [SerializeField] private GameObject environment;
    [SerializeField] private Transform UVATransform;
    private int environmentCnt;
    private float environmentLength = 420.0f;
    void Start()
    {
        environmentCnt = 1;
    }

    // Update is called once per frame
    void Update()
    {
        
        GenerateEnvironment();
    }

    /// <summary>
    /// Checks the position of the uva and always has generated 2 envs ahead.
    /// </summary>
    void GenerateEnvironment()
    {
        float uVAPosZ = UVATransform.position.z;
        if (uVAPosZ > (environmentCnt - 1) * environmentLength)
        {
            Vector3 floorPos = new Vector3(0, -12, (environmentCnt + 0.5f) * environmentLength);
            GameObject floorInstantiated = Instantiate(environment, floorPos, Quaternion.identity);
            Destroy(floorInstantiated, 100.0f);
            environmentCnt++;
        }
    }
}
