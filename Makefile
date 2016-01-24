all-tests: test cram

test:
	python3 -mnose tests --with-coverage -s

cram:
	cram examples/*.t
