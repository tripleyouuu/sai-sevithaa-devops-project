# Troubleshooting lab

Each manifest here is broken on purpose. Deploy the main chart first, apply one manifest, then work out what's wrong using only `kubectl`.

## 1. Image that can't be pulled

```bash
kubectl apply -f troubleshooting/broken-image.yaml
kubectl get pods -n syllabus -l app=syllabus-backend-canary
kubectl describe pod -n syllabus -l app=syllabus-backend-canary
kubectl get events -n syllabus --sort-by=.lastTimestamp | tail
```

What you should see: the pod sits in `ErrImagePull` and then `ImagePullBackOff`. In the `describe` events, the kubelet reports that the tag `v9.9.9-does-not-exist` isn't in the registry.

Fix: point the image at a tag that CI actually pushed (a commit SHA from GHCR).

```bash
kubectl set image deployment/syllabus-backend-canary -n syllabus backend=ghcr.io/tripleyouuu/syllabus-backend:<sha>
```

## 2. Service with no endpoints

```bash
kubectl apply -f troubleshooting/broken-service.yaml
kubectl get svc -n syllabus syllabus-backend-lab
kubectl get endpointslices -n syllabus -l kubernetes.io/service-name=syllabus-backend-lab
kubectl get pods -n syllabus --show-labels
```

What you should see: the Service exists and has a ClusterIP, but it has no endpoints. Its selector asks for `app.kubernetes.io/name=syllabus-api`, while the backend pods are labelled `app.kubernetes.io/name=syllabus-backend`. A Service only sends traffic to pods whose labels match its selector, so this one sends traffic nowhere.

Prove it from inside the cluster:

```bash
kubectl run curl -n syllabus --rm -it --image=curlimages/curl --restart=Never -- \
  curl -sS -m 3 http://syllabus-backend-lab:8000/health
```

Fix: change the selector to `syllabus-backend` and apply again.

## 3. Running but never Ready

```bash
IMAGE=$(kubectl get deploy syllabus-backend -n syllabus -o jsonpath='{.spec.template.spec.containers[0].image}')
sed "s|ghcr.io/tripleyouuu/syllabus-backend:latest|$IMAGE|" troubleshooting/broken-readiness.yaml | kubectl apply -f -
kubectl get pods -n syllabus -l app=syllabus-backend-misconfigured
kubectl describe pod -n syllabus -l app=syllabus-backend-misconfigured
kubectl logs -n syllabus -l app=syllabus-backend-misconfigured
```

What you should see: the pod is `Running`, but it stays at `0/1` Ready. Liveness (`/health`) would pass, because the process is up. Readiness (`/ready`) fails because the database password is wrong, so the pod never gets added to a Service. This lab is the reason `/health` and `/ready` are separate endpoints.

Fix: use the `syllabus-db` secret instead of a hard-coded URL.

## Clean up

```bash
kubectl delete -f troubleshooting/
```
