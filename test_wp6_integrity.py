# tests/test_wp6_integrity.py
import pytest
import hmac
import hashlib
from wp6_pqc_layer import SovereignIntegrityEnvelope, process_integrity_bundle

def test_integrity_envelope_signing():
    envelope = SovereignIntegrityEnvelope("node-01", b"shared_secret_32_bytes_long_secure_key")
    payload = b"test_payload_data"
    
    signature = envelope.sign_bundle(payload)
    assert envelope.verify_bundle(payload, signature) is True

def test_integrity_envelope_failure():
    envelope = SovereignIntegrityEnvelope("node-01", b"shared_secret_32_bytes_long_secure_key")
    payload = b"test_payload_data"
    bad_signature = b"invalid_signature_bytes"
    
    assert envelope.verify_bundle(payload, bad_signature) is False

def test_process_integrity_bundle_fail_closed():
    result = process_integrity_bundle(
        "node-01",
        b"shared_secret_32_bytes_long_secure_key",
        b"payload",
        b"wrong_sig"
    )
    assert result == "FAIL_CLOSED_ABORT"

def test_process_integrity_bundle_success():
    envelope = SovereignIntegrityEnvelope("node-01", b"shared_secret_32_bytes_long_secure_key")
    payload = b"payload"
    sig = envelope.sign_bundle(payload)
    
    result = process_integrity_bundle(
        "node-01",
        b"shared_secret_32_bytes_long_secure_key",
        payload,
        sig
    )
    assert result == "SECURE_INTEGRITY_ACCEPTED"

