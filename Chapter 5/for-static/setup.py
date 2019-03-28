import setuptools

setuptools.setup(
    name='static_server',
    license='MIT',
    description="Server: Static",
    long_description="Static, the web server",
    version="0.0.1",
    author="Moshe Zadka",
    author_email="zadka.moshe@gmail.com",
    packages=setuptools.find_packages(where='src') + ['twisted/plugins'],
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=['twisted', 'setuptools'],
)
