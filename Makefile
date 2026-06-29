.PHONY: auto-loop score validate

auto-loop:
	python -m auto_research.auto_loop

validate:
	python -m python.validate_metrics

score:
	python -m python.score
