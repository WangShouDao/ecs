def count_time(time1, time2):
    monthDay = [31,28,31,30,31,30,31,31,30,31,30,31]
    if time1[0] % 4 !=0:
        if time2[1] == time1[1]:
            count = time2[2] - time1[2]
        else:
            count = time2[2] - time1[2] + monthDay[time1[1] - 1]
    elif  time1[0] % 400 != 0:
        if time2[1] == time1[1]:
            count = time2[2] - time1[2]
        else:
            count = time2[2] - time1[2] + monthDay[time1[1] - 1]
    else:
        if time2[1] == time1[1]:
            count = time2[2] - time1[2]
        elif time2[1] == 3:
            count = time2[2] - time1[2] + 29
        else:
            count = time2[2] - time1[2] + monthDay[time1[1] - 1]
    return count

def read_input(input_lines):
    values = input_lines[0].split(' ')
    cpu = values[0]
    memory = int(values[1]) * 1024
    disk = values[2]

    value = int(input_lines[2])
    flavorArray = []
    inputDict = {}
    for i in range(3, value + 3):
        values = input_lines[i].split(' ')
        flavorName = values[0]
        cpuSize = values[1]
        memorySize = values[2].strip()
        flavorArray.append(flavorName)
        inputDict[flavorName] = {'cpu':cpuSize, 'memory':memorySize}
    kind = input_lines[value + 4].strip()

    startTime = map(int,input_lines[value + 6].strip().split(' ')[0].split('-'))
    endTime = map(int,input_lines[value + 7].strip().split(' ')[0].split('-'))
    count = count_time(startTime, endTime)
    print count,startTime,endTime
    return cpu,memory,kind,count,flavorArray,inputDict

def linear_regression(x,y,k,count):
    N = float(len(x))
    sx, sy, sxx, syy, sxy = 0, 0, 0, 0, 0
    for i in range(0, int(N)):
        sx += x[i]
        sy += y[i]
        sxx += x[i] * x[i]
        syy += y[i] * y[i]
        sxy += x[i] * y[i]
    a = (sy * sx / N - sxy) / (sx * sx / N - sxx)
    b = (sy - a * sx) / N
    # r = abs(sy * sx / N - sxy) / math.sqrt((sxx - sx * sx / N) * (syy - sy * sy / N))
    sum = 0
    for i in range(k+1,count+k+1):
        y = a * i + b
        if y>=0:
            sum += int(y)
        else:
            continue
    return int(sum)

def read_ecs(ecs_lines,flavorArray,result,inputDict,count):
    flavorDict = {}
    inputDataDict = {}
    for item in inputDict:
        inputDataDict[item] = {}
    k = 0
    sum = 0
    createTimeArray = []
    for item in ecs_lines:
        values = item.split("\t")
        uuid = values[0]
        flavorName = values[1]
        createTime = values[2].strip().split(' ')[0]
        if flavorName not in inputDict:
            continue
        elif createTime not in createTimeArray:
            createTimeArray.append(createTime)
            k+=1
            for key in inputDataDict:
                inputDataDict[key][k] = 0
            inputDataDict[flavorName][k] = 1
        else:
            inputDataDict[flavorName][k] += 1
    for item in inputDataDict:
        x = []
        y = []
        for k,v in inputDataDict[item].items():
            x.append(k)
            y.append(v)
        n = linear_regression(x,y,k,count)
        flavorDict[item] = n
        sum += n
    result.append(sum)
    for item in flavorDict:
        result.append(item + ' '+ str(flavorDict[item]))
    return flavorDict,result

def put_vm(kind,cpu,memory,flavorDict,inputDict, result):
    k = 0
    CPU = [cpu]
    MEM = [memory]
    placeDict = {1:{},}
    flavorSort = []
    temp = sorted(flavorDict.items(), key = lambda item:int(item[0][6:]),reverse = True)
    [flavorSort.append(item[0]) for item in temp]
    for item in flavorSort:
        while flavorDict[item] > 0:
            for i in range(0,k+1):
                flag = True
                if int(CPU[i]) >= int(inputDict[item]['cpu']) and int(MEM[i]) >= int(inputDict[item]['memory']):
                    CPU[i] = int(CPU[i]) - int(inputDict[item]['cpu'])
                    MEM[i] = int(MEM[i]) - int(inputDict[item]['memory'])
                    flavorDict[item] = int(flavorDict[item]) - 1
                    flag = False
                    if item not in placeDict[i+1]:
                        placeDict[i+1][item] = 1
                    else:
                        placeDict[i+1][item] += 1
                elif i < k:
                    continue
                elif i==k and flag:
                    k+=1
                    CPU.append(cpu)
                    MEM.append(memory)
                    CPU[k] = int(cpu) - int(inputDict[item]['cpu'])
                    MEM[k] = int(memory) - int(inputDict[item]['memory'])
                    flavorDict[item] = int(flavorDict[item]) - 1
                    placeDict[k+1] = {item:1}
                else:
                    break
    result.append('\n' + str(len(placeDict)))
    for item in placeDict:
        temp = str(item)
        for key in placeDict[item]:
            temp = temp + ' ' + key + ' ' + str(placeDict[item][key])
        result.append(temp)
    return result

def predict_vm(ecs_lines, input_lines):
    # Do your work from here#
    result = []
    if ecs_lines is None:
        print 'ecs information is none'
        return result
    if input_lines is None:
        print 'input file information is none'
        return result
    cpu, memory, kind, count, flavorArray,inputDict=read_input(input_lines)
    flavorDict, result = read_ecs(ecs_lines,flavorArray,result,inputDict,count)
    result=put_vm(kind,cpu,memory,flavorDict,inputDict,result)

    return result