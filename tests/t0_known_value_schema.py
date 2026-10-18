"""Test-only CD-1 known-value schema profile; not a production field registry.

Finite enum/const declarations cannot make the answer-state marker a known
value. Free text and property names retain ordinary JSON Schema semantics.
The profile admits document-local pointer references and explicit finite `not`
exclusions; it does not try to decide arbitrary schema equivalence.
"""

import json
import re
from urllib.parse import unquote

from jsonschema import Draft202012Validator


_SCHEMA_MAPS = {"$defs", "properties", "patternProperties", "dependentSchemas"}
_SCHEMA_ARRAYS = {"allOf", "anyOf", "oneOf", "prefixItems"}
_SCHEMA_VALUES = {"items", "contains", "additionalProperties", "unevaluatedProperties",
                  "unevaluatedItems", "if", "then", "else", "not", "propertyNames"}


def _profile_keywords(node, root):
    if isinstance(node, bool):
        return
    if "$schema" in node and node["$schema"] not in (
        "https://json-schema.org/draft/2020-12/schema",
        "https://json-schema.org/draft/2020-12/schema#",
    ):
        raise ValueError("invalid known-value schema: only the 2020-12 dialect is admitted")
    if "$dynamicRef" in node or (node is not root and "$id" in node):
        raise ValueError("invalid known-value schema: dynamic or nested-resource references are not admitted")


def _unknown_value(value):
    """Inspect literal values, including structured enums, without treating keys as values."""
    if isinstance(value, str):
        return value == "unknown"
    if isinstance(value, list):
        return any(_unknown_value(item) for item in value)
    if isinstance(value, dict):
        return any(_unknown_value(item) for item in value.values())
    return False


def _local_reference(root, reference):
    if not reference.startswith("#") or re.search(r"%(?![0-9a-fA-F]{2})", reference):
        raise ValueError("invalid known-value schema: only local JSON Pointer references are admitted")
    try:
        pointer = unquote(reference[1:], encoding="utf-8", errors="strict")
    except UnicodeError as error:
        raise ValueError("invalid known-value schema: reference is not valid UTF-8") from error
    if pointer == "":
        return root
    if not pointer.startswith("/") or re.search(r"~(?![01])", pointer):
        raise ValueError("invalid known-value schema: reference is not a JSON Pointer")
    target = root
    location = "schema"
    for encoded in pointer.split("/")[1:]:
        token = encoded.replace("~1", "/").replace("~0", "~")
        if location == "schema":
            # A pointer jump still crosses resource-bearing schema ancestors.
            # Schema maps may have literal '$id' keys; those are entry names.
            _profile_keywords(target, root)
            if token in _SCHEMA_MAPS:
                next_location = "map"
            elif token in _SCHEMA_ARRAYS:
                next_location = "array"
            elif token in _SCHEMA_VALUES:
                next_location = "schema"
            else:
                raise ValueError("invalid known-value schema: reference leaves supported schema locations")
        else:
            next_location = "schema"
        if isinstance(target, dict) and token in target:
            target = target[token]
        elif isinstance(target, list) and re.fullmatch(r"0|[1-9][0-9]*", token):
            index = int(token)
            if index >= len(target):
                raise ValueError("invalid known-value schema: reference target is absent")
            target = target[index]
        else:
            raise ValueError("invalid known-value schema: reference target is absent")
        location = next_location
    if location != "schema" or not isinstance(target, (dict, bool)):
        raise ValueError("invalid known-value schema: reference target is not a schema")
    return target


def known_value_validator(schema):
    """Validate the local profile before a provided value can reach a predicate.

    Reject the vocabulary itself even if this particular value is known. Leave
    all caller objects untouched. Definitions are inspected when referenced;
    annotations and unused definitions are not declarations for this field.
    """
    try:
        json.dumps(schema, allow_nan=False)
    except (TypeError, ValueError, RecursionError) as error:
        raise ValueError("invalid known-value schema: a finite JSON document is required") from error
    Draft202012Validator.check_schema(schema)
    stack = [(schema, False, False)]
    seen = set()
    while stack:
        node, inside_not, names_only = stack.pop()
        if isinstance(node, bool):
            continue
        identity = (id(node), inside_not, names_only)
        if identity in seen:
            continue
        seen.add(identity)
        _profile_keywords(node, schema)
        if not names_only:
            for keyword in ("enum", "const"):
                if keyword in node and _unknown_value(node[keyword]):
                    raise ValueError("invalid known-value schema: finite values cannot include answer-state 'unknown'")
        if "$ref" in node:
            stack.append((_local_reference(schema, node["$ref"]), inside_not, names_only))
        for keyword in ("properties", "patternProperties", "dependentSchemas"):
            stack.extend((child, inside_not, names_only) for child in node.get(keyword, {}).values())
        for keyword in ("allOf", "anyOf", "oneOf", "prefixItems"):
            stack.extend((child, inside_not, names_only) for child in node.get(keyword, []))
        for keyword in ("items", "contains", "additionalProperties", "unevaluatedProperties",
                        "unevaluatedItems", "if", "then", "else"):
            if keyword in node:
                stack.append((node[keyword], inside_not, names_only))
        if "propertyNames" in node:
            stack.append((node["propertyNames"], inside_not, True))
        if "not" in node:
            excluded = node["not"]
            direct_finite_exclusion = isinstance(excluded, dict) and set(excluded) in (
                {"enum"}, {"const"},
            )
            # A pure exclusion forbids its literals. Inside another negation it
            # may admit them again; compound forms need a reviewed field rewrite.
            if inside_not or not direct_finite_exclusion:
                stack.append((excluded, True, names_only))
    return Draft202012Validator(schema)
