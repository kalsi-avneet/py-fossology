import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py-fossology",
    version="0.1.1",
    author="Avneet Singh",
    description="Python wrapper around FOSSology's REST API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kalsi-avneet/py-fossology",
    packages=setuptools.find_packages(),
    python_requires='>=3.5',
    install_requires=[
                  'requests==2.22.0',
                    ],
)
