using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;

public class Cloner : MonoBehaviour {

    [SerializeField]
    private GameObject prefab = null;

    public static List<GameObject> instances = new List<GameObject>();

    private Vector3 startingPos = new Vector3(0, 10, 0);

    private float elapsedTimeSpawn;

    private float xOffset;
    private float zOffset;

    private bool spawnComplete = false;
    private int spawnDirection = 1;
    private const float spawnMagnitude = Global.spawnMagnitude;

    private const float xMin = Global.xMin;
    private const float zMin = Global.zMin;

    private const float xMax = Global.xMax;
    private const float zMax = Global.zMax;

    private float interval = 1f;

    private float spawnCompleteTime;
    private const float spawnToPanTime = 3f;
    private bool readyPan = false;

    void Start()
    {   
        xOffset = xMin;
        zOffset = zMin;

        elapsedTimeSpawn = Time.time;
    }

    void CollapseDancingShinji()
    {
        GameObject target = GameObject.Find("hiphop_shinji");
        GameObject.Instantiate(prefab, target.transform.position, target.transform.rotation * Quaternion.AngleAxis(180, target.transform.up));
        GameObject.Destroy(target);
    }

    void CompleteSpawn()
    {
        spawnComplete = true;
        CollapseDancingShinji();
        spawnCompleteTime = Time.time;
        readyPan = true;
    }

    void Update()
    {
        if (Input.GetKeyUp("space"))
        {
            for (; xOffset > xMin && xOffset < xMax; xOffset += spawnDirection * spawnMagnitude)
                instances.Add(GameObject.Instantiate(prefab, startingPos + new Vector3(xOffset, 0, zOffset), Random.rotation));
            for (; zOffset < zMax; zOffset += spawnMagnitude)
                for (xOffset = xMin; xOffset < xMax; xOffset += spawnMagnitude)
                    instances.Add(GameObject.Instantiate(prefab, startingPos + new Vector3(xOffset, 0, zOffset), Random.rotation));
            CompleteSpawn();
            Camera.main.GetComponent<RagdollAnimater>().ForceStart();
            return;
        }

        if (!spawnComplete && Time.time - elapsedTimeSpawn >= interval) {
            GameObject clone = GameObject.Instantiate(prefab, startingPos + new Vector3(xOffset, 0, zOffset), Random.rotation);
            instances.Add(clone);
            if ((spawnDirection > 0 && xOffset + spawnDirection * spawnMagnitude > xMax) || 
                            (spawnDirection < 0 && xOffset + spawnDirection * spawnMagnitude < xMin)) {
                if (zOffset + spawnMagnitude > zMax) {
                    CompleteSpawn();
                    return;
                }
                zOffset += spawnMagnitude;
                spawnDirection = -spawnDirection;
                interval /= 2f;
            }
            else xOffset += spawnDirection * spawnMagnitude;
            elapsedTimeSpawn = Time.time;
        }

        if (readyPan && Time.time - spawnCompleteTime > spawnToPanTime) {
            Camera.main.GetComponent<CameraPan>().BeginPan();
            readyPan = false;
        }
    }
}
