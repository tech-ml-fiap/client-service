#!/bin/bash
# Instala Docker
yum update -y -q
amazon-linux-extras install docker -y
service docker start
usermod -aG docker ec2-user

# Login no ECR
aws ecr get-login-password --region ${region} \
  | docker login --username AWS --password-stdin $(echo ${image_uri} | cut -d'/' -f1)

# Exporta variáveis de DB para dentro do container
export DB_HOST=${db_host}
export DB_PORT=${db_port}
export DB_USER=${db_user}
export DB_PASSWORD=${db_password}
export DB_NAME=${db_name}

# Executa migrations
docker run --rm \
  -e DB_HOST -e DB_PORT -e DB_USER -e DB_PASSWORD -e DB_NAME \
  ${image_uri} alembic upgrade head

# Sobe aplicação
docker run -d --name app \
  -p ${port}:${port} \
  -e DB_HOST -e DB_PORT -e DB_USER -e DB_PASSWORD -e DB_NAME \
  ${image_uri}
