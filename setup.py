from setuptools import setup, find_packages

setup(
    name="rnd_nutrition",
    version="0.0.1",
    description="RND Nutrition App for ERPNext",
    author="Your Name",
    author_email="your@email.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "frappe",
    ],
)
# Add setup.py to each repository's root
echo "from setuptools import setup, find_packages
setup(
    name='repo_name',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['frappe']
)" > setup.py
