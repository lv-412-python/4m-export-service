#!/bin/bash
set -e

until timeout 1 bash -c "cat < /dev/null > /dev/tcp/rabbitmq/5672"; do
  >&2 echo "Rabbit MQ not up yet on rabbitmq"
  sleep 10
done

echo "Rabbit MQ is up"

# do something
PYTHONPATH="${PYTHONPATH}:/export_service"
export PYTHONPATH

python3 setup.py
sleep infinity
