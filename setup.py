from setuptools import setup, find_packages

setup(
    name="artifacter-image-gen",
    version="0.1.9",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["requests", "pillow"],
)
