TEST_FILE=test-results.xml

cd ~/build-agent/smartva
rm ../$TEST_FILE | true
PYTHONPATH=. env/Scripts/py.test --junitxml=../$TEST_FILE test

if [[ -f ../$TEST_FILE ]]; then
  exit 0
fi

exit 1
