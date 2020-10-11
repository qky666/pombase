import setuptools


def read_file(filepath):
    with open(filepath) as f:
        return f.read()


setuptools.setup(
    name='pombase',
    version=read_file("VERSION"),
    description='Page Object Model for SeleniumBase',
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    author='José Torrecilla Álvarez',
    author_email='jose.torrecilla@gmail.com',
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Pytest",
        "Environment :: Web Environment",
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
    ],
    url="https://github.com/qky666/pombase",
    python_requires='>=3.8',
    packages=setuptools.find_packages(),
    # package_data={'pombase.resources': ['*'],
    #               'pombase.resources.template_files': ['*'], },
    # include_package_data=True,
    install_requires=read_file('requirements.txt').splitlines(),
    # entry_points={
    #     'console_scripts': ['pombase=pombase.cli.pombase:pombase_entry']
    # },
    # test_suite="tests"
)
