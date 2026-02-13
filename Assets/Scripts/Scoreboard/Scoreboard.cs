using UnityEngine;
using TMPro;

public class Scoreboard : MonoBehaviour
{
    [SerializeField] private Transform UVATransform;
    [SerializeField] private CollisionDetector collisionDetector;
    public Vector3 scoreboardPositionOffset;
    public TMP_Text scoreboard;

    void Start()
    {
        scoreboardPositionOffset = new Vector3(-1.7f, 3.55f, 8.21f);
    }

    // Update is called once per frame
    void Update()
    {
        transform.position  = UVATransform.position + scoreboardPositionOffset;
        scoreboard.text = $"Collisions: {collisionDetector.numberOfCollision}";
    }
}
