from Mesh import Mesh
from renderLib.RasterizationG import Rasterization
from renderLib.Mesh0 import Mesh0
import time as t
import json
import math
class Main:
    @staticmethod
    def mkdir(path):
        import os
        if not os.path.exists(path):
            os.makedirs(path) 
    @staticmethod
    def loadJson(path):
        return json.load(open(path))
    @staticmethod
    def saveImg(image,name):
        import cv2
        cv2.imwrite(name,image)
    @staticmethod
    def remove(dir_path):
        import os
        # os.walk会得到dir_path下各个后代文件夹和其中的文件的三元组列表，顺序自内而外排列，如 o下有1文件夹，1下有2文件夹：[('o\1\2', [], ['a.py','b']), ('o\1', ['2'], ['c']), ('o', ['1'], [])]
        for root, dirs, files in os.walk(dir_path, topdown=False):
            #root: 各级文件夹绝对路径
            #dirs: root下一级文件夹名称列表，如 ['文件夹1','文件夹2']
            #files: root下文件名列表，如 ['文件1','文件2']
            for name in files:# 第一步：删除文件
                os.remove(os.path.join(root, name))  # 删除文件
            for name in dirs:# 第二步：删除空文件夹
                os.rmdir(os.path.join(root, name)) # 删除一个空目录
    def __init__(self,opt):
        self.opt=opt
        self.inpath=opt["inpath"]
        self.outpath=opt["result_path"]
        self.startPosition=("startPosition" in opt) and opt["startPosition"] or 0
        self.endPosition=("endPosition" in opt) and opt["endPosition"] or 1
        self.mkdir(self.outpath)
        if opt["result_path_remove"]:
            self.remove(self.outpath)

        matrices_all=self.loadJson(self.inpath+'/matrices_all.json')
        for e in matrices_all:
            e.append([1,0,0,0, 0,1,0,0, 0,0,1,0])
        for e in matrices_all:
            for matrix in e:
                matrix.append(0)
                matrix.append(0)
                matrix.append(0)
                matrix.append(1)
        self.matrices_all=matrices_all

        print("load start")
        t0=t.time()
        numTriangular=0
        self.meshes=[]
        for i in range("maxComponentNum" in self.opt and self.opt["maxComponentNum"] or len(matrices_all)):#range(2000):#(1):# range(5000):# i in  # 500-244704 ,51684-15250776
            m0 = Mesh(self.inpath+'/obj/'+str(i)+'.obj')
            self.meshes.append(m0)
            numTriangular=numTriangular+len(m0.face)*len(matrices_all[i])
            print("\t\t加载进度:", i,"/",len(matrices_all)  , end="\t\r" )
        print("加载时间：", (t.time()-t0)/60, "min\t\t\t" )
        print("三角面片总个数：", numTriangular )
        self.render(
            config["max"],
            config["min"],
            config["step_num"]
        )
        
    def sampling(self,ras,x,y,z,saveFlag):
        images=ras.render(x,y,z)

        visibilityList={}
        for i in images:# cv2.imwrite(str(i)+".png", images[i])# print(images[i])
            visibilityList[str(i+1)]=Mesh0.parse(images[i])
        if math.floor(x)==x:x=int(x)
        if math.floor(y)==y:y=int(y)
        if math.floor(z)==z:z=int(z)
        path=str(x)+","+str(y)+","+str(z)+".json"

        if saveFlag:
            json.dump(
                visibilityList,
                open(self.outpath+"/"+path,"w")
            )

        return visibilityList

    def render(self,max,min,step_num):
        print("矩阵计算 start")
        t0=t.time()
        renderNodes=[]
        mesh_type="InstancedMesh" #"mesh0"   #
        for i in range(len(self.meshes)):#range(len(matrices_all)):
            print("矩阵计算",len(self.meshes),i,end="\t\r")
            m0 = self.meshes[i]
            if mesh_type=="InstancedMesh":
                matrices=self.matrices_all[i]
                renderNodes.append(
                    Mesh0.getInstancedMesh(m0,matrices,i)
                )
            else:#"mesh0"
                for matrix in self.matrices_all[i]:
                    renderNodes.append(
                        Mesh0.getMesh0(m0,matrix,i)
                    )

        print("渲染对象数量:",len(renderNodes))
        print("矩阵计算时间：",(t.time()-t0)/60,"min")

        print("初始化渲染器")
        t0=t.time()
        ras=Rasterization({
            "renderNodes":renderNodes,
            "width":self.opt["w"],
            "height":self.opt["h"],
            "loop":  False # True #
        })
        print("初始化渲染器的时间:",(t.time()-t0)/60,"min")
        step_len=[
            (max[0]-min[0])/step_num[0],
            (max[1]-min[1])/step_num[1],
            (max[2]-min[2])/step_num[2],
        ]
        print("step_len",step_len)
        
        print("开始采样","start:",self.startPosition,";end:",self.endPosition,";")
        t0=t.time()
        if "onlyPanorama" in self.opt  and self.opt["onlyPanorama"]:
            # i1=int((1+step_num[0])/2)
            # i2=int((1+step_num[1])/2)
            # i3=int((1+step_num[2])/2)
            # x=min[0]+i1*step_len[0]
            # y=min[1]+i2*step_len[1]
            # z=min[2]+i3*step_len[2]
            x=self.opt["posPanorama"][0]
            y=self.opt["posPanorama"][1]
            z=self.opt["posPanorama"][2]

            print("采样位置",x,y,z)
            ras.getPanorama(x,y,z)
        else:
            number_all=(1+step_num[0])*(1+step_num[1])*(1+step_num[2])
            for i1 in range(1+step_num[0]):
                for i2 in range(1+step_num[1]):
                    for i3 in range(1+step_num[2]):
                        number=i1*(1+step_num[1])*(1+step_num[2])+i2*(1+step_num[2])+i3
                        percent=number/number_all
                        print("视点总数:",number_all,";当前视点编号:",number,";处理进度:",percent,"\t\t\t",end="\r")
                        if percent>=self.startPosition and percent<=self.endPosition:      
                            x=min[0]+i1*step_len[0]
                            y=min[1]+i2*step_len[1]
                            z=min[2]+i3*step_len[2]
                            self.sampling(ras,x,y,z,True)
        # ras.getPanorama(2213.0870081831645,  23, -1888.057576657758)
        # ras.getPanorama(2154,0,-1918)
        #2154,0,-1918
        # self.sampling(ras,2213.0870081831645,  23, -1888.057576657758,True)
        print("\n 采样时间：",(t.time()-t0)/60,"min")
        self.samplingTime=(t.time()-t0)/60

if __name__ == "__main__":#用于测试
    import sys
    if len(sys.argv)<2:
        print("ERR:请指定config.json的路径")
        exit(0)
    import os
    os.system('cls') #清空Python控制台
    path=sys.argv[1]
    config=Main.loadJson(path)
    main0=Main(config)
    config["samplingTime"]=main0.samplingTime
    config["predict_AllTime"]=main0.samplingTime/(config["endPosition"]-config["startPosition"])
    config["step"]=config["step_num"]
    print("predict_AllTime",config["predict_AllTime"])
    json.dump(
        config,
        open(config["result_path"]+"/config.json","w")
    )
