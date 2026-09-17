EXPERIMENTS := $(sort $(notdir $(wildcard experiments/*)))

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

.PHONY: list
list: ## List the experiments and what each one asks
	@for dir in experiments/*/; do \
		name=$$(basename "$$dir"); \
		question=$$(head -1 "$$dir/README.md" | sed 's/^# //'); \
		status=$$(grep -m1 '^\*\*Status:\*\*' "$$dir/README.md" | sed 's/\*\*Status:\*\* //'); \
		printf "  \033[36m%-32s\033[0m %s\n      %s\n" "$$name" "$$question" "$$status"; \
	done

.PHONY: all
all: ## Run every experiment, in order
	@failed=0; \
	for dir in experiments/*/; do \
		name=$$(basename "$$dir"); \
		printf '\n\033[1m=== %s ===\033[0m\n' "$$name"; \
		./$$dir/run.sh || failed=$$((failed + 1)); \
	done; \
	if [ "$$failed" -gt 0 ]; then \
		printf '\n\033[31m%d experiment(s) failed.\033[0m\n' "$$failed"; exit 1; \
	fi; \
	printf '\n\033[32mEvery experiment passed.\033[0m\n'

.PHONY: run
run: ## Run one experiment: make run N=001
	@dir=$$(echo experiments/$(N)-*/ | head -1); \
	[ -d "$$dir" ] || { echo "no experiment matching '$(N)'"; exit 1; }; \
	./$$dir/run.sh

.PHONY: reproduce
reproduce: ## Rebuild a recorded run's code and replay it: make reproduce RUN=run-id
	@[ -n "$(RUN)" ] || { echo "name the run: make reproduce RUN=run-id"; exit 1; }
	lib/reproduce.sh $(RUN)

.PHONY: sweep
sweep: ## Run a sweep and write its report: make sweep S=intent-modes
	@[ -n "$(S)" ] || { echo "name the sweep: make sweep S=name (one of: $$(ls sweeps/*.json | xargs -n1 basename | sed 's/.json//' | tr '\n' ' '))"; exit 1; }
	lib/sweep.sh sweeps/$(S).json

.PHONY: sweeps
sweeps: ## Run every sweep, in order
	@for s in sweeps/*.json; do lib/sweep.sh "$$s" || exit 1; done

.PHONY: report
report: ## Rewrite a sweep's report from what it recorded: make report S=intent-modes
	python3 lib/sweep.py report reports/$(S)

.PHONY: lint
lint: ## shellcheck every script
	shellcheck lib/harness.sh lib/reproduce.sh lib/sweep.sh experiments/*/run.sh
