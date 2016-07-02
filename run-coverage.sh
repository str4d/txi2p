#!/bin/bash
. env/bin/activate
coverage run --branch --source=txi2p --omit=*/_version.py,*test* env/bin/trial txi2p
coverage html -d coverage
