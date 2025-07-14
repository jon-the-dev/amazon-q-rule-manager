# Runway Infrastructure as Code Rules

## Overview

Runway is a lightweight wrapper around infrastructure deployment tools (CloudFormation, Terraform, etc.) that makes it easier to manage complex deployments across multiple environments. This guide covers best practices for using Runway with CFNgin hooks for extended IaC deployments.

## Project Structure

### Standard Runway Layout

```bash
runway-project/
├── runway.yml                 # Main runway configuration
├── environments/
│   ├── dev/
│   │   ├── runway.yml        # Environment-specific config
│   │   └── tfvars/           # Terraform variables
│   ├── staging/
│   └── prod/
├── modules/
│   ├── cloudformation/
│   │   ├── stacks/
│   │   └── blueprints/
│   └── terraform/
│       ├── modules/
│       └── stacks/
├── hooks/
│   ├── pre_deploy/
│   ├── post_deploy/
│   ├── pre_destroy/
│   └── post_destroy/
├── tests/
├── docs/
└── .runway/                  # Runway cache directory
```

## Configuration Management

### Main runway.yml Structure

```yaml
# Global runway configuration
deployments:
  - modules:
      - path: modules/cloudformation/vpc
        name: vpc-stack
      - path: modules/terraform/eks
        name: eks-cluster
    environments:
      dev: true
      staging: true
      prod: true
    account_id: ${var account_id}
    assume_role:
      arn: arn:aws:iam::${var account_id}:role/RunwayDeploymentRole
    regions:
      - us-east-1
      - us-west-2
```

### Environment-Specific Configuration

- Use separate runway.yml files for each environment
- Override global settings with environment-specific values
- Use variable substitution for dynamic configuration
- Implement proper secret management for sensitive values

## CFNgin Integration

### CFNgin Configuration Best Practices

```yaml
# cfngin.yml
namespace: ${namespace}
cfngin_bucket: ${cfngin_bucket_name}

sys_path: ./

pre_build:
  - path: hooks.pre_deploy.validate_environment
  - path: hooks.pre_deploy.check_dependencies

post_build:
  - path: hooks.post_deploy.update_dns
  - path: hooks.post_deploy.notify_teams

pre_destroy:
  - path: hooks.pre_destroy.backup_data
  - path: hooks.pre_destroy.confirm_destruction

post_destroy:
  - path: hooks.post_destroy.cleanup_resources
  - path: hooks.post_destroy.update_inventory

stacks:
  - name: vpc
    class_path: blueprints.vpc.VPC
    variables:
      VpcCidr: ${vpc_cidr}
      Environment: ${environment}
    tags:
      customer: skynet
      application: sample-app
      environment: ${environment}
      regulated: no
      owner: jon@zer0day.net
```

## Hook Development

### Hook Structure and Organization

```python
# hooks/pre_deploy/validate_environment.py
from runway.cfngin.hooks.base import Hook
from runway.cfngin.context import Context
import logging

logger = logging.getLogger(__name__)

class ValidateEnvironment(Hook):
    """Validate environment configuration before deployment."""
    
    def pre_build(self, context: Context) -> bool:
        """Execute pre-build validation."""
        logger.info("Validating environment configuration...")
        
        # Validate required environment variables
        required_vars = ['AWS_REGION', 'ENVIRONMENT', 'ACCOUNT_ID']
        missing_vars = [var for var in required_vars if not context.environment.get(var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            return False
            
        # Validate AWS credentials and permissions
        if not self._validate_aws_access(context):
            return False
            
        logger.info("Environment validation completed successfully")
        return True
    
    def _validate_aws_access(self, context: Context) -> bool:
        """Validate AWS access and permissions."""
        try:
            # Implementation for AWS validation
            return True
        except Exception as e:
            logger.error(f"AWS validation failed: {e}")
            return False
```

### Hook Types and Usage

#### Pre-Deploy Hooks

- Environment validation
- Dependency checking
- Resource pre-provisioning
- Security scanning
- Configuration validation

#### Post-Deploy Hooks

- DNS updates
- Load balancer configuration
- Monitoring setup
- Notification sending
- Integration testing

#### Pre-Destroy Hooks

- Data backup
- Dependency checking
- Confirmation prompts
- Resource inventory
- Safety validations

#### Post-Destroy Hooks

- Cleanup operations
- DNS record removal
- Monitoring cleanup
- Notification sending
- Audit logging

## Security Best Practices

### IAM and Permissions

- Use least privilege principle for deployment roles
- Implement cross-account role assumption for multi-account deployments
- Use temporary credentials and avoid long-lived access keys
- Implement MFA requirements for production deployments
- Regular audit of deployment permissions

### Secrets Management

```python
# hooks/utils/secrets.py
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

def get_secret(secret_name: str, region: str = 'us-east-1') -> dict:
    """Retrieve secret from AWS Secrets Manager."""
    client = boto3.client('secretsmanager', region_name=region)
    
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except ClientError as e:
        logger.error(f"Failed to retrieve secret {secret_name}: {e}")
        raise
```

### Encryption and Data Protection

- Enable encryption at rest for all state files
- Use KMS for key management
- Implement secure parameter passing between modules
- Encrypt sensitive data in transit
- Use AWS Systems Manager Parameter Store for configuration

## Multi-Environment Management

### Environment Promotion Strategy

```yaml
# environments/dev/runway.yml
deployments:
  - modules:
      - path: modules/cloudformation/app
        parameters:
          InstanceType: t3.micro
          MinSize: 1
          MaxSize: 2
        tags:
          environment: dev
          cost-center: development

# environments/prod/runway.yml
deployments:
  - modules:
      - path: modules/cloudformation/app
        parameters:
          InstanceType: t3.large
          MinSize: 3
          MaxSize: 10
        tags:
          environment: prod
          cost-center: production
```

### Variable Management

- Use environment-specific variable files
- Implement variable validation in hooks
- Use AWS Systems Manager for environment-specific parameters
- Implement secure variable interpolation
- Document all required variables

## Terraform Integration

### Terraform Module Standards

```hcl
# modules/terraform/eks/main.tf
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Use remote state
terraform {
  backend "s3" {
    # Configuration provided by Runway
  }
}

# Standard tagging
locals {
  common_tags = {
    customer     = var.customer
    application  = var.application
    environment  = var.environment
    regulated    = var.regulated
    owner        = var.owner
    managed_by   = "runway"
  }
}
```

### State Management

- Use remote state backends (S3 + DynamoDB)
- Implement state locking
- Use separate state files per environment
- Regular state file backups
- State file encryption

## CloudFormation Integration

### Blueprint Development

```python
# blueprints/vpc.py
from troposphere import Template, Ref, Output, Parameter
from troposphere.ec2 import VPC, Subnet, InternetGateway
from runway.cfngin.blueprints.base import Blueprint

class VPC(Blueprint):
    """VPC Blueprint with standard configuration."""
    
    VARIABLES = {
        'VpcCidr': {'type': str, 'default': '10.0.0.0/16'},
        'Environment': {'type': str},
        'EnableDnsHostnames': {'type': bool, 'default': True},
        'EnableDnsSupport': {'type': bool, 'default': True},
    }
    
    def create_template(self):
        """Create CloudFormation template."""
        template = Template()
        template.set_description("VPC with public and private subnets")
        
        # Add parameters
        vpc_cidr = template.add_parameter(Parameter(
            'VpcCidr',
            Type='String',
            Default=self.variables['VpcCidr'],
            Description='CIDR block for VPC'
        ))
        
        # Create VPC
        vpc = template.add_resource(VPC(
            'VPC',
            CidrBlock=Ref(vpc_cidr),
            EnableDnsHostnames=self.variables['EnableDnsHostnames'],
            EnableDnsSupport=self.variables['EnableDnsSupport'],
            Tags=self.get_tags()
        ))
        
        # Add outputs
        template.add_output(Output(
            'VpcId',
            Description='VPC ID',
            Value=Ref(vpc),
            Export={'Name': f"{self.context.namespace}-vpc-id"}
        ))
        
        return template
    
    def get_tags(self):
        """Get standard tags for resources."""
        return [
            {'Key': 'Name', 'Value': f"{self.variables['Environment']}-vpc"},
            {'Key': 'Environment', 'Value': self.variables['Environment']},
            {'Key': 'customer', 'Value': 'skynet'},
            {'Key': 'application', 'Value': 'sample-app'},
            {'Key': 'regulated', 'Value': 'no'},
            {'Key': 'owner', 'Value': 'jon@zer0day.net'},
        ]
```

## Testing and Validation

### Infrastructure Testing

```python
# tests/test_vpc_blueprint.py
import unittest
from runway.cfngin.context import Context
from blueprints.vpc import VPC

class TestVPCBlueprint(unittest.TestCase):
    """Test VPC blueprint functionality."""
    
    def setUp(self):
        self.context = Context()
        self.blueprint = VPC('test-vpc', self.context)
    
    def test_template_creation(self):
        """Test template is created successfully."""
        self.blueprint.resolve_variables({
            'VpcCidr': '10.0.0.0/16',
            'Environment': 'test'
        })
        
        template = self.blueprint.create_template()
        self.assertIsNotNone(template)
        
        # Validate template structure
        resources = template.to_dict()['Resources']
        self.assertIn('VPC', resources)
        self.assertEqual(resources['VPC']['Type'], 'AWS::EC2::VPC')
```

### Hook Testing

```python
# tests/test_hooks.py
import unittest
from unittest.mock import Mock, patch
from hooks.pre_deploy.validate_environment import ValidateEnvironment

class TestValidateEnvironmentHook(unittest.TestCase):
    """Test environment validation hook."""
    
    def setUp(self):
        self.hook = ValidateEnvironment()
        self.context = Mock()
    
    @patch.dict('os.environ', {
        'AWS_REGION': 'us-east-1',
        'ENVIRONMENT': 'test',
        'ACCOUNT_ID': '123456789012'
    })
    def test_successful_validation(self):
        """Test successful environment validation."""
        result = self.hook.pre_build(self.context)
        self.assertTrue(result)
```

## Monitoring and Observability

### Deployment Monitoring

```python
# hooks/post_deploy/setup_monitoring.py
from runway.cfngin.hooks.base import Hook
import boto3
import logging

logger = logging.getLogger(__name__)

class SetupMonitoring(Hook):
    """Setup CloudWatch monitoring for deployed resources."""
    
    def post_build(self, context):
        """Setup monitoring after successful deployment."""
        logger.info("Setting up monitoring for deployed resources...")
        
        # Create CloudWatch alarms
        self._create_alarms(context)
        
        # Setup log groups
        self._setup_log_groups(context)
        
        # Configure SNS notifications
        self._setup_notifications(context)
        
        logger.info("Monitoring setup completed")
        return True
    
    def _create_alarms(self, context):
        """Create CloudWatch alarms for resources."""
        cloudwatch = boto3.client('cloudwatch')
        
        # Implementation for creating alarms
        pass
```

### Logging and Auditing

- Enable CloudTrail for all deployment activities
- Implement structured logging in hooks
- Use CloudWatch Logs for centralized log management
- Track deployment metrics and success rates
- Implement audit trails for compliance

## Performance Optimization

### Deployment Speed

- Use parallel deployments where possible
- Implement dependency management
- Cache frequently used resources
- Optimize hook execution order
- Use incremental deployments

### Resource Optimization

- Right-size resources based on environment
- Implement auto-scaling where appropriate
- Use spot instances for non-critical workloads
- Optimize storage classes and lifecycle policies
- Regular cost analysis and optimization

## Error Handling and Recovery

### Rollback Strategies

```python
# hooks/utils/rollback.py
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RollbackManager:
    """Manage deployment rollbacks."""
    
    def __init__(self, context):
        self.context = context
        self.rollback_stack = []
    
    def add_rollback_action(self, action: callable, *args, **kwargs):
        """Add action to rollback stack."""
        self.rollback_stack.append((action, args, kwargs))
    
    def execute_rollback(self):
        """Execute all rollback actions in reverse order."""
        logger.info("Executing rollback actions...")
        
        for action, args, kwargs in reversed(self.rollback_stack):
            try:
                action(*args, **kwargs)
                logger.info(f"Rollback action {action.__name__} completed")
            except Exception as e:
                logger.error(f"Rollback action {action.__name__} failed: {e}")
```

### Error Recovery

- Implement comprehensive error handling in hooks
- Use circuit breaker patterns for external dependencies
- Implement retry logic with exponential backoff
- Maintain deployment state for recovery
- Automated rollback triggers

## Documentation and Maintenance

### Documentation Requirements

- Document all custom hooks and their purposes
- Maintain environment-specific configuration guides
- Document deployment procedures and troubleshooting
- Keep architecture diagrams up to date
- Document disaster recovery procedures

### Maintenance Tasks

- Regular dependency updates
- Security vulnerability scanning
- Performance monitoring and optimization
- Backup and recovery testing
- Compliance auditing

## CI/CD Integration

### Pipeline Configuration

```yaml
# .github/workflows/runway-deploy.yml
name: Runway Deployment

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install Runway
        run: pip install runway
      - name: Validate Configuration
        run: runway test
  
  deploy-dev:
    needs: validate
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Dev
        run: runway deploy --environment dev
```

### Quality Gates

- Automated testing before deployment
- Security scanning integration
- Cost estimation and approval
- Manual approval for production deployments
- Automated rollback on failure

## Best Practices Summary

### Configuration Management

- Use version control for all configuration files
- Implement configuration validation
- Use environment-specific overrides
- Maintain configuration documentation
- Regular configuration audits

### Security

- Follow least privilege principles
- Use temporary credentials
- Implement secrets management
- Regular security assessments
- Compliance monitoring

### Operations

- Implement comprehensive monitoring
- Use infrastructure as code principles
- Maintain disaster recovery procedures
- Regular backup and recovery testing
- Performance optimization

### Development

- Use consistent coding standards
- Implement comprehensive testing
- Use version control best practices
- Code review processes
- Documentation maintenance
