using UnityEngine;

public class CollisionDetector : MonoBehaviour
{
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    public int numberOfCollision = 0;
    public Vector3 collisionPosition = new Vector3(0, 0, 0);
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
    private void OnTriggerEnter(Collider other)
    {
        Debug.Log($"hitCount: {numberOfCollision}");
        if (other.gameObject.tag == "StaticObstacle")
        {
            numberOfCollision++;
            Debug.Log($"hitCount: {numberOfCollision}");
            collisionPosition = other.gameObject.transform.position;
        }
    }
}
