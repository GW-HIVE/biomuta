from setuptools import find_packages, setup  # type: ignore


def main():

    setup(
        name="biomuta",
        version="1.0",
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,
        install_requires=["flask"],
    )


if __name__ == "__main__":
    main()