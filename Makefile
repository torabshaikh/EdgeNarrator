CUDA_ARCH ?= $(shell nvidia-smi --query-gpu=compute_cap --format=csv,noheader | tr -d '.')

# Note: uv sync installs a CPU-only llama-cpp-python from the lockfile.
# The second step rebuilds it with CUDA. Run 'make install' / 'make install-jetson'
# instead of plain 'uv sync' to keep the CUDA build active.

install:
	uv sync
	CMAKE_ARGS="-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=$(CUDA_ARCH)" \
	  uv pip install llama-cpp-python --force-reinstall --no-cache-dir

install-jetson:
	uv sync
	CMAKE_ARGS="-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=87" \
	  uv pip install llama-cpp-python --force-reinstall --no-cache-dir
