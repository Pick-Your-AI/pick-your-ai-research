"""Synthetic CD-1 encoding/normalization; not a released contract reader.

An explicit answer state is separate from its value, field type and rule policy.
Callers supply the field's reviewed local schema before using a provided value.
This module reads a test-only sidecar; it never rewrites historical build bytes,
resolves catalog evidence or decides selection activation and compatibility.
"""

from copy import deepcopy
from dataclasses import dataclass
from enum import StrEnum
import json
from pathlib import Path
import re

from jsonschema import Draft202012Validator, ValidationError


SCHEMA_PATH = Path(__file__).with_name("fixtures") / "t0-answer-states.schema.json"
ENCODING = Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))


class State(StrEnum):
    PROVIDED = "provided"
    UNKNOWN = "unknown"
    MISSING = "missing"
    WITHHELD = "withheld"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True, slots=True)
class Answer:
    state: State
    value: object = None
    source: str | None = None
    source_path: str | None = None

    @property
    def provided(self):
        return self.state is State.PROVIDED


def pointer_tokens(pointer):
    """Non-root RFC 6901 string form; never dotted paths or URI fragments."""
    if not isinstance(pointer, str) or re.fullmatch(r"(?:/(?:[^~/]|~[01])*)+", pointer) is None:
        raise ValueError("answer path must be a non-root JSON Pointer")
    return tuple(token.replace("~1", "/").replace("~0", "~") for token in pointer.split("/")[1:])


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate answer JSON key: {key!r}")
        result[key] = value
    return result


class AnswerIndex:
    def __init__(self, raw):
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        document = json.loads(raw, object_pairs_hook=unique_object)
        # Reject accepted-by-Python NaN/Infinity and overflowing JSON numbers.
        json.dumps(document, allow_nan=False)
        try:
            ENCODING.validate(document)
        except ValidationError as error:
            raise ValueError(f"invalid CD-1 answer encoding: {error.message}") from error
        answers = document["x_t0_answer_states"]["answers"]
        self._answers = {
            pointer_tokens(path): (path, deepcopy(answer))
            for path, answer in answers.items()
        }
        for tokens in self._answers:
            if any(tokens[:length] in self._answers for length in range(1, len(tokens))):
                raise ValueError("overlapping parent/child answer paths")

    def read(self, pointer, value_schema):
        """Read a typed fact, preserving unresolved state and source attribution.

        A withheld/unresolved parent covers its descendants. A provided parent
        can supply a nested value; absent members/indices are missing. Invalid
        array syntax or scalar traversal is an input error, never a known false.
        The schema describes the requested field, not the whole parent value.
        """
        tokens = pointer_tokens(pointer)
        for length in range(len(tokens), 0, -1):
            match = self._answers.get(tokens[:length])
            if match is not None:
                break
        else:
            return Answer(State.MISSING)
        source_path, record = match
        state = State(record["state"])
        if state is not State.PROVIDED:
            return Answer(state, source_path=source_path)
        value = record["value"]
        for token in tokens[length:]:
            if isinstance(value, dict):
                if token not in value:
                    return Answer(State.MISSING, source_path=source_path)
                value = value[token]
            elif isinstance(value, list):
                if re.fullmatch(r"0|[1-9][0-9]*", token) is None:
                    raise ValueError("invalid answer array index")
                index = int(token)
                if index >= len(value):
                    return Answer(State.MISSING, source_path=source_path)
                value = value[index]
            else:
                raise ValueError("cannot traverse a scalar answer")
        Draft202012Validator.check_schema(value_schema)
        try:
            Draft202012Validator(value_schema).validate(value)
        except ValidationError as error:
            raise ValueError(f"invalid provided value at {pointer}: {error.message}") from error
        return Answer(state, deepcopy(value), record.get("source"), source_path)

    def predicate(self, pointer, value_schema, predicate):
        """Only provided, field-valid data reaches a rule's value predicate."""
        answer = self.read(pointer, value_schema)
        if not answer.provided:
            return None
        result = predicate(answer.value)
        if result is not True and result is not False and result is not None:
            raise ValueError("predicate must return a normalized bool or None")
        return result
