#!/bin/bash

#
# SCRIPT TO PUSH A DOCKER IMAGE TO DOCKER HUB
#



# Remote domain under Docker Hub of Network API
domain=globocom

# Network API image name
image_name=networkapi


echo "Let's push Network API image to Docker Hub"
echo "Enter your Docker Hub user:"
read user

echo "Trying to login.."
docker login --username ${user}

[ ! "$?" -eq "0" ] && {
    echo "Something went wrong during login"
    echo ":("
    exit 1
}

echo "What is the tag you are pushing now (example 0.1.0):"
read tag

docker tag ${image_name}:${tag} ${domain}/${image_name}:${tag}
docker push ${domain}/${image_name}:${tag}

[ ! "$?" -eq "0" ] && {
    echo "Something went wrong on pushing tag ${tag}"
    echo ":("
    exit 2
}

echo "Do you want to push latest tag too (y/N):"
read latest

if [ "${latest}" = "y" ]; then
    docker tag ${image_name}:latest ${domain}/${image_name}:latest
    docker push ${domain}/${image_name}:latest
fi;

echo "We are done!"
echo "Try to run the new image by:"
echo "docker run --name networkapi -it --rm -d ${domain}/${image_name}:${tag}"

exit 0;
