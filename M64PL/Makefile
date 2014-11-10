all: pipeline.py
	python3 pipeline.py < project-input.0.txt

test: testPipeline.py pipeline.py
	python3 cutest.py testPipeline.py

