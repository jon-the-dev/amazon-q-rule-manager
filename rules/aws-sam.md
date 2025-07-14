# AWS SAM

## Template Structure

- Always use SAM template version 2010-09-09 with Transform: AWS::Serverless-2016-10-31
- Use parameter files for environment-specific configurations (dev, staging, prod)
- Define global configurations in the Globals section to avoid repetition
- Use consistent naming conventions: {Environment}-{Application}-{Function/Resource}

## Lambda Functions

- Set explicit memory and timeout values based on function requirements
- Use environment variables for configuration, not hardcoded values
- Enable X-Ray tracing for all Lambda functions for observability
- Use layers for shared dependencies and common utilities
- Implement proper error handling and logging in all functions
- Use dead letter queues for failed function executions

## API Gateway

- Enable CloudWatch logs for API Gateway stages
- Use API Gateway request/response validation to reduce Lambda invocations
- Implement proper CORS configuration for browser-based applications
- Use API keys and usage plans for rate limiting when appropriate
- Enable AWS WAF for production APIs to protect against common attacks

## Monitoring and Observability

- Create CloudWatch alarms for Lambda errors, duration, and throttles
- Use CloudWatch Insights for log analysis and debugging
- Implement distributed tracing with X-Ray for complex applications
- Set up SNS topics for alarm notifications when provided
- Monitor cold start metrics and optimize accordingly

## Security Best Practices

- Use IAM roles with least privilege principle for all resources
- Enable encryption at rest and in transit for all data stores
- Use AWS Secrets Manager or Parameter Store for sensitive configuration
- Implement proper input validation and sanitization
- Use VPC endpoints for private communication when needed

## Performance Optimization

- Use provisioned concurrency for latency-sensitive functions
- Implement connection pooling for database connections
- Use AWS Lambda Powertools for consistent logging, metrics, and tracing
- Optimize package size and use layers for large dependencies
- Configure appropriate reserved concurrency limits

## Deployment and CI/CD

- Use SAM CLI for local development and testing
- Implement gradual deployments with CodeDeploy for production
- Use parameter overrides for environment-specific deployments
- Enable rollback triggers for failed deployments
- Use SAM Pipeline for automated CI/CD workflows

## Cost Optimization

- Monitor function duration and right-size memory allocation
- Use ARM-based Lambda functions (arm64) for cost savings when compatible
- Implement proper caching strategies (API Gateway, Lambda layers)
- Use scheduled scaling for predictable workloads
- Monitor and optimize DynamoDB read/write capacity

## Testing

- Use SAM local for local development and testing
- Implement unit tests for business logic
- Use integration tests for API endpoints
- Test error scenarios and edge cases
- Validate IAM policies and permissions

## Resource Management

- Use DynamoDB with on-demand billing for variable workloads
- Implement proper cleanup for temporary resources
- Use S3 lifecycle policies for data archival
- Set up proper backup strategies for stateful resources
- Use CloudFormation stack policies for production protection
