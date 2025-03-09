.PHONY: install run clean

install:
	@echo "Installing Tidbyt Renderer software..."
	@chmod -R u+rwx scripts/
	@scripts/install.sh

run:
	@echo "Running Tidbyt Renderer..."
	@scripts/run.sh

clean:
	@echo "Cleaning up installation..."
	@sudo rm -rf __pycache__
	@find . -name "*.pyc" -delete