using UnityEngine;

public class VisualFeedback : MonoBehaviour
{
    public DynamicObstacleSpawner dynamicObstacleSpawner;
    public Vector3 circlePosition = new Vector3(0,0,0);
    [SerializeField]
    private Transform UVATransform;
    [SerializeField]
    private GameObject circle;
    [SerializeField]
    private GameObject feedbackPlane;


    private Vector3 positionOffset = new Vector3(0, 0, 7.1f);
    public float multiplier = 0.5f;

    void Start()
    {
    }

    // Update is called once per frame
    void Update()
    {
        transform.position = UVATransform.position + positionOffset;
        circle.transform.position = new Vector3(multiplier*dynamicObstacleSpawner.dynamicObstaclePos.x, 0.0f, transform.position.z);
        feedbackPlane.transform.position = transform.position;
        

    }
}
