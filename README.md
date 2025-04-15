## Bucket Policy To Create S3 Bucket
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::vidizone-streamer1/media/*",
                "arn:aws:s3:::vidizone-streamer1/static/*"
            ]
        }
    ]
}
```

## CORS Policy
```
[
  {
    "AllowedHeaders": ["Authorization", "*"],
    "AllowedMethods": ["GET", "HEAD", "PUT", "POST"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]

```