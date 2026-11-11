from __future__ import annotations

import argparse

from market_recon.rag.cli import _add_store_options


def test_rag_store_options_registered_on_subparser() -> None:
    parser = argparse.ArgumentParser()
    _add_store_options(parser)
    args = parser.parse_args(["--model", "test-model", "--qdrant-path", "index"])
    assert args.model == "test-model"
    assert args.qdrant_path == "index"
