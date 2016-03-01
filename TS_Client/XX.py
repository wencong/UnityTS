import os
from shutil import copytree, ignore_patterns

SrcDir = 'H:/work/SVN/swordm3d-code/trunk/client/swordm3d/Assets/_Game/Scripts'
#SrcDir = 'H:/work/SVN/swordm3d-code/trunk/client/swordm3d/Assets'
#SrcDir = 'H:/Test'

NoneAwakeList = []
SampleList = []

def log(szMsg):
    print szMsg

def GetLeftAndRightTrace(awakeMethod):
    leftTrace = rightTrace = 0;
    bTrace = False
    
    stack = 0;
    nIndex = 0;
    
    for ch in awakeMethod:
        if (ch == '{'):
            stack += 1
            if (bTrace == False):
                leftTrace = nIndex
                bTrace = True
            
        elif (ch == '}'):
            rightTrace = nIndex
            stack -= 1
        
        nIndex += 1
        if (bTrace == True and stack == 0):
            return leftTrace, rightTrace
    
    return leftTrace, rightTrace

def SplitReturn(awakeContent):
    ret = awakeContent.split('return')
    
    splitRet = ''
    if (len(ret) > 1):
        for nIndex in range(len(ret)):
            block = ret[nIndex]

            ifcond = block;
            
            ifpos = block.rfind("if")
            
            try:
                if ifpos != -1 and '{' not in ifcond[ifpos: ] and nIndex != (len(ret)-1):
                    ret[nIndex] = block + '{'
                    
                    end = ret[nIndex + 1]
                    fenhaoPos = end.find(';')
                    ret[nIndex + 1] = '%s%s%s' % (end[:fenhaoPos+1], '}', end[fenhaoPos+1:])
            except:
                pass
                #log(block)
                    
        splitRet = '\r\nTS.EndSample(); return'.join(ret)
    else:
        splitRet = awakeContent
        
    splitRet = splitRet + "\nTS.EndSample();"
    
    return splitRet

def GetIEnumeraInfo(IEnumeraContent):
    leftTrace, rightTrace = GetLeftAndRightTrace(IEnumeraContent)
    
    pos = IEnumeraContent.find("(")
    name = IEnumeraContent[1:pos]
    
    return name, leftTrace, rightTrace
    

def AddSampleToCoroutine(fileName, fullpath):
    fp = open(fullpath, 'r')
    szCodeText = fp.read()
    splitIEnumera = szCodeText.split("IEnumerator")
    
    if (len(splitIEnumera) < 2):
        return
    
    for nIndex in range(len(splitIEnumera)):
        
        if nIndex == 0:
            continue
        IenumeraContent = splitIEnumera[nIndex]
        
        info = GetIEnumeraInfo(IenumeraContent)
        if (info[1] == 0 or info[2] == 0):
            continue
        coroutineName = info[0]
        coroutineBefore = IenumeraContent[0:info[1]+1]
        coroutineContent = IenumeraContent[info[1]+1:info[2]]
        coroutineAfter = IenumeraContent[info[2]:]
        
        splitIEnumera[nIndex] = '%s\r\nTS.BeginSampleCrossFrame("%s.%s");\r\n%s\r\nTS.EndSampleCrossFrame("%s.%s");\r\n    %s' % (coroutineBefore,\
                                                                                                          fileName, coroutineName,\
                                                                                                          coroutineContent,\
                                                                                                          fileName, coroutineName,\
                                                                                                          coroutineAfter
                                                                                                          )
        #print splitIEnumera[nIndex]
        
    newContent = "IEnumerator".join(splitIEnumera)
    fp = open(fullpath, 'w')
    fp.write(newContent);
    #print newContent
    
def AddSample(szFileName, szCodeText, keyword):
    
    posAwake = szCodeText.find(keyword)
    
    if posAwake == -1:
        #log("no %s method in %s" %( keyword, szFileName))
        return;
    
    leftTrace, rightTrace = GetLeftAndRightTrace(szCodeText[posAwake:])
    
    if (leftTrace == 0 or rightTrace == 0):
        #log("%s Do not find {} content" % szFileName)
        return;
    
    awakeBefore =  szCodeText[:posAwake + leftTrace + 1]
    awakeContent = szCodeText[posAwake + leftTrace + 1: posAwake + rightTrace]
    awakeAfter =   '    ' + szCodeText[posAwake + rightTrace:]
    #print awakeBefore
    #print awakeContent
    #print awakeAfter
    
    #return

    funcName = keyword.split(' ');
    awakeSampleName = szFileName + "." + funcName[1];
    
    if ('StartCoroutine' in awakeContent):
        log("there is yield in %s.%s" % (szFileName, keyword))
        return;
    
    awakeContent = SplitReturn(awakeContent);
    
    szSampleContent = '%s\r\nTS.BeginSample("%s");\n%s\r\n%s' % \
                                (awakeBefore, awakeSampleName, awakeContent, awakeAfter)
                                
    return szSampleContent
    
def AddSamples(fileName, fullpath, keyword):
    fp = open(fullpath, 'r')
    fileContent = fp.read()
    
    ret = AddSample(fileName, fileContent, keyword)
    
    if (ret != None):
        #SampleList.append(fullpath)
        fp.close()
        fp = open(fullpath, 'w')
        fp.write(ret);
    
    '''
    else:
        NoneAwakeList.append(fullpath)
    '''
    fp.close()
                
    
    pass

def start():
    for root, dirs, files in os.walk(SrcDir, True):
        for file in files:
            try:
                if (not file.endswith(".cs")):
                    continue
                
                if file in ('XX.cs', 'ISubModule.cs', 'MonoSingleton.cs'):
                    continue
                
                fullpath = root + '/' + file
                
                print file;
                
                AddSamples(file, fullpath, "void Awake")
                
                AddSamples(file, fullpath, "void Start()")
                AddSamples(file, fullpath, "void Start ()")
                
                AddSamples(file, fullpath, "void OnEnable")
                
                AddSamples(file, fullpath, "void Init ()")
                AddSamples(file, fullpath, "void Init()")
                
                AddSamples(file, fullpath, "bool Init()")
                AddSamples(file, fullpath, "bool Init ()")
                
                #AddSampleToCoroutine(file, fullpath);
                
                '''
                AddSamples(file, fullpath, "void OnDisable")
                
                AddSamples(file, fullpath, "void Update()")
                AddSamples(file, fullpath, "void Update ()")
                
                AddSamples(file, fullpath, "void LateUpdate")
                AddSamples(file, fullpath, "void FixedUpdate")
                
                
                AddSamples(file, fullpath, "void Update()")
                AddSamples(file, fullpath, "void Update ()")
                AddSamples(file, fullpath, "void LateUpdate()")
                AddSamples(file, fullpath, "void LateUpdate ()")
                
                AddSamples(file, fullpath, "void FixedUpdate()")
                AddSamples(file, fullpath, "void FixedUpdate ()")
                
                '''
                
                '''
                AddSamples(file, fullpath, "bool Init ()")
                AddSamples(file, fullpath, "void Init ()")
                AddSamples(file, fullpath, "bool UnInit ()")
                '''
                
            except Exception as e:
                #log(e)
                continue
    
        #print '\n'
    pass
    
if __name__ in ("main", "__main__"):
    start();
    #AddSampleToCoroutine("Game.cs", "H:/Test/Game.cs");
    
    
        