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

FROM python:3.10.0-slim-bullseye

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
