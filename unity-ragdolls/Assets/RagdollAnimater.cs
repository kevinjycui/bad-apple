using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RagdollAnimater : MonoBehaviour
{
    private const float spawnMagnitude = Global.spawnMagnitude;

    private const float xMin = Global.xMin;
    private const float zMin = Global.zMin;

    private const float xMax = Global.xMax;
    private const float zMax = Global.zMax;

    private float width;
    private float height;

    private List<GameObject> [,] screenMap;

    private const float startTime = 60 + 45 + 0.39f;
    private bool started = false;

    private List<List<List<int>>> animData;
    private int animIndex = 0;

    private float lastAnimTime;
    private const float fps = 138f/150 * 1f/20;

    public static List<List<List<int>>> ImportJson(string path)
    {
        TextAsset textAsset = Resources.Load(path) as TextAsset;
        return JsonConvert.DeserializeObject<List<List<List<int>>>>(textAsset.ToString());
    }

    void Start()
    {
        animData = ImportJson("data");
        width = animData[0][0].Count;
        height = animData[0].Count;
        screenMap = new List<GameObject>[(int) width, (int) height];
        for (int i=0; i<width; i++)
            for (int j=0; j<height; j++)
                screenMap[i,j] = new List<GameObject>();
        lastAnimTime = Time.time;
    }

    void InitScreen() {
        foreach (GameObject instance in Cloner.instances) {
            float x = instance.transform.position.x;
            float z = instance.transform.position.z;
            int i = Math.Min((int) width-1, Math.Max(0, (int) ((x - xMin) * width / (xMax - xMin))));
            int j = Math.Min((int) height-1, Math.Max(0, (int) (height - ((z - zMin) * height / (zMax - zMin)))));
            screenMap[i, j].Add(instance);
        }
        Debug.Log("Bad!");
        // string s = "";
        // for (float j=0; j<height; j++) {
        //     for (float i=0; i<width; i++) {
        //         s += screenMap[(int) i, (int) j].Count + " ";
        //     }
        //     s += "\n";
        // }
        // Debug.Log(s);
    }

    public void ForceStart()
    {
        InitScreen();
        started = true;
        lastAnimTime = Time.time;
    }

    void Update()
    {
        if (!started && Time.time >= startTime) {
            InitScreen();
            started = true;
            lastAnimTime = Time.time;
        }
        else if (started && animIndex < animData.Count && Time.time - lastAnimTime >= fps) {
            List<List<int>> frame = animData[animIndex];
            // string s = "";
            for (float j=0; j<height; j++) {
                for (float i=0; i<width; i++) {
                    foreach (GameObject instance in screenMap[(int) i, (int) j])
                        instance.SetActive(frame[(int) (j * frame.Count/height)][(int) (i * frame[0].Count/width)] == 1);
                    // s += screenMap[(int) i, (int) j].Count > 0 && frame[(int) (j * frame.Count/height)][(int) (i * frame[0].Count/width)] == 1 ? "##" : "  ";
                }
                // s += "\n";
            }
            // Debug.Log(s);
            animIndex++;
            lastAnimTime = Time.time;
        }
    }
}
