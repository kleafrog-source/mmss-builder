.PHONY: auto-loop auto-loop-ollama auto-stop auto-ui score validate

auto-loop:
	python -m auto_research.auto_loop

auto-loop-ollama:
	python -m auto_research.auto_loop --use-ollama

auto-stop:
	New-Item -ItemType File -Force auto_research/stop.flag | Out-Null

validate:
	python -m python.validate_metrics

score:
	python -m python.score

auto-ui:
	python -m auto_research.run_ui
