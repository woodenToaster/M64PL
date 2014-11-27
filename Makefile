all: pipeline.py
	python3 pipeline.py < project-input.0.txt

main: pipeline.py main.py
	python3 main.py
	
test: testPipeline.py pipeline.py
	python3 cutest.py -v testPipeline.py

