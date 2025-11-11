"""
UltraCore Banking Platform Setup
"""

from setuptools import setup, find_packages

# Read version
with open("src/ultracore/__init__.py") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break

# Read README
try:
    with open("README.md", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "UltraCore Banking Platform"

setup(
    name="ultracore",
    version=version,
    description="AI-Native Core Banking Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="UltraCore Team",
    author_email="info@ultracore.com",
    url="https://github.com/ultracore/ultracore",
    license="Proprietary",
    
    # Package configuration
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    
    # Python version
    python_requires=">=3.10",
    
    # Dependencies
    install_requires=[
        # Core
        "python-dateutil>=2.8.2",
        
        # Async
        "asyncio>=3.4.3",
        
        # Graph
        "networkx>=3.0",
        
        # ML/AI (optional but recommended)
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0",
        "pandas>=2.0.0",
        
        # Data validation
        "pydantic>=2.0.0",
        
        # Utils
        "python-dotenv>=1.0.0",
    ],
    
    # Optional dependencies
    extras_require={
        "api": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "pydantic>=2.0.0",
        ],
        "database": [
            "sqlalchemy>=2.0.0",
            "psycopg2-binary>=2.9.0",
            "alembic>=1.12.0",
        ],
        "graph": [
            "neo4j>=5.14.0",
        ],
        "ml": [
            "numpy>=1.24.0",
            "scikit-learn>=1.3.0",
            "pandas>=2.0.0",
            "xgboost>=2.0.0",
            "tensorflow>=2.14.0",  # For LSTM
        ],
        "monitoring": [
            "prometheus-client>=0.18.0",
            "opentelemetry-api>=1.21.0",
            "opentelemetry-sdk>=1.21.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.10.0",
            "flake8>=6.1.0",
            "mypy>=1.6.0",
        ],
    },
    
    # Entry points
    entry_points={
        "console_scripts": [
            "ultracore=ultracore.cli:main",
        ],
    },
    
    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
    ],
    
    # Include package data
    include_package_data=True,
    zip_safe=False,
)
