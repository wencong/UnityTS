import tornado.ioloop
import tornado.web

import logging
import os
import time
import io

import subprocess

def get_default_logger(log_to, log_path=None, level=logging.DEBUG,
                       name='profiler'):
    """Get a logger."""
    logger = logging.getLogger(name)
    if logger.handlers:
        # already setup
        return logger
    if log_to.count("console"):
        hdlr = logging.StreamHandler()
        logger.addHandler(hdlr)
    if log_to.count("file") and log_path:
        if os.access(log_path, os.F_OK):
            os.rename(log_path, log_path + '.' + str(int(time.time())))
            pass
        hdlr = logging.FileHandler(log_path)
        logger.addHandler(hdlr)
    logger.setLevel(level)
    return logger


class SampleData:
    def __init__(self, sampleName, sampleTime, sampleParentName, startTime, endTimd, totalTime):
        self.sampleName = sampleName;
        self.sampleTime = sampleTime
        self.sampleParentName = sampleParentName
        self.startTime = startTime
        self.endTime = endTimd
        
        self.totalTime = totalTime
        
        self.childSamples = []
        
        self.nCallTimes = 1;
    
    def AddChild(self, sampleData):
        self.childSamples.append(sampleData)
        #self.childSamples.sort(cmp = lambda x, y : cmp (y.sampleTime, x.sampleTime))
        self.childSamples.sort(cmp = lambda x, y : cmp (float(x.startTime), float(y.startTime)))
    
    def Children(self):
        return self.childSamples;
    
    def __str__(self):
        return '%s %s %s %s %s' % (self.sampleName, self.sampleTime, self.sampleParentName, self.startTime, self.endTime)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('25')
    
    def post(self):
        #print self.request.arguments['data']
        dataStr = self.request.arguments['data'][0]
        #print dataStr;
        
        dataList = dataStr.split(';');
        
        samples = {}
        
        for value in dataList:
            sample = value.split(':')
            
            try:
                sampleName = sample[0];
                sampleTime = sample[1];
                sampleParentName = sample[2];
                startTimd = sample[3]
                endTime = sample[4]
                
                totalTime = ''
                if (len(sample) >= 6):
                    totalTime = sample[5]
                
                t = samples.get(sampleName, None)
                
                #samples[sampleName] = SampleData(sampleName, float(sampleTime), sampleParentName, startTimd, endTime, totalTime)
                
                if (t == None):
                    samples[sampleName] = SampleData(sampleName, float(sampleTime), sampleParentName, startTimd, endTime, totalTime)
                else:
                    t.sampleTime += float(sampleTime);
                    t.nCallTimes += 1
                    #t.AddChild(SampleData(SampleData(sampleName, float(sampleTime))));
                
            except:
                print(value)
    
        sampleHierarchy = {}
    
        
        for k in samples:
            sampleData = samples[k]
            if (sampleData.sampleParentName != '' and sampleData.sampleParentName != None):
                try:
                    samples[sampleData.sampleParentName].AddChild(sampleData)
                except Exception as e:
                    print sampleData
            else:
                sampleHierarchy[k] = sampleData;
                
        sampleList = sorted(sampleHierarchy.items(), key = lambda d: d[1].startTime)
        #sampleList.reverse()
        #sampleList = sampleHierarchy
        
        #print sampleList;
        
        self.logger = get_default_logger('console')
    
        for sample in sampleList:
            self.ListSample(sample[1], '+');

    def ListSample(self, sampleData, ch):
        if (sampleData.totalTime == ''):
            print("%10s:[%s - %s]\t%s%s[%s]" % (str(sampleData.sampleTime), self.FormatTimeStamp(sampleData.startTime), 
                                        self.FormatTimeStamp(sampleData.endTime), ch , sampleData.sampleName, sampleData.nCallTimes))
        
        else:
            print("%10s:[%s - %s]\t%s%s(%s)" % (str(sampleData.sampleTime), self.FormatTimeStamp(sampleData.startTime), 
                                        self.FormatTimeStamp(sampleData.endTime), ch , sampleData.sampleName, sampleData.totalTime))
                                      
        
        children = sampleData.Children();
        
        for child in children:
            self.ListSample(child, ch + '----');
    
    def FormatTimeStamp(self, timeStamp):
        dotPos = timeStamp.find('.');
        return timeStamp[:dotPos -6] + ',' + timeStamp[dotPos-6: dotPos -3] + ',' + timeStamp[dotPos-3:]
        
if __name__ == "__main__":
    application = tornado.web.Application([
    (r"/jxsj_profiler", MainHandler),
    ])
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
