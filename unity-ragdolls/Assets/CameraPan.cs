using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraPan : MonoBehaviour
{
    private bool beginPan = false;

    private const float panSpeed = 1f;

    private const float finalY = 8f;
    private const float finalRotX = 80f;

    public void BeginPan()
    {
        beginPan = true;
    }

    void Update()
    {
        if (beginPan) {
            if (transform.position.y < finalY)
                transform.Translate(new Vector3(0, panSpeed * Time.deltaTime, 0), Space.World);
            if (transform.eulerAngles.x < finalRotX) {
                transform.Translate(new Vector3(0, 0, panSpeed * Time.deltaTime), Space.World);
                transform.Rotate(new Vector3(panSpeed * 10 * Time.deltaTime, 0, 0), Space.World);
            }
        }
    }
}
