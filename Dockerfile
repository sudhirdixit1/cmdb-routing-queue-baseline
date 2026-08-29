# A pinned environment for the whole reproduction.
#
# Round sixteen found that a BLAS thread-count change moved a bootstrap
# percentile, and verify_paper.py tests rounding EQUALITY at the printed
# precision rather than a tolerance.  Pinning versions is therefore not
# enough: this image pins the interpreter, the artefact hashes, and the
# thread counts of every BLAS backend the stack can pick up.
#
#   docker build -t emptycmdb .
#   docker run --rm -v "$PWD/data:/work/data" -v "$PWD/results:/work/results" \
#              -v "$PWD/figures:/work/figures" emptycmdb
#
# The data volume is mounted rather than baked in: nothing in this repository
# redistributes anybody's data.  scripts/fetch_corpus.py downloads it by DOI
# on first run and records a SHA-256 for every file.

# THE BASE IS PINNED BY DIGEST, NOT BY TAG.  A tag is mutable: `python:
# 3.10.0-slim-bullseye` can be rebuilt against a new Debian snapshot and the
# same Dockerfile then produces a different image, which is precisely the
# failure the rest of this file exists to prevent.  The digest below is the
# multi-architecture manifest list, so `docker build` still selects the right
# platform while the CONTENT is fixed.  Re-resolve it with:
#
#   docker buildx imagetools inspect python:3.10.0-slim-bullseye
#
FROM python:3.10.0-slim-bullseye@sha256:ad540a471260fee5e5e1a99ee2acf142efe8c279a7a54315160d8033ba88f0d8

# Single-threaded BLAS.  This is the difference between a bit-identical
# bootstrap percentile and one that moves with the host's core count.
ENV OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 \
    VECLIB_MAXIMUM_THREADS=1 \
    PYTHONHASHSEED=0 \
    PYTHONUNBUFFERED=1 \
    TZ=UTC

WORKDIR /work

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.lock /work/requirements.lock
RUN python -m pip install --no-cache-dir --upgrade "pip==24.0" \
 && python -m pip install --no-cache-dir --require-hashes \
        -r /work/requirements.lock

COPY scripts /work/scripts
COPY paper /work/paper
COPY PROTOCOL.md REPRODUCE.md README.md /work/

CMD ["python", "scripts/reproduce_all.py"]
