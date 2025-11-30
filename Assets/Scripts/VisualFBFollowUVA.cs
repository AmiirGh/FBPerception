using UnityEngine;

public class VisualFBFollowUVA : MonoBehaviour
{
    [SerializeField]
    private Transform UVATransform;
    private Vector3 positionOffset = new Vector3(0, 0, 7.1f);
    
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        transform.position = UVATransform.position + positionOffset;
    }
}
