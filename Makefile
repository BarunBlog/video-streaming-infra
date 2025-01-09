aws-configure:
	aws configure

key-pair:
	@if [ -f "MyKeyPair.pem" ]; then \
		echo "MyKeyPair.pem exists. Deleting the old key pair..."; \
		rm MyKeyPair.pem; \
	fi
	aws ec2 create-key-pair --key-name MyKeyPair --query 'KeyMaterial' --output text > MyKeyPair.pem
	chmod 400 MyKeyPair.pem

up:
	pulumi up

refresh:
	pulumi refresh