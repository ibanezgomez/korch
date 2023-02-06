from utils.logger import log
from kubernetes import client, config, utils
import yaml

class K8sProvider:

    driver=None

    def __init__(self, *kwargs):
        log.info("Starting K8s connection")
        try:
            #config.load_kube_config(config_file=kwargs[0]['kubeconfig'])
            config.load_kube_config()
            self.driver = client
            log.info("Loaded cluster: "+str(self.getName()))
        except:
            log.error("Unable to load K8s driver")
            exit()

    def getPods(self):
        return self.driver.list_pod_for_all_namespaces(watch=False)
            
    def getName(self):
        return config.list_kube_config_contexts()[0][0]['name']
    
    def apply(self, name, deployment_file):
        log.info("Deploying "+name+" - "+deployment_file+"...")
        utils.create_from_yaml( self.driver.ApiClient(), deployment_file)

    #def deploy(self, name, deployment_file):
    #    log.info("Deploying "+name+"...")
    #    with open(deployment_file) as f:
    #        dep = yaml.safe_load(f)
    #        resp = self.driver.AppsV1Api().create_namespaced_deployment(body=dep, namespace="default")
    #        log.info("Deployment created. status='%s'" % resp.metadata.name)
