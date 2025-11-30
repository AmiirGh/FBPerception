using TreeEditor;
using UnityEngine;

public class CameraFollowUva : MonoBehaviour
{
    [SerializeField]
    private Transform UVATransform;
    public Vector3 cameraPositionOffset;
    public Vector3 cameraRotationOffset;

    void Start()
    {
        cameraPositionOffset = new Vector3(0, 0.76f, 0.36f);
        cameraRotationOffset = new Vector3(12.73f, 0, 0);
        transform.Rotate(cameraRotationOffset);
    }

    void LateUpdate()
    {
        transform.position = UVATransform.position + cameraPositionOffset;
    }
}
