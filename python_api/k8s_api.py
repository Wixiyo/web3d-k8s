from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
import yaml

def test():
    # Configs can be set in Configuration class directly or using helper utility
    config.load_kube_config()

    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

def init():
    #可以用以下命令把token 放到一个 文件中
    # Token=$(kubectl describe secret $(kubectl get secret -n kube-system | grep ^admin-user | awk '{print $1}') -n kube-system | grep -E '^token'| awk '{print $2}')
    # echo $Token
    # with open('token.txt', 'r') as file:
    #     Token = file.read().strip('\n')
    
    # #方法二 获取指定的token
    # #kubectl -n kube-system get secret | grep kubernetes-dashboard-token
    # #kubectl describe -n kube-system secret/kubernetes-dashboard-token-xxx
    # #https://github.com/kubernetes-client/python/blob/master/kubernetes/docs
    # # Token = 'thooyn.n2k1kl7mimb46mwv'
    # APISERVER = 'https://100.75.250.48:6443'
 
    # configuration = client.Configuration()
    # setattr(configuration, 'verify_ssl', False)
    # configuration.host = APISERVER    #ApiHost
    # configuration.verify_ssl = False
    # configuration.debug = False
    # configuration.api_key['authorization'] = Token
    config.load_kube_config()
 
    
 
def list_pod_for_all_namespaces(v1):
    ret = v1.list_pod_for_all_namespaces(watch=False)
    print("Listing pods with their IPs:")
    for i in ret.items:
        print("%s\t%s\t%s" %(i.status.pod_ip, i.metadata.namespace, i.metadata.name))
 
def create_namespace(v1):
    bodynamespace = {
        "apiVersion": "v1",
        "kind": "Namespace",
        "metadata": {
            "name": "test123",
        }
    }
    ret = v1.create_namespace(body=bodynamespace)
    print("create_namespace result")
    print (ret)
 
def delete_namespace(v1):
    body = client.V1DeleteOptions()
    body.api_version = "v1"
    body.grace_period_seconds = 0
    ret = v1.delete_namespace("test123", body=body)
    print("delete_namespace result")
    print(ret)
 
def list_namespace(v1):
    limit = 56                                  #返回最大值,可选参数可以不写
    timeout_seconds = 56                                #超时时间可选参数
    watch = False                                   #监听资源，可选参数可以不填
    try:
        api_response = v1.list_namespace(limit=limit,timeout_seconds=timeout_seconds, watch=watch)
        print("list_namespace result")
        for  namespace in api_response.items:
            print(namespace.metadata.name)
    except ApiException as e:
        print("Exception when calling CoreV1Api->list_namespace: %s\n" % e)
 
def create_namespaced_deployment(configuration):
    v1 = client.AppsV1Api(client.ApiClient(configuration))
    #http://www.json2yaml.com/ 把yaml转成json ；然后用https://www.json.cn/json/jsonzip.html 压缩json
    '''
    apiVersion: apps/v1
    kind: Deployment
    metadata: 
    name: test1
    spec:
    selector: 
        matchLabels:
        app: test
    replicas: 1
    template:
        metadata:
        labels: 
            app: test
        spec:
        containers:
            - name: test 
            image: nginx:latest 
            imagePullPolicy: IfNotPresent 
            ports:
                - containerPort: 80
    '''
    body=eval('{"apiVersion":"apps/v1","kind":"Deployment","metadata":{"name":"test1"},"spec":{"selector":{"matchLabels":{"app":"test"}},"replicas":1,"template":{"metadata":{"labels":{"app":"test"}},"spec":{"containers":[{"name":"test","image":"nginx:latest","imagePullPolicy":"IfNotPresent","ports":[{"containerPort":80}]}]}}}}')
    resp = v1.create_namespaced_deployment(body=body, namespace="default")
    print("create_namespaced_deployment result")
    print(resp)
 
def update_namespaced_deployment(configuration):
    v1 = client.AppsV1Api(client.ApiClient(configuration))
    body=eval('{"apiVersion":"apps/v1","kind":"Deployment","metadata":{"name":"test1"},"spec":{"selector":{"matchLabels":{"app":"test"}},"replicas":2,"template":{"metadata":{"labels":{"app":"test"}},"spec":{"containers":[{"name":"test","image":"nginx:latest","imagePullPolicy":"IfNotPresent","ports":[{"containerPort":80}]}]}}}}')
    resp = v1.patch_namespaced_deployment( name="test1",namespace="default", body=body)
    print("patch_namespaced_deployment result")
    print(resp)
 
def delete_namespaced_deployment(configuration):
    v1 = client.AppsV1Api(client.ApiClient(configuration))
    body=client.V1DeleteOptions(propagation_policy='Foreground',grace_period_seconds=0)
    resp = v1.delete_namespaced_deployment(name="test1",namespace="default", body=body )
    print("delete_namespaced_deployment result")
    print(resp)

def list_pod(namespace):
    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    if namespace == None:
        for i in ret.items:
            print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
    else:
        for i in ret.items:
            if i.metadata.namespace == namespace:
                print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

def create_namespaced_pod(path):
    v1  = client.CoreV1Api()
    namespace = "default"
    body = read_yaml(path)
    print(body)
    # body = {"apiVersion":"v1","kind":"Pod","metadata":{"name":"gl-test"},"spec":{"restartPolicy":"OnFailure","containers":[{"name":"pyopengl-test","image":"pyopengl:1.0","imagePullPolicy":"IfNotPresent","command":["bash","start.sh"],"volumeMounts":[{"name":"app","mountPath":"/home"}]}],"volumes":[{"name":"app","hostPath":{"path":"/media/wxy/ubuntu/workspace/app"}}]}}
    # print(body)
    try:
        api_response = v1.create_namespaced_pod(namespace , body)
        print(api_response)
    except ApiException as e:
        print("Exception when calling CoreV1Api->create_namespaced_service: %s\n" % e)

def create_namespaced_service(v1):
    namespace = "default"
    body = {'apiVersion': 'v1', 'kind': 'Service', 'metadata': {'name': 'nginx-service', 'labels': {'app': 'nginx'}}, 'spec': {'ports': [{'port': 80, 'targetPort': 80}], 'selector': {'app': 'nginx'}}}
    try:
        api_response = v1.create_namespaced_service(namespace , body)
        print(api_response)
    except ApiException as e:
        print("Exception when calling CoreV1Api->create_namespaced_service: %s\n" % e)
 
def delete_namespaced_service(v1):
    name = 'nginx-service'                              #要删除svc名称
    namespace = 'default'                               #命名空间
    try:
        api_response = v1.delete_namespaced_service(name, namespace)
        print(api_response)
    except ApiException as e:
        print("Exception when calling CoreV1Api->delete_namespaced_service: %s\n" % e)
 
def read_yaml(path):
    try:
        # 打开文件
        with open(path,"r",encoding="utf-8") as f:
            data=yaml.load(f,Loader=yaml.FullLoader)
            return data
    except:
        return None

    
if __name__ == '__main__':
    init()
    list_pod(None)
    create_namespaced_pod('test.yaml')
    list_pod('default')
    # test()