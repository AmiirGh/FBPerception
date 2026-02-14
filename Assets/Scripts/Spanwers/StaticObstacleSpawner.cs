using UnityEngine;
using UnityEngine.UIElements;

public class StaticObstacleSpawner : MonoBehaviour
{

    [SerializeField] private GameObject staticObstacle;

    [SerializeField] private Transform cameraTransform;

    [SerializeField] private UVAMovementController uVAMovementController;
    [SerializeField] private MyGameManager myGameManager;
    private float timer = 0.0f;
    public Vector3 staticObstaclePos = new Vector3(0, 0, 0);
    private int cnt = 0;

    private float xRange = 0.0f;
    private float yRange = 0.0f;

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
        if (timer >= (1 / myGameManager.generationRate)) {
            timer = 0;
            GenerateStaticObstacle(myGameManager.sObstacleGenExactOnPlayerProb);
        }
    }

    /// <summary>
    /// every 1/(generationRate) seconds, generates then destroys the static obstacles
    /// </summary>
    private void GenerateStaticObstacle(float sObstacleGenExactOnUvaProb)
    {
        float eps = Random.Range(0f, 1f);
        if (eps < sObstacleGenExactOnUvaProb)
        { // generate with the same x y as the uva
            staticObstaclePos = new Vector3(cameraTransform.position.x, cameraTransform.position.y+1.0f, cameraTransform.position.z + 25.0f);
        }
        else
        { // generate in random position
            staticObstaclePos = new Vector3(Random.Range(-xRange, xRange), Random.Range(-yRange, yRange), cameraTransform.position.z + 25.0f);
        }
        
        obstacleInstantiated = Instantiate(staticObstacle, staticObstaclePos, Quaternion.identity);
        Destroy(obstacleInstantiated, 3f);
    }
}
