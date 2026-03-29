import re


PROVIDER_LABELS = {
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
}

SERVICE_EQUIVALENTS = {
    "object_storage": {
        "aws": "S3",
        "azure": "Blob Storage",
        "gcp": "Cloud Storage",
        "display": "Object Storage",
    },
    "relational_db": {
        "aws": "RDS",
        "azure": "Azure Database for PostgreSQL",
        "gcp": "Cloud SQL",
        "display": "Relational Database",
    },
    "identity": {
        "aws": "IAM",
        "azure": "Azure Active Directory",
        "gcp": "Cloud IAM",
        "display": "Identity & Access Management",
    },
    "compute": {
        "aws": "EC2",
        "azure": "Virtual Machines",
        "gcp": "Compute Engine",
        "display": "Compute",
    },
    "serverless": {
        "aws": "Lambda",
        "azure": "Azure Functions",
        "gcp": "Cloud Functions",
        "display": "Serverless Functions",
    },
    "cdn": {
        "aws": "CloudFront",
        "azure": "Azure CDN",
        "gcp": "Cloud CDN",
        "display": "CDN",
    },
}

TERRAFORM_RESOURCE_TYPES = {
    "aws": {
        "S3": [
            "aws_s3_bucket",
            "aws_s3_bucket_public_access_block",
            "aws_s3_bucket_server_side_encryption_configuration",
        ],
        "RDS": ["aws_db_instance"],
        "IAM": ["aws_iam_user", "aws_iam_account_password_policy"],
        "EC2": ["aws_instance"],
        "Lambda": ["aws_lambda_function"],
        "CloudFront": ["aws_cloudfront_distribution"],
    },
    "azure": {
        "Blob Storage": ["azurerm_storage_account", "azurerm_storage_container"],
        "Azure Database for PostgreSQL": ["azurerm_postgresql_server"],
        "Azure Active Directory": ["azurerm_user_assigned_identity"],
        "Virtual Machines": ["azurerm_linux_virtual_machine"],
        "Azure Functions": ["azurerm_function_app"],
        "Azure CDN": ["azurerm_cdn_profile", "azurerm_cdn_endpoint"],
    },
    "gcp": {
        "Cloud Storage": ["google_storage_bucket"],
        "Cloud SQL": ["google_sql_database_instance"],
        "Cloud IAM": ["google_project_iam_audit_config", "google_project_iam_member"],
        "Compute Engine": ["google_compute_instance"],
        "Cloud Functions": ["google_cloudfunctions2_function"],
        "Cloud CDN": ["google_compute_backend_bucket"],
    },
}

SERVICE_DESCRIPTIONS = {
    "S3": "Object storage",
    "Blob Storage": "Object storage",
    "Cloud Storage": "Object storage",
    "RDS": "Relational database",
    "Azure Database for PostgreSQL": "Relational database",
    "Cloud SQL": "Relational database",
    "IAM": "Identity and access",
    "Azure Active Directory": "Identity and access",
    "Cloud IAM": "Identity and access",
    "EC2": "Virtual machines",
    "Virtual Machines": "Virtual machines",
    "Compute Engine": "Virtual machines",
    "Lambda": "Serverless",
    "Azure Functions": "Serverless",
    "Cloud Functions": "Serverless",
    "CloudFront": "Content delivery",
    "Azure CDN": "Content delivery",
    "Cloud CDN": "Content delivery",
}


def normalize_provider(provider: str) -> str:
    return (provider or "aws").strip().lower()


def get_provider_label(provider: str) -> str:
    return PROVIDER_LABELS.get(normalize_provider(provider), provider.upper())


def slugify_service_name(service: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", service.strip().lower()).strip("_")


def get_generic_concept(service: str) -> str | None:
    normalized = service.strip().lower()
    for concept, mapping in SERVICE_EQUIVALENTS.items():
        if normalized == concept:
            return concept
        for provider_name in ("aws", "azure", "gcp"):
            if mapping.get(provider_name, "").lower() == normalized:
                return concept
    return None


def get_provider_service_name(generic_service: str, provider: str) -> str:
    provider = normalize_provider(provider)
    concept = get_generic_concept(generic_service)
    if concept:
        return SERVICE_EQUIVALENTS[concept].get(provider, generic_service)
    return generic_service


def get_provider_services(provider: str) -> list[str]:
    provider = normalize_provider(provider)
    services = []
    for mapping in SERVICE_EQUIVALENTS.values():
        value = mapping.get(provider)
        if value:
            services.append(value)
    return services


def get_service_description(service: str) -> str:
    return SERVICE_DESCRIPTIONS.get(service, "Custom service")


def get_terraform_resources(service: str, provider: str) -> list[str]:
    provider_map = TERRAFORM_RESOURCE_TYPES.get(normalize_provider(provider), {})
    canonical = get_provider_service_name(service, provider)
    return provider_map.get(canonical, [slugify_service_name(canonical)])
