import re
import string
from contextlib import contextmanager
import os
import uuid
from opentelemetry import trace
from enum import Enum


tracer = trace.get_tracer(__name__)

def normalize_text(text: str) -> str:
    """Lower text and remove punctuation, articles and extra whitespace.
    Copied from the [QuAC](http://quac.ai/) evaluation script found at
    https://s3.amazonaws.com/my89public/quac/scorer.py"""

    def remove_articles(text: str) -> str:
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def white_space_fix(text: str) -> str:
        return " ".join(text.split())

    def remove_punc(text: str) -> str:
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def lower(text: str) -> str:
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(text))))

#########################################################
######## Context Managers, Copy from deepeval############
#########################################################

TELEMETRY_DATA_FILE = ".deepeval_telemtry.txt"

class Feature(Enum):
    REDTEAMING = "redteaming"
    SYNTHESIZER = "synthesizer"
    EVALUATION = "evaluation"
    GUARDRAIL = "guardrail"
    BENCHMARK = "benchmark"
    UNKNOWN = "unknown"


def telemetry_opt_out():
    return os.getenv("DEEPEVAL_TELEMETRY_OPT_OUT") == "YES"

def get_unique_id(file_path=TELEMETRY_DATA_FILE):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = f.read().strip().split("\n")
            unique_id = data[0] if len(data) > 0 else str(uuid.uuid4())
    else:
        unique_id = str(uuid.uuid4())
        # Initialize the file with the new unique ID and unknown feature
        with open(file_path, "w") as f:
            f.write(f"{unique_id}\n{Feature.UNKNOWN.value}")
    return unique_id


def get_last_feature(file_path=TELEMETRY_DATA_FILE):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = f.read().strip().split("\n")
            last_feature = data[1] if len(data) > 1 else Feature.UNKNOWN.value
            return (
                Feature(last_feature)
                if last_feature in Feature._value2member_map_
                else Feature.UNKNOWN
            )
    else:
        return Feature.UNKNOWN


def set_last_feature(feature: Feature, file_path=TELEMETRY_DATA_FILE):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = f.read().strip().split("\n")
            unique_id = data[0]  # Keep the existing unique_id
    else:
        unique_id = str(uuid.uuid4())

    with open(file_path, "w") as f:
        f.write(f"{unique_id}\n{feature.value}")

@contextmanager
def capture_benchmark_run(benchmark: str, num_tasks: int):
    if not telemetry_opt_out():
        with tracer.start_as_current_span("Ran benchmark") as span:
            span.set_attribute("user.unique_id", get_unique_id())
            span.set_attribute("benchmark", benchmark)
            span.set_attribute("num_tasks", num_tasks)
            set_last_feature(Feature.BENCHMARK)
            yield span
    else:
        yield


