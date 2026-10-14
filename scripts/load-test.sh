#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${NAMESPACE:-syllabus}"
TARGET="${TARGET:-http://syllabus-backend:8000/api/stats}"
WORKERS="${WORKERS:-20}"
DURATION="${DURATION:-180}"

echo "Hitting $TARGET with $WORKERS workers for ${DURATION}s"
echo "In another terminal: kubectl get hpa -n $NAMESPACE -w"

kubectl run load-generator -n "$NAMESPACE" --rm -i --restart=Never \
  --image=busybox:1.36 -- /bin/sh -c "
    end=\$((\$(date +%s) + $DURATION))
    for i in \$(seq 1 $WORKERS); do
      (while [ \$(date +%s) -lt \$end ]; do wget -q -O /dev/null $TARGET; done) &
    done
    wait
    echo done
  "
