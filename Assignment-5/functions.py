import json
import re
from pyspark import SparkContext

# A hack to avoid having to pass 'sc' around
dummyrdd = None
def setDefaultAnswer(rdd): 
	global dummyrdd
	dummyrdd = rdd

def task1(amazonInputRDD):
    def split(line):
        sp = line.split()
        return (sp[0][4:], sp[1][7:], sp[2])

    return amazonInputRDD.map(split)

def task2(amazonInputRDD):
    def split(line):
        sp = line.split()
        return (sp[0], float(sp[2]))
    
    def calc(x):
        return (x[0], sum(x[1])/len(x[1]))

    return amazonInputRDD.map(split).groupByKey().mapValues(list).map(calc)

def task3(amazonInputRDD):
    def split(line):
        sp = line.split()
        return (sp[1], float(sp[2]))
    
    def calc(x):
        x, y = x
        dict = {}
        for i in y:
            if i in dict:
                dict[i] += 1
            else:
                dict[i] = 1
            
        max = -1
        value = -1
        for k, v in dict.items():
            if v > max:
                value = k
                max = v
            elif v == max:
                if k > value:
                    value = k
                
        return (x, value)
    
    return amazonInputRDD.map(split).groupByKey().mapValues(list).map(calc)

def task4(logsRDD):
    def split(line):
        sp = line.split()
        return (sp[3][8:12], 1)
    
    return logsRDD.map(split).reduceByKey(lambda x, y: x + y)

def task5_flatmap(x):
    sp = x.split(" ")
    res = []
    for i in sp:
        res.append(re.sub(r'[^a-zA-Z0-9]+', '', i))
    if len(res) == 0:
        res = ['']
    return res

def task6(playRDD):
    def split(line):
        sp = line.split()
        l = 0
        if sp is not None:
            l = len(sp)
        return (sp[0], (line, l))
    
    return playRDD.map(split).filter(lambda x: x[1][1]>10)

def task7_flatmap(x):
    result = []
    for i in x["laureates"]:
        result.append(i["surname"])
    return result

def task8(nobelRDD):
    def calc(x):
        k = x["category"]
        v = []
        for i in x["laureates"]:
            v.append(i["surname"])
        return (k,v)
    
    def relist(x):
        list = []
        for item in x:
            for i in item:
                list.append(i)
        return list
                
    return nobelRDD.map(json.loads).map(calc).groupByKey().mapValues(relist)

def task9(logsRDD, l):
    def split(line):
        sp = line.split()
        return (sp[0], sp[3][1:12])
    
    def calc(x):
        host, date = x
        bool = True
        for i in l:
            if i not in date:
                bool = False
        if bool:
            return host
    
    return logsRDD.map(split).groupByKey().mapValues(list).map(calc).filter(lambda x: x is not None)

def task10(bipartiteGraphRDD):
    def split(x):
        return (x[1], x[0])
    
    def relist(x):
        return len(x)
        
    return bipartiteGraphRDD.groupByKey().mapValues(relist).map(split).groupByKey().mapValues(relist)
