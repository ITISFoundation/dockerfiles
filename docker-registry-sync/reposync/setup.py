import re
import sys
from pathlib import Path

from setuptools import find_packages, setup

current_dir = Path(sys.argv[0] if __name__ == "__main__" else __file__).resolve().parent


def read_reqs(reqs_path: Path):
    return re.findall(r"(^[^#-][\w]+[-~>=<.\w]+)", reqs_path.read_text(), re.MULTILINE)


# -----------------------------------------------------------------
# Hard requirements on third-parties and latest for in-repo packages
install_requirements = read_reqs(current_dir / "requirements" / "base.txt")
test_requirements = read_reqs(current_dir / "requirements" / "test.txt")

setup(
    name="reposync",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src",},
    include_package_data=True,
    entry_points={"console_scripts": ["run-reposync=reposync.main:main",]},
    python_requires=">=3.7",
    install_requires=install_requirements,
    tests_require=test_requirements,
    setup_requires=["pytest-runner"],
)
