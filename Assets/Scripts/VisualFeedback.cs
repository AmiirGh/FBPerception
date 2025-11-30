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

    // Update is called once per frame
    void Update()
    {
        Vector3 dynaObsPos = dynamicObstacleSpawner.dynamicObstaclePos;
        Vector3 uvaPos = UVATransform.position;
        transform.position = uvaPos + posOffset;
        Debug.Log($"pos uvaPos: {uvaPos}");
        Debug.Log($"pos VisualPos: {transform.position}");

        Vector3 visFbPos = transform.position;
        Debug.Log($"pos visFbPos: {visFbPos}");
        Debug.Log($"pos dynaObsPos: {dynaObsPos}");
        Vector3 circlePos = new Vector3(multiplier * (dynaObsPos.x - uvaPos.x) + visFbPos.x,
                                                 visFbPos.y,
                                                 multiplier * (dynaObsPos.z) + visFbPos.z);
        //circle.transform.position = circlePos;
        Debug.Log($"pos circlePos: {circlePos}");

        int degree = dynamicObstacleSpawner.degree;
        float distanceRadius = 4.0f / 2; // This is the scale of the visual feedback Plane
        circle.transform.position = new Vector3(distanceRadius * Mathf.Cos(degree * Mathf.PI / 180.0f) + transform.position.x,
                                             transform.position.y,
                                             distanceRadius * Mathf.Sin(degree * Mathf.PI / 180.0f) + visFbPos.z);


        feedbackPlane.transform.position = visFbPos;
        

    }
}
