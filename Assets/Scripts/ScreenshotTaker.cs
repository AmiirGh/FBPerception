using System.IO;
using UnityEngine;

public class ScreenshotTaker : MonoBehaviour
{
    private int counter = 0;

    void Update()
    {
        if (OVRInput.GetDown(OVRInput.Button.PrimaryIndexTrigger, OVRInput.Controller.RTouch))
        {
            TakeScreenshot();
        }
    }

    void TakeScreenshot()
    {
        string filename = $"Screenshot_{System.DateTime.Now:yyyyMMdd_HHmmss}_{counter++}.png";
        string path;
        path = Path.Combine(Directory.GetCurrentDirectory(), filename);


        ScreenCapture.CaptureScreenshot(path);
        Debug.Log($"Screenshot saved to: {path}");
    }
}
