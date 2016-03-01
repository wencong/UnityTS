using UnityEngine;
using System;
using System.Collections;
using System.Diagnostics;
using System.Collections.Generic;
using System.Text;

#if UNITY_EDITOR
    using UnityEditor;
#endif

struct SStopWatch
{
    public Stopwatch stopwatch;
    public double startTime;
    //public double endTme;
}

struct SampleData
{
    public string sampleName;
    public string parentSampleName;

    public double startTime;
    public double endTime;

    public double sampleTime;

    //public Stopwatch stopWatch = null;

    override public string ToString()
    {
        return string.Format("{0}:{1:0.00}:{2}:{3:0.00}:{4:0.00};", sampleName, sampleTime, parentSampleName, startTime, endTime);
    }
}

struct SampleDataCrossFrame
{
    public string sampleName;
    //public string parentSampleName;

    public double startTime;
    public double endTime;
    public double sampleTime;

    public int sampleFrames;
    
    public int startFrame;
    public int endFrame;

    public Stopwatch stopwatch;

    override public string ToString()
    {
        return string.Format("{0}[{1}-{2}]:{3:0.00}:{4}:{5:0.00}:{6:0.00};", sampleName, startFrame, endFrame, sampleTime, "", startTime, endTime);
    }
}


public class TS : MonoBehaviour
{
    private static Dictionary<string, SStopWatch> stopwatchMaps = new Dictionary<string, SStopWatch>();
    private static Stack<string> sampleStack = new Stack<string>();
    private static List<SampleData> sampleDatas = new List<SampleData>();
    //private static List<SampleData> cacheDatas  = new List<SampleData>();

    private static Dictionary<string, SampleDataCrossFrame> stopwatchMapsCrs = new Dictionary<string, SampleDataCrossFrame>();
    private static List<SampleDataCrossFrame> sampleDataCrs = new List<SampleDataCrossFrame>();

    /*
     * upload url
     * */
    public string urlTimeSimple = "http://172.18.98.17:8888/jxsj_profiler";

    /*
     * cache multipart/form-data 
     * */
    StringBuilder sb = new StringBuilder(20480);

    private static long timeStamp;

    private static bool bStopSample = true;
    private double totalTime = 0.0;

    private static int m_nCurrentFrame = 0;

    //int nFirstFrame = 0;
    void Awake()
    {
        bStopSample = false;
TS.BeginSample("XX.cs.Awake");

        m_nCurrentFrame = Time.frameCount;

        timeStamp = Stopwatch.GetTimestamp();

        StartCoroutine(_CheckSamples());

TS.EndSample();
    }

    void OnEnable()
    {

    }

    void Start()
    {

    }

    void FixedUpdate()
    {

    }
    void Update()
    {
        TS.BeginSample("TS.Update");
        TS.EndSample();
    }

    void LateUpdate()
    {
    
    }

    void OnDisable()
    {
    
    }

    void OnLevelWasLoaded()
    {
    
    }

    public static void TerminateSample()
    {
        bStopSample = true;
    }

	// Update is called once per frame

    public static void BeginSample(string samplerName)
    {
        if (bStopSample)
            return;

        if (stopwatchMaps.ContainsKey(samplerName))
        {
			UnityEngine.Debug.LogWarning(string.Format("Sample: {0} is already exist!", samplerName));
            return;
        }
        Stopwatch stopwatch = Stopwatch.StartNew();
        stopwatch.Start();

        SStopWatch sstopwatch = new SStopWatch();
        sstopwatch.stopwatch = stopwatch;

        sstopwatch.startTime = (Stopwatch.GetTimestamp() / (double)Stopwatch.Frequency) * 1000;

        stopwatchMaps.Add(samplerName, sstopwatch);
        sampleStack.Push(samplerName);
    }

    public static void EndSample()
    {
        if (bStopSample && sampleStack.Count == 0)
            return;

        if (sampleStack.Count == 0)
        {
            return;
        }

        string sampleName = sampleStack.Pop();

        if (!stopwatchMaps.ContainsKey(sampleName))
        {
			UnityEngine.Debug.LogErrorFormat("Sample {0} is not exist!", sampleName);
            return;
        }

        SStopWatch sstopwatch = stopwatchMaps[sampleName];
        if (!sstopwatch.stopwatch.IsRunning)
        {
			UnityEngine.Debug.LogErrorFormat("Sampler {0} is not running, please call BeginSample first", sampleName);
            return;
        }

        sstopwatch.stopwatch.Stop();
        stopwatchMaps.Remove(sampleName);

        SampleData sd = new SampleData();

        sd.startTime = sstopwatch.startTime;
        double nTime = ((double)sstopwatch.stopwatch.ElapsedTicks / (double)Stopwatch.Frequency) * 1000;
        sd.endTime = ((double)Stopwatch.GetTimestamp() / (double)Stopwatch.Frequency) * 1000;

        sd.sampleName = sampleName;
        sd.sampleTime = nTime;
        

        if (sampleStack.Count != 0)
        {
            sd.parentSampleName = sampleStack.Peek();
        }
        else
        {
            sd.parentSampleName = string.Format("Frame {0}", m_nCurrentFrame);
        }

        sampleDatas.Add(sd);
    }

    public static void BeginSampleCrossFrame(string sampleName)
    {
        if (bStopSample)
            return;

        //stopwatchMapsCrs.contaik
        if (stopwatchMapsCrs.ContainsKey(sampleName))
        {
			UnityEngine.Debug.LogWarningFormat(string.Format("Sample: {0} is already exist!", sampleName));
            return;
        }
        Stopwatch stopwatch = Stopwatch.StartNew();
        stopwatch.Start();

        SampleDataCrossFrame data = new SampleDataCrossFrame();
        data.stopwatch = stopwatch;
        data.sampleName = sampleName;
        data.startFrame = m_nCurrentFrame;
        data.startTime = ((double)Stopwatch.GetTimestamp() / (double)Stopwatch.Frequency) * 1000;

        stopwatchMapsCrs.Add(sampleName, data);
    }

    public static void EndSampleCrossFrame(string sampleName)
    {
        if (bStopSample)
            return;

        if (!stopwatchMapsCrs.ContainsKey(sampleName))
        {
			UnityEngine.Debug.LogErrorFormat("Sample {0} is not exist in CrossFrameData", sampleName);
            return;
        }

        SampleDataCrossFrame data = stopwatchMapsCrs[sampleName];
        if (!data.stopwatch.IsRunning)
        {
			UnityEngine.Debug.LogErrorFormat("Sampler {0} is not running, please call BeginSampleCrossFrame first", sampleName);
            return;
        }

        data.stopwatch.Stop();
        stopwatchMapsCrs.Remove(sampleName);

        double nTime = ((double)data.stopwatch.ElapsedTicks / (double)Stopwatch.Frequency) * 1000;
        data.endFrame = m_nCurrentFrame;
        data.sampleTime = nTime;
        data.sampleFrames = data.endFrame - data.startFrame;
        data.endTime = ((double)Stopwatch.GetTimestamp() / (double)Stopwatch.Frequency) * 1000;

        sampleDataCrs.Add(data);
    }

    IEnumerator _CheckSamples()
    {
        while (!bStopSample)
        {
            yield return new WaitForEndOfFrame();

            _UploadSampleData();
            CacheData();
            m_nCurrentFrame++;
        }
        
    }

    private void CacheData()
    {
        //SampleData[] cache = new SampleData[sampleDatas.Count];
        //sampleDatas.CopyTo(cache);
        //cacheDatas
        /*
        cacheDatas.Clear();
        cacheDatas.AddRange(sampleDatas);
        */
        sampleDatas.Clear();
        sampleDataCrs.Clear();
    }

    private float _GetFps()
    {
        return 1.0f;
    }

    //IEnumerator _UploadSampleData()
    void _UploadSampleData()
    {
        WWWForm form = new WWWForm();

        long currentStamp = Stopwatch.GetTimestamp();
        sb.Remove(0, sb.Length);

        /*
        if (m_nCurrentFrame == 0)
        {
            sb.Append(string.Format("Time since started: {0:0.00};", timeSinceStarted));
        }
        */
        double frameTime = ((double)(currentStamp - timeStamp) / (double)Stopwatch.Frequency) * 1000;

        totalTime += frameTime;

        sb.Append(string.Format("Frame {0}:{1:0.00}:{2}:{3:0.00}:{4:0.00}:{5:0.00};", m_nCurrentFrame, frameTime,
                  null, timeStamp / (double)Stopwatch.Frequency * 1000, currentStamp / (double)Stopwatch.Frequency * 1000, totalTime));

        timeStamp = currentStamp;

        while (sampleStack.Count != 0)
        {
            EndSample();
        }
                
        foreach (var data in sampleDatas)
        {
            sb.Append(data.ToString());
        }

        _UploadCrsFrameData(form);

        form.AddField("data", sb.ToString());

        new WWW(urlTimeSimple, form);

        //yield return www;
    }

    void _UploadCrsFrameData(WWWForm form)
    {
        int nCount = sampleDataCrs.Count;
        if (nCount != 0)
        {
            for (int nIndex = 0; nIndex < nCount; ++nIndex)
            {
                sb.Append(sampleDataCrs[nIndex].ToString());
            }
        }
    }
}
