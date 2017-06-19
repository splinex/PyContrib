# jenkins_build.sh -- jenkins build script

find . -regex "\(.*__pycache__.*\|*.py[co]\)" -delete
python3 ./setup.py sdist

version=`python3 ./setup.py --version`
cp ./dist/pycontrib-${version}.tar.gz /mnt/releases/
