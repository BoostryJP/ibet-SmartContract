#!/bin/bash
source ~/.bash_profile

cd /app/ibet-SmartContract

# test実施
brownie test --disable-warnings -v --network quorum