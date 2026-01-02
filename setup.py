from setuptools import setup, find_packages

setup(
    name="robby",
    version="0.1.0",
    description="Autonomous Development Conductor for QuietBuild OS",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "test": ["pytest>=7.4.0"],
    },
)
