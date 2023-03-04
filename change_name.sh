#!/bin/bash

find . -type f -name '*.py' -exec sed -i '' s/DIPL/DIP/g {} +
find . -type f -name '*.py' -exec sed -i '' s/dipl/dip/g {} +
find . -type f -name '*.rst' -exec sed -i '' s/DIPL/DIP/g {} +
find . -type f -name '*.rst' -exec sed -i '' s/dipl/dip/g {} +
rename 's/dipl/dip/g' tests/blocks/*
rename 's/DIPL/DIP/g' src/lexer/*
rename 's/DIPL/DIP/g' src/*
