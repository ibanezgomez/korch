IFS="
"
for i in `docker images | grep -e 'minikube/' -e '<none>' | awk '{print $3}'`; do docker image rm $i; done
for d in `kubectl get deployments | awk '{print $1}' | grep -v NAME`; do kubectl delete deployment $d; done 
for p in `kubectl get pods | awk '{print $1}' | grep -v NAME`; do kubectl delete pod $p; done 
for s in `kubectl get services | awk '{print $1}' | grep -v NAME`; do kubectl delete service $s; done 
for s in `kubectl get jobs | awk '{print $1}' | grep -v NAME`; do kubectl delete job $s; done 