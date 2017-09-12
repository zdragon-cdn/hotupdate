#!/usr/bin/python
#encoding=utf-8
import io
import sys
import hashlib
import string
import os
import os.path
import json
import time

def printUsage():
    print ('''''Usage: [python] pymd5sum.py <filename>''')

def getMD5(filePath):
    m = hashlib.md5()
    file = io.FileIO(filePath,'r')
    bytes = file.read(1024)
    while(bytes != b''):
        m.update(bytes)
        bytes = file.read(1024)
    file.close()

    #md5value = ""
    md5value = m.hexdigest()
    return md5value
    #dest = io.FileIO(sys.argv[1]+".CHECKSUM.md5",'w')
    #dest.write(md5value)
    #dest.close()

def handleFolder(dir):

    for parent,dirnames,filenames in os.walk(dir):    #三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
        # print("x\t"+parent + "\t")
        # for dirname in  dirnames:                       #输出文件夹信息
            # print("dir\t"+os.path.join(parent,dirname))

            # handleFolder(os.path.join(parent,dirname))
        for filename in filenames:                        #输出文件信息
            # print("file\t"+ os.path.join(parent,filename))
            printMD5(os.path.join(parent,filename));

# relativePath  要加 /
def updateManifest(relativePath):   
    f = file(relativePath + "project.manifest", "r");

    jsonObj = json.load(f)
    f.close()


    # 直接以所有资源的MD5值  的MD5值做版本号
    versionMD5 = hashlib.md5()

    jsonObj["assets"] = {}
    for parent,dirnames,filenames in os.walk("assets"):    #三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
    # print("x\t"+parent + "\t")
        # for dirname in  dirnames:                       #输出文件夹信息
        #     print("dir\t"+dirname)

        # handleFolder(os.path.join(parent,dirname))
        for filename in filenames:                        #输出文件信息
            filePath = os.path.join(parent,filename)
            attr = filePath[7:]
            jsonObj["assets"][attr] = {}
            md5Value =  getMD5(filePath)
            jsonObj["assets"][attr]["md5"] = md5Value

            versionMD5.update(md5Value)
            if(len(filePath) > 4 and filePath[-4:] == ".zip"):
                jsonObj["assets"][attr]["compressed"] = True
            
    jsonObj["version"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    jsonStr = json.dumps(jsonObj, ensure_ascii = False,indent = 4)

    #写入project.manifest
    outFile = file(relativePath + "project.manifest", "w")
    outFile.write(jsonStr.strip().encode('utf-8') + '\n')
    outFile.close()
    
    #写入version.manifest
    outFile = file(relativePath +"version.manifest", "w")
    del jsonObj["assets"] #= None
    del jsonObj["searchPaths"] #= None
    jsonStr = json.dumps(jsonObj, ensure_ascii = False,indent = 4)
    outFile.write(jsonStr.strip().encode('utf-8') + '\n')
    outFile.close()

def initHotUpdate(defaultRelativePath, sslRelativePath, creatorVersion):
    #创建目录
    if os.path.isdir(defaultRelativePath) == False:
        os.mkdir(defaultRelativePath)
    
    if os.path.isdir(sslRelativePath) == False:
        os.mkdir(sslRelativePath)

    projectPath = os.path.abspath('.')
    projectName = os.path.split(projectPath)[0]
    projectName = os.path.split(projectName)[-1]

    engineVersion = "creator " + creatorVersion
    
    projectManifest = ''' {
               "packageUrl": "$schema://raw.githubusercontent.com/zdragon-cdn/hotupdate/$project/$version/assets/", 
                "searchPaths": {}, 
                "assets": {}, 
                "remoteVersionUrl": "$schema://raw.githubusercontent.com/zdragon-cdn/hotupdate/$project/$version/$filedir/version.manifest", 
                "version": "2017-03-08 20:07:16", 
                "engineVersion": "$engineVersion", 
                "remoteManifestUrl": "$schema://raw.githubusercontent.com/zdragon-cdn/hotupdate/$project/$version/$filedir/project.manifest"
            }'''


    versionManifest = '''{
        "packageUrl": "$schema://raw.githubusercontent.com/zdragon-cdn/hotupdate/$project/$version/assets/", 
        "remoteVersionUrl": "$schema://raw.githubusercontent.com/zdragon-cdn/hotupdate/$project/$version/$filedir/version.manifest", 
        "version": "2017-03-08 20:07:16", 
        "engineVersion": "$engineVersion", 
        "remoteManifestUrl": "$schema://raw.githubusercontent.com/zdragon-cdn/hotupdate/$project/$version/$filedir/project.manifest"
    }'''

    #直接全部列出来 毕竟文件比较少
    if os.path.exists(defaultRelativePath + 'version.manifest') == False:
        f = open(defaultRelativePath+'version.manifest', 'w')    
        versionStr = versionManifest.replace('$schema', 'http')
        versionStr = versionStr.replace('$project', projectName)  
        versionStr = versionStr.replace('$filedir', 'default')
        versionStr = versionStr.replace('$version', creatorVersion)
        versionStr = versionStr.replace('$engineVersion', engineVersion)
        jo = json.loads(versionStr)
        content = json.dumps(jo, ensure_ascii=False, indent=4)  
        f.write(content)
        f.close()

    if os.path.exists(defaultRelativePath + 'project.manifest') == False:
        f = open(defaultRelativePath + 'project.manifest', 'w')    
        projectStr = projectManifest.replace('$schema', 'http')
        projectStr = projectStr.replace('$project', projectName)  
        projectStr = projectStr.replace('$filedir', 'default')
        projectStr = projectStr.replace('$version', creatorVersion)
        projectStr = projectStr.replace('$engineVersion', engineVersion)
        jo = json.loads(projectStr)
        content = json.dumps(jo, ensure_ascii=False, indent=4)  
        f.write(content)
        f.close()  

    if os.path.exists(sslRelativePath + 'version.manifest') == False:
        f = open(sslRelativePath + 'version.manifest', 'w') 
        versionStr = versionManifest.replace('$schema', 'https')
        versionStr = versionStr.replace('$project', projectName)   
        versionStr = versionStr.replace('$filedir', 'ssl')
        versionStr = versionStr.replace('$version', creatorVersion)
        versionStr = versionStr.replace('$engineVersion', engineVersion)
        jo = json.loads(versionStr)
        content = json.dumps(jo, ensure_ascii=False, indent=4)   
        f.write(content)
        f.close()


    if os.path.exists(sslRelativePath + 'project.manifest') == False:
        f = open(sslRelativePath + 'project.manifest', 'w') 
        projectStr = projectManifest.replace('$schema', 'https')
        projectStr = projectStr.replace('$project', projectName)   
        projectStr = projectStr.replace('$filedir', 'ssl')
        projectStr = projectStr.replace('$version', creatorVersion)
        projectStr = projectStr.replace('$engineVersion', engineVersion)
        jo = json.loads(projectStr)
        content = json.dumps(jo, ensure_ascii=False, indent=4)   
        f.write(content)
        f.close()
    

def main():
    if len(sys.argv) < 2 :
        print(u"请输入cocos creator 版本号 如 1.4.1")
        return

    creatorVersion = sys.argv[1]
    defaultRelativePath = './default/'
    sslRelativePath = './ssl/'
    initHotUpdate(defaultRelativePath, sslRelativePath, creatorVersion)
    updateManifest(defaultRelativePath)
    updateManifest(sslRelativePath)


if __name__ == '__main__':
    main()



