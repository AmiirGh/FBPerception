using UnityEngine;
using System.Net;
using System;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using UnityEngine.SceneManagement;
using System.Linq;
using Unity.VisualScripting;
using static Feedbacks;

public class TCP : MonoBehaviour
{

    private string HOST;
    private int PORT;
    private TcpListener server;
    private TcpClient client;
    private NetworkStream netStream;
    public static int tempFromPCtoHMD = 0;

    [SerializeField] DynamicObstacleSpawner dynamicObstacleSpawner;
    [SerializeField] InputHandler inputHandler;
    [SerializeField] Feedbacks feedbacks;
    [SerializeField] CollisionDetector collisionDetector;

    public string receivedData = string.Empty;
    private float[] sentData;
    public UnityEngine.UI.Text display;
    public static Vector3 position;
    private Vector3 rotation;
    private DateTime startTime;
    private int tempRew = 10;
    private volatile bool isRunning = true;
    private static readonly object scoreLock = new object();

    async void Start()
    {
        HOST = "172.20.10.4";
        PORT = 12345;
        await StartServerAsync();
    }

    void Update()
    {
        position = transform.position;
        rotation = transform.eulerAngles;
    }

    private async Task StartServerAsync()
    {
        try
        {
            server = new TcpListener(IPAddress.Parse(HOST), PORT);
            server.Start();
            Debug.Log($"Server started at {HOST}:{PORT}. Waiting for client...");
            client = await server.AcceptTcpClientAsync();
            netStream = client.GetStream();
            Debug.Log("Client connected.");
            startTime = DateTime.Now;
            _ = ReceiveDataAsync();
            _ = SendDataAsync();
        }
        catch (SocketException ex)
        {
            Debug.LogError($"SocketException: {ex.Message}");
            Cleanup();
        }
    }

    private async Task ReceiveDataAsync()
    {
        try
        {
            byte[] lengthBuffer = new byte[4];

            while (isRunning)
            {
                if (netStream != null && netStream.CanRead)
                {
                    int lengthBytesRead = await netStream.ReadAsync(lengthBuffer, 0, lengthBuffer.Length);
                    if (lengthBytesRead < 4)
                    {
                        break;
                    }

                    int messageLength = BitConverter.ToInt32(lengthBuffer.Reverse().ToArray(), 0);

                    byte[] dataBuffer = new byte[messageLength];
                    int totalBytesRead = 0;

                    while (totalBytesRead < messageLength)
                    {
                        int bytesRead = await netStream.ReadAsync(dataBuffer, totalBytesRead, messageLength - totalBytesRead);
                        if (bytesRead == 0)
                        {
                            break;
                        }
                        totalBytesRead += bytesRead;
                    }

                    if (totalBytesRead == messageLength)
                    {
                        try
                        {
                            string jsonData = Encoding.UTF8.GetString(dataBuffer, 0, totalBytesRead);
                            var receivedJson = JsonConvert.DeserializeObject<ReceivedData>(jsonData);


                            if (receivedJson != null)
                            {

                                tempFromPCtoHMD = receivedJson.tempFromPCtoHMD;
                                Debug.Log($"tempFromPCtoHMD: {tempFromPCtoHMD}");
                            }
                            Debug.Log($"Received JSON: {jsonData}");
                        }
                        catch (JsonException ex)
                        {
                            Debug.LogError($"JSON Decode Error: {ex.Message}");
                        }
                    }
                }
            }
        }
        catch (Exception ex)
        {
            Debug.LogError($"Error in ReceiveDataAsync: {ex.Message}");
        }
    }

    private async Task SendDataAsync()
    {
        //private int tempRew = 10;
        try
        {
            while (isRunning && netStream != null && netStream.CanWrite)
            {
                var dataToSend = new SentData
                {
                    timestamp = (float)Math.Round((DateTime.Now - startTime).TotalSeconds, 5),
                    intervalNumber = dynamicObstacleSpawner.intervalNumber,
                    trialNumber = dynamicObstacleSpawner.trialNumber,
                    isDynamicObstaclePresent = dynamicObstacleSpawner.isDynamicObstaclePresent,
                    degree = dynamicObstacleSpawner.degreeDeg,
                    degreeInt = dynamicObstacleSpawner.degreeInt,
                    level = dynamicObstacleSpawner.level,
                    feedbackModality = feedbacks.feedbackModality,
                    rightIndexButton = inputHandler.rightIndexButton,
                    leftIndexButton = inputHandler.leftIndexButton,
                    rightThumbstickX = inputHandler.rightThumbstick.x,
                    rightThumbstickY = inputHandler.rightThumbstick.y,
                    numberOfCollision = collisionDetector.numberOfCollision,
                };

                string jsonData = JsonConvert.SerializeObject(dataToSend);
                byte[] jsonDataBytes = Encoding.UTF8.GetBytes(jsonData);

                byte[] lengthPrefix = BitConverter.GetBytes(jsonDataBytes.Length);
                Array.Reverse(lengthPrefix);
                await netStream.WriteAsync(lengthPrefix, 0, lengthPrefix.Length);



                await netStream.WriteAsync(jsonDataBytes, 0, jsonDataBytes.Length);
                Debug.Log($"Sent JSON: {jsonData}");
                Debug.Log($"length prefix: {lengthPrefix}");
                await Task.Delay(100);
            }
        }
        catch (Exception ex)
        {
            Debug.LogError($"SendData Exception: {ex.Message}");
        }
    }

    private void Cleanup()
    {
        isRunning = false;
        netStream?.Close();
        client?.Close();
        server?.Stop();
        Debug.Log("Server stopped and resources cleaned up.");
    }

    private void OnDestroy()
    {
        Cleanup();
    }

}

[Serializable]
public class SentData
{
    public float timestamp;
    public int intervalNumber;
    public int trialNumber;
    public bool isDynamicObstaclePresent;
    public float degree;
    public int degreeInt;
    public int level;
    public string feedbackModality;
    public float rightIndexButton;
    public float leftIndexButton;
    public float rightThumbstickX;
    public float rightThumbstickY;
    public int numberOfCollision;

}

[Serializable]
public class ReceivedData
{
    public int tempFromPCtoHMD;
}