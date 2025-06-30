coverage run --source tsingleap_backend,users,settings,competitions,forum,utils,tag -m pytest --junit-xml=xunit-reports/xunit-result.xml
ret=$?
coverage xml -o coverage-reports/coverage.xml
coverage report
exit $ret
