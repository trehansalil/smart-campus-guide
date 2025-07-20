from setuptools import setup, find_packages

setup(
    name="smart-campus-guide",
    version="1.0.0",
    description="An AI-powered, RAG-based college recommendation system using vector search, GPT, and FastAPI.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Salil Trehan",
    url="https://github.com/trehansalil/smart-campus-guide",
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[],  # Use pyproject.toml & uv for dependency management
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="college recommendation RAG vector search AI FastAPI LLM",
)

