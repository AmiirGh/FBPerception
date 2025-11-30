using UnityEngine;

public class StaticObstacleSpawner : MonoBehaviour
{
    [SerializeField]
    private GameObject staticObstacle;
    [SerializeField]
    private Transform UVATransform;
    private float timer = 0.0f;
    public Vector3 staticObstaclePos = new Vector3(0, 0, 0);
    private int cnt = 0;

    private float xRange = 4.0f;
    private float yRange = 4.0f;
    private float generationRate = 5f;
    private GameObject obstacleInstantiated;
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        timer += Time.deltaTime;
        if (timer >= (1 / generationRate)) {
            timer = 0;
            GenerateStaticObstacle();
        }
    }

    /// <summary>
    /// every 1/(generationRate) seconds, generates then destroys the static obstacles
    /// </summary>
    void GenerateStaticObstacle()
    {
        staticObstaclePos = new Vector3(Random.Range(-xRange, xRange), Random.Range(-yRange, yRange), UVATransform.position.z + 20.0f);

        obstacleInstantiated = Instantiate(staticObstacle, staticObstaclePos, Quaternion.identity);
        Destroy(obstacleInstantiated, 5f);
    }
}
