from setuptools import find_packages, setup

setup(
    name="comic_matcher",
    version="0.2.1",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.0.0",
        "recordlinkage>=0.15",
        "jellyfish>=0.8.0",
        "scikit-learn>=0.24.0",
        "numpy>=1.19.0",
        "tqdm>=4.50.0",
        "rapidfuzz>=1.0.0",
        "python-Levenshtein>=0.12.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "ruff>=0.1.6",
            "wheel>=0.35.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "comic-matcher=comic_matcher.cli:main",
        ],
    },
    description="Entity resolution for comic book title matching",
    author="Josh Wren",
    author_email="joshisplutar@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.12",
    ],
)
