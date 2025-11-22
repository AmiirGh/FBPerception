using UnityEngine;

public class VisualFeedbackCircle : MonoBehaviour
{

    public VisualFeedback visualFeedback;
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        transform.position = visualFeedback.circlePosition;
    }
}
