# Flashfood-python

- DevOps project for the course

- Python Bottle Server code for the Flashfood bot.

- This server is for making database transactions and storing the schema and information in the redis database.

- This is a platform where any verified restaurant can come to sell food items. We provide them with our customer base and push offers to customers present in that area that time. Also, a user can come and ask for currently live offers.

- Packages required to run the python server locally.
    - `bottle`
    - `pandas`
    - `redis`
    - `googlemaps`
    - `requests`
    - `geopy`
    - `pottery`

- To build a docker image, use the `dockerfile` present in the root directory.

- For running this server, ou can pull the docker image available to docker hub.
    - Pull : docker pull suryavampire/redpython
    - Run : docker run -p 4000:4000 suryavampire/redpython

- To just run the server locally clone this branch and run the following command : `python3 server.py`
    - The python server assumes that the redis server is running locally. Tries to connect to 0.0.0.0:6379. If their is a different address, it needs to changed appropriately.

- To test the server, as in to test the database transactions run the following command : `python3 test.py`. The test code assumes that the python server is running locally. If it not the case then pass the appropriate server address in the code.
