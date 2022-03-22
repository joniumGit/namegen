import setuptools

with open('README.md', 'r') as f:
    readme = f.read()

setuptools.setup(
    name='namegen',
    version='1.0.0',
    author='joniumGit',
    author_email='52005121+joniumGit@users.noreply.github.com',
    description='LCG Based Username Generator',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/joniumGit/namegen',
    packages=['namegen'],
    package_dir={
        '': 'src'
    },
    python_requires='>=3.9',
    install_requires=[
        'fastapi',
    ],
    extras_require={
        'dev': [
            'uvicorn',
            'requests',
            'pytest',
            'pytest-cov'
        ],
        'runnable': [
            'uvicorn'
        ]
    }
)
