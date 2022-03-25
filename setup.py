import setuptools

with open('README.md', 'r') as f:
    readme = f.read()

setuptools.setup(
    name='namegen',
    version='2.0.0',
    author='joniumGit',
    author_email='52005121+joniumGit@users.noreply.github.com',
    description='LCG Based Username Generator',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/joniumGit/namegen',
    packages=['namegen', 'namegen.server'],
    package_dir={
        '': 'src'
    },
    python_requires='>=3.7',
    extras_require={
        'dev': [
            'fastapi',
            'uvicorn',
            'requests',
            'pytest',
            'pytest-cov'
        ],
        'runnable': [
            'fastapi',
            'uvicorn'
        ]
    }
)
