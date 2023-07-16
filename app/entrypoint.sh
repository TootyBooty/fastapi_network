#!/bin/bash

while ! nc -z postgresql 5432
do
  echo "Failure connected to PostgreSQL"
  sleep 3
done

while ! nc -z memcached 11211
do
  echo "Failure connected to Memcached"
  sleep 3
done


uvicorn main:app --host 0.0.0.0 --port 8000