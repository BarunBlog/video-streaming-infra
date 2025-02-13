"""A Python Pulumi program"""

import pulumi
import pulumi_aws as aws
import json

# Configurations
config = pulumi.Config()
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
aws.ec2.RouteTableAssociation("vidizone-private-rt-association-2",
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
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=8000,
            to_port=8000,
            cidr_blocks=["10.0.1.0/24"],  # Allow Django app traffic from public subnet
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

# Security group for flower server
flower_server_security_group = aws.ec2.SecurityGroup("vidizone-flower-server-sg",
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
            from_port=5000,
            to_port=5000,
            cidr_blocks=["10.0.1.0/24", "10.0.2.0/24"],  # Allow Flower port traffic from public and private subnets
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=32,
            to_port=32,
            cidr_blocks=["10.0.1.0/24"],  # Allow User-data from public subnet
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
        "Name": "vidizone-flower-server-sg",
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
            cidr_blocks=["10.0.2.0/24", "10.0.3.0/24"],  # Allow from private subnet 1 and 2
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
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=32,
            to_port=32,
            cidr_blocks=["10.0.1.0/24"],  # Allow User-data from public subnet
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

# Creating Flower server in the private subnet 1
aws.ec2.Instance(f"vidizone-flower-server-instance",
    instance_type="t2.micro",
    ami=ami_id,
    subnet_id=private_subnet1.id,
    vpc_security_group_ids=[flower_server_security_group.id],
    key_name="MyKeyPair",
    associate_public_ip_address=False,
    tags={"Name": f"vidizone-flower-server-instance"},
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

# Create an S3 bucket
bucket = aws.s3.BucketV2("vidizone-s3-bucket",
    bucket="vidizone-streamer",
    tags={
        "Name": "vidizone-streamer",
    },
)

bucket_ownership_controls = aws.s3.BucketOwnershipControls("bucket_ownership_controls",
    bucket=bucket.id,
    rule={
        "object_ownership": "BucketOwnerPreferred",
    })

bucket_public_access_block = aws.s3.BucketPublicAccessBlock("bucket_public_access_block",
    bucket=bucket.id,
    block_public_acls=False,
    block_public_policy=False,
    ignore_public_acls=False,
    restrict_public_buckets=False
)

example_bucket_acl_v2 = aws.s3.BucketAclV2("example_bucket_acl",
    bucket=bucket.id,
    acl="public-read",
    opts = pulumi.ResourceOptions(depends_on=[
            bucket_ownership_controls,
            bucket_public_access_block,
    ]))

bucket_cors_configuration_v2 = aws.s3.BucketCorsConfigurationV2("vidizone-cors-config",
    bucket=bucket.id,
    cors_rules=[
        {
            "allowed_headers": ["Authorization", "*"],
            "allowed_methods": ["GET", "HEAD"],
            "allowed_origins": ["*"],
            "expose_headers": ["ETag"],
            "max_age_seconds": 3000,
        }
    ]
)

# Attach the bucket policy to the bucket
bucket_policy_resource = aws.s3.BucketPolicy("vidzone-streamer-policy",
    bucket=bucket.id,
    policy=bucket.id.apply(lambda bucket_id: json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": [
                    f"arn:aws:s3:::{bucket_id}/static/*",
                    f"arn:aws:s3:::{bucket_id}/media/*"
                ]
            }
        ]
    }))
)

