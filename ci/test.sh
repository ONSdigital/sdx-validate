#!/bin/bash

set -e -x

pushd sdx-validate
  make
  make test
popd