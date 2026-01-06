using UnityEngine;

public class StaticObstacleSpawner : MonoBehaviour
{
    [SerializeField]
    private GameObject staticObstacle;
    [SerializeField]
    private Transform UVATransform;
    [SerializeField]
    private UVAMovementController uVAMovementController;
    private float timer = 0.0f;
    public Vector3 staticObstaclePos = new Vector3(0, 0, 0);
    private int cnt = 0;

    private float xRange = 0.0f;
    private float yRange = 0.0f;
    private float generationRate = 15f;
    private GameObject obstacleInstantiated;
    void Start()
    {
        xRange = 1.1f *  uVAMovementController.xRange;
        yRange = 1.1f * uVAMovementController.yRange;
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
        staticObstaclePos = new Vector3(Random.Range(-xRange, xRange), Random.Range(-yRange, yRange), UVATransform.position.z + 25.0f);
        if(staticObstaclePos.x < -6.0f & Mathf.Abs(staticObstaclePos.y) > 6.0f)
        {
            Debug.Log("x more than 6");
        }
        obstacleInstantiated = Instantiate(staticObstacle, staticObstaclePos, Quaternion.identity);
        Destroy(obstacleInstantiated, 3f);
    }
}
