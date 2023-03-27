# web3d-k8s
a web3d cloud-edge architecture base on k8s



安装说明：

机器操作系统为：ubuntu。

安装的docker版本为：20.10.22

安装的k8s版本为：1.22.0

安装的kubeedge版本为：1.12.1



**一、安装k8s集群主节点**

(在master节点上操作)

**准备环境**

```shell
# 禁用交换分区
swapoff -a

# 永久禁用，打开/etc/fstab注释掉swap那一行。  
vim /etc/fstab

# 修改内核参数(首先确认你的系统已经加载了 br_netfilter 模块，默认是没有该模块的，需要你先安装 bridge-utils)
apt-get install -y bridge-utils
modprobe br_netfilter
lsmod | grep br_netfilter

# 如果报错找不到包，需要先更新 apt-get update -y
```

**安装docker**

\# 参考资料

https://www.runoob.com/docker/ubuntu-docker-install.html

```shell
# 设置开机启动并启动docker 
sudo systemctl start docker
sudo systemctl enable docker

# 编辑docker配置文件
vim /etc/docker/daemon.json

# 添加以下内容
{
  "exec-opts": ["native.cgroupdriver=systemd"]
}

# 修改docker数据目录（可选）
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "data-root": "/www/docker"
}

# 重启docker
systemctl restart docker
```

**安装 k8s主要组件**

1.安装依赖项

```shell
# 首先更新 apt 包索引，并安装使用 Kubernetes apt 仓库所需要的包：
apt-get update
apt-get install -y ca-certificates curl

# 如果你使用 Debian 9（stretch）或更早版本，则你还需要安装 apt-transport-https：
apt-get install -y apt-transport-https

# 下载 Google Cloud 公开签名秘钥：
curl -fsSLo /etc/apt/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
```

**问题**：这一步骤可能失败，因为国内无法下载cloud.google.com上的内容

**解决方案：**先从能翻墙的机器下载https:// packages.cloud.google.com/apt/doc/apt-key.gpg再将apt-key.gpg重命名为kubernetes-archive-keyring.gpg，然后传到机器的/etc/apt/keyrings/目录下

```shell
mkdir /etc/apt/keyrings/
cp apt-key.gpg /etc/apt/keyrings/kubernetes-archive-keyring.gpg
```

2.添加 Kubernetes apt 仓库：

```shell
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
```

★问题：国内无法访问https://apt.kubernetes.io/

★解决方案：其中https://apt.kubernetes.io/ 可改为 https://mirrors.aliyun.com/kubernetes/apt

```shell
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://mirrors.aliyun.com/kubernetes/apt kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
```

3.更新 apt 包索引，使之包含新的仓库，并安装 k8s三套件： 

```shell
sudo apt-get update 
sudo apt-get install -y kubectl=1.22.0-00 kubeadm=1.22.0-00 kubelet=1.22.0-00

# 阻止自动更新(apt upgrade时忽略)。所以更新的时候先unhold，更新完再hold。
sudo apt-mark hold kubelet kubeadm kubectl
```

**初始化集群**

```shell
kubeadm init --image-repository registry.aliyuncs.com/google_containers --kubernetes-version=v1.22.0 --pod-network-cidr=10.244.0.0/16
```

★问题：可能出现kubeadm命令不能用或kubeadm command not found

★解决方案：

echo "export KUBECONFIG=/etc/kubernetes/admin.conf" >> /etc/profile

如果【初始化集群】成功，则会出现结果： 

To start using your cluster, you need to run the following as a regular user:

mkdir -p $HOME/.kube sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config sudo chown $(id -u):$(id -g) $HOME/.kube/config

Alternatively, if you are the root user, you can run:

export KUBECONFIG=/etc/kubernetes/admin.conf

You should now deploy a pod network to the cluster. Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at: https://kubernetes.io/docs/concepts/cluster-administration/addons/

Then you can join any number of worker nodes by running the following on each as root:

kubeadm join 172.23.63.40:6443 --token kjnfer.6i5msg83zhnr4zyy \ --discovery-token-ca-cert-hash sha256:7380016ab4269741100133180ca71e29e2178cf77b310a62910a5041e082770d

此处要记得按照提示执行标红部分的命令来保存k8s集群配置文件。标蓝部分是k8s推荐的将节点加入集群的命令，但这里我们不需要，因为我们要使用kubeedge的方式来使边缘节点加入集群。

**二，安装kubeedge的cloudcore**

(在cloudcore节点操作)

●**准备环境**(同一)

●**安装docker**(同一)

●**安装 k8s主要组件**(同一，但仅安装kubectl)

● 放开kubeedge所需端口：1883、1884、10000、10001、10002、10003、10004、10550 （云端和边缘节点都要放开）

1.安装keadm：

```shell
# 下载(如果无法连接到github下载，先下载到别的机器再上传)
wget https://github.com/kubeedge/kubeedge/releases/download/v1.12.1/keadm-v1.12.1-linux-amd64.tar.gz

# 解压
tar zxvf keadm-v1.12.1-linux-amd64.tar.gz

# 添加执行权限并移动keadm工具到系统bin目录
chmod +x keadm-v1.12.1-linux-amd64/keadm/keadm
mv keadm-v1.12.1-linux-amd64/keadm/keadm /usr/local/bin/
```

2.启动KubeEdge cloudcore

```shell
# 执行init操作,其中[master-node-ip]改为k8s的master节点的公网IP
keadm init keadm init --advertise-address=[master-node-ip] --set iptablesManager.mode="external" --profile version=v1.12.1
```

**问题：**如果将kubeedge的cloudcore部署到k8s master节点上，要先将master去污（untaint）,因为cloudcore是以pod运行的，而master节点默认是不允许调度pod上去的

**解决方案：**

将master节点标记为可调度

kubectl taint nodes --all node-role.kubernetes.io/master-

3.添加节点亲和性设置（阻止kube-proxy等k8s核心pod调度到边缘节点）

```shell
kubectl get daemonset -n kube-system | grep -v NAME | awk '{print $1}' | xargs -n 1 kubectl patch daemonset -n kube-system --type='json' -p='[{"op": "replace", "path":"/spec/template/spec/affinity","value":{"nodeAffinity":{"requireDuringSchedulingIgnoreDuringExecution":{"nodeSelectorTerms":[{"matchExpressions":[{"key":"node-role.kubenetes.io/edge","operator":"DoesNotExist"}]}]}}}}]'
```

4.启用数据收集组建metrics-server（可选）

```shell
# 安装metrics-server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/download/metrics-server-helm-chart-3.8.3/components.yaml
```

如遇到metrics-server安装问题，参考：https://blog.csdn.net/icanflyingg/article/details/126370832



**三，安装kubeedge的edgecore**

（在edgecore节点操作）

●**准备环境**(同一)

●**安装docker**(同一)

●**安装 k8s主要组件**(同一，但仅安装kubectl)

●安装keadm(同二.1)

1.先在cloudcore机器上获取token（在cloudcore节点操作）

```shell
keadm gettoken
```

2.到边缘机器上安装edgecore（在edgecore节点操作）

```shell
keadm join --cloudcore-ipport=[cloudcore-ip]:10000 --token=[token] --kubeedge-version=1.12.1
# [cloudcore-ip] 是cloudcore 节点的ip地址，[token]是在上一步获取到的token

# 检查edgecore安装是否成功 ->
# 查看edgecore状态
service edgecore status 

# 查看edgecore安装日志 
journalctl -u edgecore.service -f

# 启动edge-stream(可以在云端查看到边缘日志) ->
# 修改边缘端机器上的文件
vim /etc/kubeedge/config/edgecore.yaml #将edgeStream设为true

# 重启edgecore
service edgecore restart
```

3.验证集群可用(在cloudcore节点上操作)

```shell
# 准备一个depolyment的yaml文件：->
# depolyment示例（nginx-deployment.yaml） 
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80

# 部署depolyment：
kubectl apply -f [nginx-deployment.yaml]

# 查看depolyment信息：
kubectl get deployment

# 卸载depolyment：
kubectl delete deployment [deployment-name]

# 再检查pod是否已删除：
kubectl get pod
```

**四，调试命令：** 

```shell
# 日志命令->
# describe方式：
kubectl describe pods metrics-server -n kube-system 

# log方式：
kubectl logs -f pod/metrics-server-cd4d8f6f9-9hmb8 -n kube-system -c metrics-server

# systemctl方式
systemctl status kubelet

# docker命令->
# 批量停止容器
sudo docker stop $(sudo docker ps -a | grep "Exited" | awk '{print $1 }')

# 批量删除容器
sudo docker rm $(sudo docker ps -a | grep "Exited" | awk '{print $1 }')

# 批量删除镜像
sudo docker rmi $(sudo docker images | grep "none" | awk '{print $3}')
```

