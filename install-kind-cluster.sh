#!/bin/bash

kind create cluster --config=kind-config.yaml  --name my-cluster

kubectl cluster-info --context kind-my-cluster

helm repo add cilium https://helm.cilium.io/

export TMPDIR=$HOME/tmp
docker pull quay.io/cilium/cilium:v1.16.1
kind load  docker-image quay.io/cilium/cilium:v1.16.1  --name=my-cluster

helm install cilium cilium/cilium --version 1.16.1 \
   --namespace kube-system \
   --set image.pullPolicy=IfNotPresent \
   --set ipam.mode=kubernetes


cilium hubble enable --ui

cilium status --wait
