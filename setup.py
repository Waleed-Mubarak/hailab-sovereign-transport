from setuptools import setup

setup(
    name="hailab-sovereign-transport",
    version="1.0.0",
    py_modules=[
        "wp2_sim",
        "wp3_sim",
        "wp6_pqc_layer",
        "cbt_compatibility_layer",
        "cryptographic_security_layer",
        "sovereign_transport_kernel",
        "ai_sovereign_bridge",
        "audit_verifier",
        "chaos_sim",
        "hailab_sovereign",
        "sim",
    ],
    install_requires=[
        "pytest",
    ],
)
