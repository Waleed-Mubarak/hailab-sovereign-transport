from setuptools import setup, find_packages

setup(
    name="hailab-sovereign-transport",
    version="1.0.0",
    packages=find_packages(exclude=["tests*"]),
    py_modules=[
        "wp6_pqc_layer",
        "cbt_compatibility_layer",
        "cryptography_security_layer",
        "sovereign_transport_kernel",
        "ai_sovereign_bridge",
        "audit_verifier",
        "chaos_sim",
        "hailab_sovereign",
        "sim"
    ],
    install_requires=[
        "pytest",
    ],
)
