using System.Collections.Generic;
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
    private List<float> feedbackRadii = new List<float> { 1.06f, 1.53f, 2.0f};

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
        int level =  dynamicObstacleSpawner.level;
        float frd = feedbackRadii[level];
        if (level == 0 || level == 1)
        {
            Debug.Log(" ");
        }
        circle.transform.position = new Vector3(frd * Mathf.Cos(degree) + visFbPos.x,
                                                transform.position.y,
                                                frd * Mathf.Sin(degree) + visFbPos.z);


        feedbackPlane.transform.position = visFbPos;
        

    }
}
