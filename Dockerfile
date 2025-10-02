# Step 1 : Build the environment with dependencies
FROM python:3.10 AS builder

ENV PYTHONUNBUFFERED=1

WORKDIR /oceanprotocol_job_details/

# Install uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# Place executables in the environment at the front of the path
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment
ENV PATH="/oceanprotocol_job_details/.venv/bin:$PATH"

# Compile bytecode
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# uv Cache
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

# Install dependencies
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

FROM python:3.10-slim

WORKDIR /oceanprotocol_job_details

# Copy the oceanprotocol_job_details code (with the same depth)
COPY --from=builder /oceanprotocol_job_details/.venv /oceanprotocol_job_details/.venv
COPY oceanprotocol_job_details/ /oceanprotocol_job_details/oceanprotocol_job_details
COPY pyproject.toml /oceanprotocol_job_details/pyproject.toml
COPY tests /oceanprotocol_job_details/tests

WORKDIR /oceanprotocol_job_details

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV PATH="/oceanprotocol_job_details/.venv/bin:$PATH"

# Check if running dev & tests
CMD ["pytest", "-v"]