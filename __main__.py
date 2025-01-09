"""A Python Pulumi program"""

import pulumi
import pulumi_aws as aws
from pulumi_aws.ec2 import Instance

# Configurations
region = aws.config.region

# Creating a VPC
vpc = aws.ec2.Vpc("my-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags={
        "Name": "vidizone-vpc",
    }
)

# Create a public subnet for App server
public_subnet1 = aws.ec2.Subnet("vidizone-public-subnet-1",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=True,
    availability_zone="ap-southeast-1a",
    tags={
        "Name": "vidizone-public-subnet-1",
    }
)

# Create a private subnet 1
private_subnet1 = aws.ec2.Subnet("vidizone-private-subnet-1",
    vpc_id=vpc.id,
    cidr_block="10.0.2.0/24",
    map_public_ip_on_launch=False,
    availability_zone="ap-southeast-1b",
    tags={
        "Name": "vidizone-private-subnet-1",
    }
)

# Create a private subnet 2
private_subnet2 = aws.ec2.Subnet("vidizone-private-subnet-2",
    vpc_id=vpc.id,
    cidr_block="10.0.3.0/24",
    map_public_ip_on_launch=False,
    availability_zone="ap-southeast-1c",
    tags={
        "Name": "vidizone-private-subnet-2",
    }
)

# Create an Elastic IP for the NAT Gateway
eip = aws.ec2.Eip("vidizone-nat-eip",
    domain="vpc",
)

# Create the NAT Gateway
nat_gateway = aws.ec2.NatGateway("vidizone-nat-gateway",
    allocation_id=eip.id,
    subnet_id=public_subnet1.id,  # NAT Gateway goes in a public subnet
    tags={
        "Name": "vidizone-nat-gateway",
    }
)

# Create an Internet Gateway
internet_gateway = aws.ec2.InternetGateway("vidizone-app-igw",
    vpc_id=vpc.id,
    tags={
        "Name": "vidizone-app-igw",
    }
)

# Create a public route table for public subnets
public_route_table1 = aws.ec2.RouteTable("vidizone-public-route-table",
    vpc_id=vpc.id,
    routes=[
        {
            "cidr_block": "0.0.0.0/0", # Default route to the internet
            "gateway_id": internet_gateway.id,
        }
    ],
    tags={
        "Name": "vidizone-public-route-table",
    }
)

# Create a private route table for private subnets
private_route_table1 = aws.ec2.RouteTable("vidizone-private-route-table",
    vpc_id=vpc.id,
    routes=[
        {
            "cidr_block": "0.0.0.0/0",
            "nat_gateway_id": nat_gateway.id,
        }
    ],
    tags={
        "Name": "vidizone-private-route-table",
    }
)

# Associate route table with the public subnet
aws.ec2.RouteTableAssociation("vidizone-public-rt-association-1",
    subnet_id=public_subnet1.id,
    route_table_id=public_route_table1.id
)

# Associate route table with private subnet 1
aws.ec2.RouteTableAssociation("vidizone-private-rt-association-1",
    subnet_id=private_subnet1.id,
    route_table_id=private_route_table1.id
)

# Associate route table with private subnet 2
aws.ec2.RouteTableAssociation("vidizone-private-rt-association-1",
    subnet_id=private_subnet2.id,
    route_table_id=private_route_table1.id
)


# Security group for nginx load balancer
nginx_security_group = aws.ec2.SecurityGroup("vidizone-nginx-sg",
    vpc_id=vpc.id,
    description="Allow HTTP and SSH",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=80,
            to_port=80,
            cidr_blocks=["0.0.0.0/0"],  # Allow HTTP from anywhere
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=22,
            to_port=22,
            cidr_blocks=["0.0.0.0/0"],  # Allow SSH from anywhere
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],  # Allow all outbound traffic
        ),
    ],
    tags={
        "Name": "vidizone-nginx-sg",
    }
)

# Security group for the App server (Private subnet 1)
app_server_security_group = aws.ec2.SecurityGroup("vidizone-app-server-sg",
    vpc_id=vpc.id,
    description="Allow HTTP and SSH from public subnet",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=22,
            to_port=22,
            cidr_blocks=["10.0.1.0/24"],  # Allow SSH only from public subnet
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=80,
            to_port=80,
            cidr_blocks=["10.0.1.0/24"],  # Allow HTTP only from public subnet
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],  # Allow all outbound traffic
        ),
    ],
    tags={
        "Name": "vidizone-app-server-sg",
    }
)

# Security group for the redis server (Private subnet 2)
redis_server_security_group = aws.ec2.SecurityGroup("vidizone-redis-server-sg",
    vpc_id=vpc.id,
    description="Allow traffic to Redis server only from app servers, and SSH from Bastion server",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=22,
            to_port=22,
            cidr_blocks=["10.0.1.0/24"],  # Allow SSH only from public subnet
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=6379,
            to_port=6379,
            cidr_blocks=["10.0.2.0/24"],  # Allow only from private subnet 1
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],  # Allow all outbound traffic
        ),
    ],
    tags={
        "Name": "vidizone-redis-server-sg",
    }
)


# Security group for the worker(celery) server (Private subnet 2)
worker_server_security_group = aws.ec2.SecurityGroup("vidizone-worker-server-sg",
    vpc_id=vpc.id,
    description="Allow SSH from Bastion server",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=22,
            to_port=22,
            cidr_blocks=["10.0.1.0/24"],  # Allow SSH only from public subnet
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],  # Allow all outbound traffic
        ),
    ],
    tags={
        "Name": "vidizone-worker-server-sg",
    }
)

# Security group for the postgres db (Private subnet 2)
postgres_db_security_group = aws.ec2.SecurityGroup("vidizone-postgres-db-sg",
    vpc_id=vpc.id,
    description="Allow SSH from Bastion server",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=22,
            to_port=22,
            cidr_blocks=["10.0.1.0/24"],  # Allow SSH only from public subnet
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=5432,
            to_port=5432,
            cidr_blocks=["10.0.2.0/24"],  # Allow traffic from private subnet 1
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],  # Allow all outbound traffic
        ),
    ],
    tags={
        "Name": "vidizone-postgres-db-sg",
    }
)


# Creating the ec2 instances
ami_id = "ami-060e277c0d4cce553"

# Creating ec2 instance for nginx
nginx_instance = aws.ec2.Instance("vidizone-nginx-instance",
    instance_type="t2.micro",
    ami=ami_id,
    subnet_id=public_subnet1.id,
    vpc_security_group_ids=[nginx_security_group.id],
    key_name="MyKeyPair",
    associate_public_ip_address=True,
    tags={"Name": "vidizone-nginx-instance"},
)

# Creating ec2 instances for app servers
num_of_app_servers = 2

for i in range(num_of_app_servers):
    aws.ec2.Instance(f"vidizone-app-server-instance-{i+1}",
        instance_type="t2.micro",
        ami=ami_id,
        subnet_id=private_subnet1.id,
        vpc_security_group_ids=[app_server_security_group.id],
        key_name="MyKeyPair",
        associate_public_ip_address=False,
        tags={"Name": f"vidizone-app-server-instance-{i+1}"},
    )

# Creating ec2 instance for redis
aws.ec2.Instance(f"vidizone-redis-server-instance",
    instance_type="t2.micro",
    ami=ami_id,
    subnet_id=private_subnet2.id,
    vpc_security_group_ids=[redis_server_security_group.id],
    key_name="MyKeyPair",
    associate_public_ip_address=False,
    tags={"Name": f"vidizone-redis-server-instance"},
)

# Creating ec2 instances for worker servers
num_of_worker_servers = 2

for i in range(num_of_worker_servers):
    aws.ec2.Instance(f"vidizone-worker-server-instance-{i+1}",
        instance_type="t2.micro",
        ami=ami_id,
        subnet_id=private_subnet2.id,
        vpc_security_group_ids=[worker_server_security_group.id],
        key_name="MyKeyPair",
        associate_public_ip_address=False,
        tags={"Name": f"vidizone-worker-server-instance-{i+1}"},
    )

# Creating ec2 instance for postgres db
aws.ec2.Instance(f"vidizone-postgres-db-instance",
    instance_type="t2.micro",
    ami=ami_id,
    subnet_id=private_subnet2.id,
    vpc_security_group_ids=[postgres_db_security_group.id],
    key_name="MyKeyPair",
    associate_public_ip_address=False,
    tags={"Name": f"vidizone-postgres-db-instance"},
)