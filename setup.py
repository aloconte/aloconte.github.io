from setuptools import setup, find_packages

VERSION = '0.2.0'

setup(
    name="mkdocs-dark",
    version=VERSION,
    url='https://github.com/aloconte/aloconte.github.io',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Topic :: Documentation',
        'Topic :: Text Processing',
    ],
    install_requires=[
        'mkdocs',
    ],
    license='MIT',
    description='MkDocs dark theme focused on navigation and usability',
    author='Ado Loconte',
    author_email='adoloconte@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'mkdocs.themes': [
            'dark = mkdocs_dark',
        ]
    },
    zip_safe=False
)
