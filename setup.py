import setuptools

setuptools.setup(name='pslabs',
    version='0.1',
    description='Use PS3 controller to drive throlabs controller',
    #url='http://github.com/rwalle/py_thorlabs_ctrl',
    #author='',
    #author_email='',
    #license='',
    packages=setuptools.find_packages(),
    install_requires=['pygame','py_thorlabs_ctrl'],
    #test_suite='tests',
    )