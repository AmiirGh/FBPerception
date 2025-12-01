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


    public Vector3 posOffset = new Vector3(0, -3f, 5.4f);
    public float multiplier = 0.5f;

    void Start()
    {
    }

    void Update()
    {
        Vector3 dynaObsPos = dynamicObstacleSpawner.dynamicObstaclePos;
        Vector3 uvaPos = UVATransform.position;
        transform.position = uvaPos + posOffset;
        Vector3 visFbPos = transform.position;
        Vector3 circlePos = new Vector3(multiplier * (dynaObsPos.x - uvaPos.x) + visFbPos.x,
                                                 visFbPos.y,
                                                 multiplier * (dynaObsPos.z) + visFbPos.z);

        float degree = dynamicObstacleSpawner.degree;
        float distanceRadius = 4.0f / 2; // This is the scale of the visual feedback Plane devided by 2
        circle.transform.position = new Vector3(distanceRadius * Mathf.Cos(degree) + transform.position.x,
                                             transform.position.y,
                                             distanceRadius * Mathf.Sin(degree) + visFbPos.z);


        feedbackPlane.transform.position = visFbPos;
        

    }
}
