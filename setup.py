from setuptools import setup, find_packages

setup(
    name="powerpyro",
    version="0.5.0",
    packages=find_packages(),
    install_requires=["pythonnet>=3.0.5",],
    author="Alexandre Bezerra de Lima, Ryann Carlos de Arruda Quintino",
    author_email="alexandrebezerra3207@gmail.com",
    maintainer="Alexandre Bezerra de Lima, Ryann Carlos de Arruda Quintino",
    maintainer_email="alexandrebezerra3207@gmail.com, ryann.arrudasc@gmail.com",
    description="", # TODO: To add
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ryann-arruda/powerpyro",
    classifiers=[

    ],
    python_requires=">=3.12",
)