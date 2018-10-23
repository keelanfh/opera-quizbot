#!/bin/bash

echo "Installing command line tools..."
xcode-select --install
echo

echo "Checking that Python 3 has been installed"
if command -v python3 &>/dev/null; then
    echo "Python 3 is installed, proceeding..."
else
    echo "Python 3 is not installed. Go to python.org to download and re-run setup.sh"
fi
echo

echo "Checking that Heroku CLI has been installed"
if command -v heroku &>/dev/null; then
    echo "Heroku CLI is installed, proceeding..."
else
    echo "Heroku is not installed. Go to https://devcenter.heroku.com/articles/heroku-cli#macos to download and re-run setup.sh"
fi
echo

echo "Installing virtualenv..."
pip3 install virtualenv
echo

echo "Setting up virtualenv..."
virtualenv --python=python3 venv
source venv/bin/activate
echo

echo "Installing application requirements..."
pip3 install -r requirements.txt
echo

echo "To activate virtualenv, run the following command:"
echo "source venv/bin/activate"
echo

echo "Then, run the following to test the web server locally."
echo "heroku local"
echo
