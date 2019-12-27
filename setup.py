import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="thon",
    version="0.0.1",
    author="emuggie",
    author_email="emuggie@gmail.com",
    description="Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/emuggie/thon",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3.0",
        "Operating System :: OS Independent",
    ],
    entry_point = {
        # 'console_scripts' : ['run=pworm.server:run']
    },
    python_requires='>=3.5',
)