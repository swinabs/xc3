# Copyright (c) 2023, Xgrid Inc, https://xgrid.co

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

namespace      = "amirprojectxc3"
env            = "dev"
region         = "ap-southeast-2"
account_id     = "192248234478"
vpc_cidr_block = "10.0.0.0/16"
public_subnet_cidr_block = {
  "ap-southeast-2a" = "10.0.0.0/24"
  "ap-southeast-2b" = "10.0.1.0/24"
}
domain_name    = ""
hosted_zone_id = ""

private_subnet_cidr_block = {
  "ap-southeast-2a" = "10.0.100.0/24"
}
# private_subnet_cidr_block  = "10.0.100.0/24"
allow_traffic              = ["0.0.0.0/0"] // Use your own network CIDR
ses_email_address          = "104088013@student.swin.edu.au"
creator_email              = "104088013@student.swin.edu.au"
owner_email                = "104088013@student.swin.edu.au"
instance_type              = "t2.micro"
total_account_cost_lambda  = "total_account_cost"
total_account_cost_cronjob = "cron(0 0 1,15 * ? *)"     // flexible can be set according to need
prometheus_layer           = "lambda_layers/python.zip" // s3 key for lambda layer
memory_size                = 128
timeout                    = 300
project                    = "amirprojectxc3"
create_kms                 = false
maximum_budget = 5.0
threshold= 10
cloudwatch_namespace = "CustomCostMetric"
metric_name = "CostPercentageMetric"
sender_email = "104088013@student.swin.edu.au"
recipient_email = "maharjanamir.101@gmail.com"
security_group_ingress = {
  "pushgateway" = {
    description = "PushGateway"
    from_port   = 9091
    to_port     = 9091
    protocol    = "tcp"
    cidr_blocks = ["10.0.100.0/24"]
  },
  "prometheus" = {
    description = "Prometheus"
    from_port   = 9000
    to_port     = 9000
    protocol    = "tcp"
    cidr_blocks = ["10.0.100.0/24"]
  },
  "http" = {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["10.0.100.0/24"]
  },
  "https" = {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.100.0/24"]
  }
}
