export MATCHA := $(shell pwd)
export MATCHA_LIB := $(shell pwd)/matcha/std
export CLASSPATH := .:$(shell pwd)

all-tests: test cram

test:
	python3 -mnose tests --with-coverage -s

cram:
	cram examples/*.t
