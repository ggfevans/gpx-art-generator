from setuptools import setup, find_packages

setup(
    name="gpx-art",
    version="0.1.0",
    description="Transform GPS routes into artwork",
    author="GPX Art Generator Team",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.0",
        "gpxpy>=1.6.0",
    ],
    entry_points={
        'console_scripts': [
            'gpx-art=gpx_art.main:cli',
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

