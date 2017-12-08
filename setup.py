from setuptools import setup


setup(
    name='goldshire',
    packages=['goldshire'],
    include_package_data=True,
    install_requires=[
        'flask',
        'pandas',
        'requests',
        'forex-python',
    ],
)
