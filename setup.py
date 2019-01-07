from setuptools import setup

setup(
    name="rannotation",
    version="0.1",
    description="rectangle annotation tool for object detection dataset creation",
    keywords="cnn objectdetection annotation image",
    url="https://github.com/kznovo/rectangle-annotation",
    author="Kazuya Hatta",
    author_email="kazuya.hatta@gmail.com",
    license="MIT",
    packages=["rannotation"],
    install_requires=[
        "opencv-python"
    ],
    entry_points = {
        "console_scripts": ["rannotate=rannotation:main"]
    },
    zip_safe=False
)