using UnityEngine;

public class MyGameManager : MonoBehaviour
{
    [SerializeField]
    private DynamicObstacleSpawner dynamicObstacleSpawner;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (dynamicObstacleSpawner.intervalNumber > 2)
        {
            Time.timeScale = 0f;
            Application.Quit();
        }
    }
}
