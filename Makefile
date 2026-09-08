# FPI_SUBSCRIBER_LAUNCH_RC5 build and test entry points (see README.md / START_HERE.md)
.PHONY: build test serve preview clean
build:
	python3 build/extract.py && python3 build/build.py && python3 hosting/render-host-configs.py
serve:
	@echo "Terminal 1: node server/mock-kit.mjs"; echo "Terminal 2: set -a; . ./tests/test.env; set +a; node server/dev-server.mjs"; echo "Terminal 3: python3 tests/serve.py --port=8765 --api=http://127.0.0.1:8780 --xff-per-request"
test:
	python3 tests/run_tests.py
preview:
	python3 tests/make_preview.py PREVIEW_single_file_NONPRODUCTION_RC5.html RC5
clean:
	rm -rf dist src tests/results
