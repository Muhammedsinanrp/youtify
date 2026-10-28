from setuptools import setup, find_packages

setup(
    name="youtify",
    version="1.0.0",
    description="Elegant Cross-Platform Local Music Player for Windows, macOS, and Linux",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Muhammed Sinan",
    url="https://github.com/Muhammedsinanrp/youtify",
    license="MIT",
    py_modules=["main"],
    install_requires=[
        "PyQt6>=6.5.0",
    ],
    entry_points={
        "console_scripts": [
            "youtify=main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio :: Players",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.9",
)
