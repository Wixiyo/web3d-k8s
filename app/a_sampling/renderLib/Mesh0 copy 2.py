import numpy as np
import OpenGL
def getVF(mesh,matrix):
    matrixInstance=np.array(matrix).reshape(4,4).T
    vertex0=np.array(mesh.vertex)
    vertex0=np.c_[vertex0,np.ones(vertex0.shape[0])] #c_是column(列)的缩写，就是按列叠加两个矩阵，就是把两个矩阵左右组合，要求行数相等。
    vertex0=np.dot(vertex0,matrixInstance)[:,0:3]
    vertex0=np.dot(
        np.array(vertex0),
        np.array([
                [1,0,0],
                [0,0,-1],
                [0,1,0]
            ])
        )
    face0=np.array(mesh.face)-1
    return vertex0,face0
class Mesh0():
    def __init__(self,id,V,F):
        def srgb_to_linsrgb (srgb):
            gamma = ((srgb + 0.055) / 1.055)**2.4
            scale = srgb / 12.92
            return np.where (srgb > 0.04045, gamma, scale)
        # id=1+10*256+3*256*256
        self.color=np.array([
            (id&0xff0000)>>16,#b
            (id&0x00ff00)>>8,#g
            (id&0x0000ff)#r
            ])/255
        self.vertex=np.array(V)
        self.color2=np.ones(self.vertex.shape)
        for i in range(3):
            self.color2[:,i]=self.color2[:,i]*self.color[i]

        self.face=np.array(F).reshape(-1)
        self.vertex=self.vertex.reshape(-1)
        self.color2=self.color2.reshape(-1)

        self.createVAO()
    def createVAO(this):
        import OpenGL
        this.vbo = OpenGL.arrays.vbo.VBO(np.array(this.vertex,'f'))
        this.ebo = OpenGL.arrays.vbo.VBO(np.array(this.face,'H'),target = OpenGL.GL.GL_ELEMENT_ARRAY_BUFFER)
        this.vboLength = len(this.vertex)
        this.eboLength = len(this.face)
        this.bCreate = True
    def draw(this):
        OpenGL.GL.glColor4f(this.color[0], this.color[1], this.color[2], 1.0)  # 设置当前颜色为红色不透明
        this.vbo.bind()
        # this.cbo.bind()
        OpenGL.GL.glInterleavedArrays(OpenGL.GL.GL_V3F,0,None)
        this.ebo.bind()
        # OpenGL.GL.glFrontFace(OpenGL.GL.GL_CW) # GL_CCW（逆时针）或 GL_CW（顺时针）为正向
        OpenGL.GL.glCullFace(OpenGL.GL.GL_FRONT)    # 背面透明 GL_FRONT GL_FRONT_AND_BACK
        OpenGL.GL.glDrawElements(OpenGL.GL.GL_TRIANGLES,this.eboLength,OpenGL.GL.GL_UNSIGNED_SHORT,None)   
        #void     glDrawElementsInstanced(GLenum mode, GLsizei count, GLenum type, void* indices, GLsizei primcount )
    @staticmethod
    def parse(image):
        result={}
        image=256*256*image[:,:,0]+256*image[:,:,1]+image[:,:,2]
        for k in np.unique(image):
            if not k==0xffffff:
                result[str(k)] = image[ image == k ].size
        return result
    @staticmethod
    def getMesh0(mesh,matrix,id):
        v,f=getVF(mesh,matrix)
        return Mesh0(id,v,f)
    @staticmethod
    def getInstancedMesh(mesh,matrices,id):
        vertex_all=np.array([])
        face_all=np.array([])
        for matrix in matrices:
            vertex0,face0=getVF(mesh,matrix)

            start_pos=vertex_all.shape[0]
            face0=face0+start_pos
            
            if start_pos==0:
                vertex_all=vertex0
                face_all=face0
            else:
                vertex_all=np.vstack([vertex_all,vertex0])
                face_all=np.vstack([face_all,face0])

        return Mesh0(id,vertex_all,face_all)
    @staticmethod
    def getBigMesh(mesh,matrices,id):
        vertex_all=np.array([])
        face_all=np.array([])
        for matrix in matrices:
            vertex0,face0=getVF(mesh,matrix)
            
            start_pos=vertex_all.shape[0]
            face0=face0+start_pos
            
            if start_pos==0:
                vertex_all=vertex0
                face_all=face0
            else:
                vertex_all=np.vstack([vertex_all,vertex0])
                face_all=np.vstack([face_all,face0])

        return Mesh0(id,vertex_all,face_all)