"""Bounded optional notification metadata, independent of runtime or display owners."""

from __future__ import annotations

import base64
import hashlib
import json
import re
import uuid

PREFIX = 'x-codex-plus.notification.v1.'
MAX_CATEGORY = 1536
FIELDS = {'v', 'provider', 'host', 'instance', 'thread', 'turn', 'kind', 'body_format'}


def native_id(value):
    if not isinstance(value, str) or len(value) != 36 or str(uuid.UUID(value)) != value:
        raise ValueError('invalid native notification identity')
    return value


def label(value, limit):
    if (not isinstance(value, str) or not value or len(value.encode()) > limit
            or any(ord(char) < 32 or 127 <= ord(char) < 160 for char in value)):
        raise ValueError('invalid notification source label')
    return value


def validate(value):
    if (not isinstance(value, dict) or set(value) != FIELDS or type(value.get('v')) is not int
            or value['v'] != 1 or value.get('provider') != 'codex'
            or value.get('kind') != 'completion' or value.get('body_format') not in {'markdown', 'plain'}):
        raise ValueError('unsupported notification metadata')
    label(value['host'], 63)
    label(value['instance'], 128)
    native_id(value['thread'])
    native_id(value['turn'])
    return value


def metadata(host, instance, thread, turn, *, markdown=True):
    return validate({'v': 1, 'provider': 'codex', 'host': host, 'instance': instance,
                     'thread': thread, 'turn': turn, 'kind': 'completion',
                     'body_format': 'markdown' if markdown else 'plain'})


def encode(value):
    data = json.dumps(validate(value), sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()
    result = PREFIX + base64.urlsafe_b64encode(data).decode().rstrip('=')
    if len(result) > MAX_CATEGORY:
        raise ValueError('notification metadata exceeds bound')
    return result


def decode(value):
    if (not isinstance(value, str) or len(value) > MAX_CATEGORY or not value.startswith(PREFIX)):
        raise ValueError('unsupported notification category')
    raw = value[len(PREFIX):]
    if not re.fullmatch('[A-Za-z0-9_-]+', raw):
        raise ValueError('invalid notification category encoding')
    def unique(pairs):
        result = {}
        for key, item in pairs:
            if key in result:
                raise ValueError('duplicate notification metadata field')
            result[key] = item
        return result
    try:
        parsed = json.loads(base64.urlsafe_b64decode(raw + '=' * (-len(raw) % 4)), object_pairs_hook=unique)
        result = validate(parsed)
        if encode(result) != value:
            raise ValueError('noncanonical notification metadata')
        return result
    except (ValueError, TypeError, UnicodeError, RecursionError) as error:
        raise ValueError('invalid notification metadata') from error


def episode(value):
    value = validate(value)
    return tuple(value[key] for key in ('provider', 'host', 'instance', 'thread', 'turn', 'kind'))


def event_id(value):
    return hashlib.sha256(json.dumps(episode(value), separators=(',', ':')).encode()).hexdigest()
