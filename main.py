#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim :set tabstop=4 expandtab shiftwidth=4 softtabstop=4

import os, signal, time, json
from subprocess import *
from datetime import date, datetime

from utils.asciiart.art import *
from utils.logger import log
from utils.daemon import Daemon
from utils.scheduler import Job, Scheduler
from utils.server import Server
from modules.deployment import Deployment

CFG_FILE="config.json"

def signal_handler(signal, frame):
    # ToDo: Clean everithing
    log.debug("Exiting...")
    exit(0)

def deploymentsChecker():
    for d in config['deployments']:
        log.info("Status of %s: %s" % (deployments[d].getDisplayName(), deployments[d].getStatus()))
    return True

def deploymentsAreWorking():
    res=False
    for d in config['deployments']:
        status=deployments[d].getStatus()
        if status not in [0, 2]: 
            res=True
            break
    return res

def deploymentsHaveFinished():
    for d in config['deployments']:
        log.info("Result of %s: %s" %(deployments[d].getDisplayName(),  deployments[d].getResult()))
    return True

if __name__ == "__main__":
    with open(CFG_FILE) as c:
        config=json.load(c)
        scheduler = Scheduler()
        scheduler.start()
        signal.signal(signal.SIGINT, signal_handler)
        print(text2art('-----------------\n   Korcholis...  is  ' + config['general']['name'] + " !!!" + '\n-----------------'))
        log.debug("Starting %s v%s" % (config['general']['name'], config['general']['version']))
        #server = Server()
        log.info("Loading K8s provider: %s", config['kubernetes']['library'])
        k8s_provider= __import__('modules.' + config['kubernetes']['library'], fromlist=[config['kubernetes']['library']]).K8sProvider(config['kubernetes']['config'])
        deployments = {}
        for d in config['deployments']:
            log.info("Loading deployment id: %s", d)
            deployment_config=config['deployments'][d]
            deployment_config["name"]=d
            deployments[d] = Deployment(k8s_provider, config['deployments'][d])
            Daemon(deployments[d].run).start()
        scheduler.addJob('DeploymentChecker', Job(deploymentsChecker, {}, min=range(0, 60, 1)))  # se ejecuta cada 1 minuto
        while deploymentsAreWorking(): 
            log.info("Waiting to finish...")
            time.sleep(10)  
        log.info("All the deployments have finished")
        scheduler.deleteJob('DeploymentChecker')
        deploymentsHaveFinished()
    exit()