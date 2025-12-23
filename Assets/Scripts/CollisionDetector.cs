using UnityEngine;

public class CollisionDetector : MonoBehaviour
{
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    public int numberOfCollision = 0;
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
    private void OnTriggerEnter(Collider other)
    {
        if (other.gameObject.tag == "StaticObstacle")
        {
            numberOfCollision++;
            Debug.Log($"hitCount: {numberOfCollision}");
        }
    }
}
