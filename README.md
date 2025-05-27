# amazonq-rules
AmazonQ for Developer Rules

## Overview
This repository contains rule files for Amazon Q that can be installed in your projects. The rules help ensure consistency in AWS, Python, and Terraform code.

## Usage

### Managing Rules
Use the `manage_rules.py` script to install, update, uninstall, and list rules:

```bash
# List available rules
python manage_rules.py list

# List rules installed in a project
python manage_rules.py list /path/to/project

# Show detailed information about available rules
python manage_rules.py show-installable

# Install a rule to a project
python manage_rules.py install aws /path/to/project

# Update a source rule with changes from a project
python manage_rules.py update python /path/to/project

# Uninstall a rule from a project
python manage_rules.py uninstall terraform /path/to/project
```

### Available Rules

- **AWS Rules**: Guidelines for AWS resources including alarms, tagging, and default values
- **Python Rules**: Standards for Python development including version requirements and coding practices
- **Terraform Rules**: Best practices for Terraform including version requirements and security principles

## Configuration
You can override the default source directory by setting the `AMAZONQ_RULES_SOURCE` environment variable.
