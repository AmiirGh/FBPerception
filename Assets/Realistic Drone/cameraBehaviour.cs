using UnityEngine;
using System.Collections;

public class cameraBehaviour : MonoBehaviour {

    public Transform followThis;

    public float radius = 10;
    public float angle = 0;

    public float runningSpeed = 5f;
    public float turningSpeed = 5f;
    public float zoomSpeed = 5f;

    public float yOffset = 5f;

    private Vector3 offset = new Vector3(2.0f, 2.0f, 2.0f);



    void Update()
    {
        transform.position = followThis.position + offset;
    }


}
