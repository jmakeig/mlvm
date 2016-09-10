* `virtualenv env` to create a new virtualenv called “env”
* `source env/bin/activate` to set virtualenv
* `pip install -r requirements.txt` to install dependencies
* `python setup.py develop`


mlvm uses [tappy](http://tappy.readthedocs.io/) to run standard Python `unittest` tests. Run the tests and print the TAP results to stdout

* `python mlvm/test/runner.py`

For a better TAP experience you can also run some additional TAP consumers. These are Node.js tools, so you’ll need Node and npm

* `npm install` intalls the dependencies
* `npm test` runs the tests and reports results to stdout and system notifications

* `git clone git@github.com:google/macops.git`
* `~/Workspaces/mlvm/env/bin/python ~/Worksapces/macops/gmacpyutil/setup.py install`
