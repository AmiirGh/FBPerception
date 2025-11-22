using UnityEngine;

public class VisualFeedbackPlane : MonoBehaviour
{

    public Transform visualFeedback;
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        transform.position = visualFeedback.position;
    }
}
