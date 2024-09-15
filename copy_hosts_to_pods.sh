#!/bin/bash

# Check if namespace is provided as an argument
if [ -z "$1" ]; then
    echo "Usage: $0 <namespace>"
    exit 1
fi

# Set the namespace from the first argument
NAMESPACE=$1

# Path to the file to be copied
FILE_TO_COPY="hosts.txt"

# Destination path inside the pods
DESTINATION_PATH="hosts.txt"  # Change this to the desired path inside the pod

# Get the list of pod names in the specified namespace
pods=$(kubectl get pods -n $NAMESPACE -o jsonpath="{.items[*].metadata.name}")

# Loop through each pod and copy the file
for pod in $pods; do
    echo "Copying $FILE_TO_COPY to $pod in namespace $NAMESPACE"
    kubectl cp $FILE_TO_COPY $NAMESPACE/$pod:$DESTINATION_PATH
    if [ $? -eq 0 ]; then
        echo "Successfully copied $FILE_TO_COPY to $pod"
    else
        echo "Failed to copy $FILE_TO_COPY to $pod"
    fi
done

