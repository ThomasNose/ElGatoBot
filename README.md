# ElGatoBot

# Creates new docker image
sudo docker build -t {user}/{repo} .

# We then push this new image 
sudo docker push {user}/{repo}

# Finally we start the bot running with default region and in the background
sudo docker run -d -e AWS_DEFAULT_REGION={region e.g. eu-west-2} {user}/{repo}
