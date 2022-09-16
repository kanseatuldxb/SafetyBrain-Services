sudo apt update
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
sudo apt-cache policy docker-ce
sudo apt install docker-ce
sudo systemctl status docker
//docker pull ubuntu
docker pull kanseatuldxb/ppe_application_image
docker images
sudo docker run -it ppe_application_image -d