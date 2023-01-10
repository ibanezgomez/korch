#from .daemon import Daemon
from utils.logger import log
import os
from os import path
import subprocess
import yaml
from git import Repo

class Deployment:
    repo_url     = ""
    desc         = "Generic description"
    status       = -1
    result       = ""
    name         = ""
    display_name = ""
    deployment_file_path = ""
    service_file_path = ""
    result_path = ""

    def __init__(self, k8s_provider, *kwargs):
        log.info("Loading deployment...")
        self.k8s_provider=k8s_provider
        self.name=kwargs[0]['name']
        self.repo_url=kwargs[0]['repo_url']
        self.display_name=kwargs[0]['display_name']
        self.result_path="tmp/"+self.name
        self.deployment_file_path=self.result_path+"/deployment.yaml"
        self.service_file_path=self.result_path+"/service.yaml"
        self.published_port=kwargs[0]['published_port']
        self.container_port=kwargs[0]['container_port']

        try:
            os.mkdir(self.result_path)
            Repo.clone_from(self.repo_url, self.result_path)
        except:
            log.info("Continue... it exists.")

    def getName(self):
        return self.name
    
    def getDisplayName(self):
        return self.name
    
    def getDescription(self):
        return self.desc
    
    def getStatus(self):
        return self.status

    def getBaseUrl(self):
        return self.baseurl

    def getResult(self):
        return self.result

    def getDeploymentFilePath(self):
        return "/opt/pki/containers/sast_engine/deployment.yaml"

    def run(self):
        if self.onStartDeploy():
            if self.onDeploy():
                if self.setResult(): return self.onDeployFinished()
        return self.onFailureDeploy()

    def setResult(self):
        log.debug('[setResult] %s' % self.getDisplayName())

        # Service tpl create stage
        with open("tmp/base_service.yaml") as f:
            list_doc = yaml.safe_load(f)
            list_doc['metadata']['name']=self.name
            list_doc['metadata']['labels']['name']=self.name
            list_doc['spec']['selector']['name']=self.name
            list_doc['spec']['ports'][0]['port']=self.published_port
            list_doc['spec']['ports'][0]['targetPort']=self.container_port
            with open(self.service_file_path, "w") as f:
                yaml.dump(list_doc, f)

        self.k8s_provider.apply(self.name, self.service_file_path)
        self.result = "Deploy & service finished, time for a beer ;-)"
        return True

    def onStartDeploy(self):
        log.debug('[onStartDeploy] %s' % self.getDisplayName())
        img_name='minikube/'+self.name
        
        # Build stage
        with open("/tmp/build.log", "a") as output:
            subprocess.call("docker build -t "+img_name+" "+self.result_path, shell=True, stdout=output, stderr=output)
        
        # Deployment tpl create stage
        with open("tmp/base_deployment.yaml") as f:
            list_doc = yaml.safe_load(f)
            list_doc['metadata']['name']=self.name
            list_doc['metadata']['labels']['name']=self.name
            list_doc['spec']['selector']['matchLabels']['name']=self.name
            list_doc['spec']['template']['metadata']['labels']['name']=self.name
            list_doc['spec']['template']['spec']['containers'][0]['name']=self.name
            list_doc['spec']['template']['spec']['containers'][0]['image']=img_name
            list_doc['spec']['template']['spec']['containers'][0]['ports'][0]['containerPort']=self.container_port

            with open(self.deployment_file_path, "w") as f:
                yaml.dump(list_doc, f)

        # Load stage  
        with open("tmp/build.log", "a") as output:
            subprocess.call("minikube image load "+img_name, shell=True, stdout=output, stderr=output)

        return True

    def onDeploy(self):
        log.debug('[onDeploy] %s' % self.getDisplayName())
        self.k8s_provider.deploy(self.name, self.deployment_file_path)
        return True
    
    # Status values:
    #   -1 - Configuring job
    #    0 - Finished with error
    #    1 - In progresss
    #    2 - Finished with success
    def setDeployStatus(self, status):
        log.debug('[setDeployStatus] %s' % self.getDisplayName())
        self.status=status
        return True

    def onDeployFinished(self):
        log.info('[onFinishedScan] %s' % self.getDisplayName())
        self.setDeployStatus(2)
        return True

    def onFailureDeploy(self):
        log.error('[onFailureScan] %s' % display_name)
        self.setDeployStatus(0)
        return True

