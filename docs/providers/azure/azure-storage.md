# Azure Storage

Source pages:
- Introduction to Azure Storage: https://learn.microsoft.com/en-us/azure/storage/common/storage-introduction
- Security recommendations for Blob storage: https://learn.microsoft.com/en-us/azure/storage/blobs/security-recommendations

## Introduction to Azure Storage

Source: https://learn.microsoft.com/en-us/azure/storage/common/storage-introduction

# Introduction to Azure Storage

The Azure Storage platform is Microsoft's cloud storage solution for modern data storage scenarios. Azure Storage offers highly available, massively scalable, durable, and secure storage for a variety of data objects in the cloud. Azure Storage data objects are accessible from anywhere in the world over HTTP or HTTPS via a REST API. Azure Storage also offers client libraries for developers building applications or services with .NET, Java, Python, JavaScript, C++, and Go. Developers and IT professionals can use Azure PowerShell and Azure CLI to write scripts for data management or configuration tasks. The Azure portal and Azure Storage Explorer provide user-interface tools for interacting with Azure Storage.

## Benefits of Azure Storage

Azure Storage services offer the following benefits for application developers and IT professionals:

- Durable and highly available. Redundancy ensures that your data is safe in the event of transient hardware failures. You can also opt to replicate data across data centers or geographical regions for additional protection from local catastrophe or natural disaster. Data replicated in this way remains highly available in the event of an unexpected outage.
- Secure. All data written to an Azure storage account is encrypted by the service. Azure Storage provides you with fine-grained control over who has access to your data.
- Scalable. Azure Storage is designed to be massively scalable to meet the data storage and performance needs of today's applications.
- Managed. Azure handles hardware maintenance, updates, and critical issues for you.
- Accessible. Data in Azure Storage is accessible from anywhere in the world over HTTP or HTTPS. Microsoft provides client libraries for Azure Storage in a variety of languages, including .NET, Java, Node.js, Python, Go, and others, as well as a mature REST API. Azure Storage supports scripting in Azure PowerShell or Azure CLI. And the Azure portal and Azure Storage Explorer offer easy visual solutions for working with your data.

## Azure Storage data services

The Azure Storage platform includes the following data services:

- Azure Blobs (../blobs/storage-blobs-introduction) : A massively scalable object store for text and binary data. Also includes support for big data analytics through Data Lake Storage.
- Azure Files (../files/storage-files-introduction) : Managed file shares for cloud or on-premises deployments.
- Azure Elastic SAN (../elastic-san/elastic-san-introduction) : A fully integrated solution that simplifies deploying, scaling, managing, and configuring a SAN in Azure.
- Azure Queues (../queues/storage-queues-introduction) : A messaging store for reliable messaging between application components.
- Azure Tables (../tables/table-storage-overview) : A NoSQL store for schemaless storage of structured data.
- Azure Managed Disks (/en-us/azure/virtual-machines/managed-disks-overview) : Block-level storage volumes for Azure VMs.
- Azure Container Storage (/en-us/azure/storage/container-storage/container-storage-introduction) : A volume management, deployment, and orchestration service built natively for containers.

Each service is accessed through a storage account with a unique address. To get started, see Create a storage account (storage-account-create) .

Additionally, Azure provides the following specialized storage:

- Azure NetApp Files (../../azure-netapp-files/azure-netapp-files-introduction) : Enterprise files storage, powered by NetApp: makes it easy for enterprise line-of-business (LOB) and storage professionals to migrate and run complex, file-based applications with no code change. Azure NetApp Files is managed via NetApp accounts and can be accessed via NFS, SMB and dual-protocol volumes. To get started, see Create a NetApp account (../../azure-netapp-files/azure-netapp-files-create-netapp-account) .
- Azure Managed Lustre (/en-us/azure/azure-managed-lustre/amlfs-overview) : A high-performance distributed parallel file system solution, ideal for HPC workloads that require high throughput and low latency.

For help in deciding which data services to use for your scenario, see Review your storage options (/en-us/azure/cloud-adoption-framework/ready/considerations/storage-options) in the Microsoft Cloud Adoption Framework.

## Review options for storing data in Azure

Azure provides a variety of storage tools and services. To determine which Azure technology is best suited for your scenario, see Review your storage options (/en-us/azure/cloud-adoption-framework/ready/considerations/storage-options) in the Azure Cloud Adoption Framework.

## Sample scenarios for Azure Storage services

The following table compares Azure Storage services and shows example scenarios for each.

Feature Description When to use

Azure Files Offers fully managed cloud file shares that you can access from anywhere via the industry standard Server Message Block (SMB) protocol (/en-us/windows/win32/fileio/microsoft-smb-protocol-and-cifs-protocol-overview) , Network File System (NFS) protocol (https://en.wikipedia.org/wiki/Network_File_System) , and Azure Files REST API (/en-us/rest/api/storageservices/file-service-rest-api) .

You can mount Azure file shares from cloud or on-premises deployments of Windows, Linux, and macOS. You want to "lift and shift" an application to the cloud that already uses the native file system APIs to share data between it and other applications running in Azure.

You want to replace or supplement on-premises file servers or NAS devices.

You want to store development and debugging tools that need to be accessed from many virtual machines.

Azure NetApp Files Offers a fully managed, highly available, enterprise-grade NAS service that can handle the most demanding, high-performance, low-latency workloads requiring advanced data management capabilities. You have a difficult-to-migrate workload such as POSIX-compliant Linux and Windows applications, SAP HANA, databases, high-performance compute (HPC) infrastructure and apps, and enterprise web applications.

You require support for multiple file-storage protocols in a single service, including NFSv3, NFSv4.1, and SMB3.1.x, enables a wide range of application lift-and-shift scenarios, with no need for code changes.

Azure Blobs Allows unstructured data to be stored and accessed at a massive scale in block blobs.

Also supports Azure Data Lake Storage (../blobs/data-lake-storage-introduction) for enterprise big data analytics solutions. You want your application to support streaming and random access scenarios.

You want to be able to access application data from anywhere.

You want to build an enterprise data lake on Azure and perform big data analytics.

Azure Elastic SAN Azure Elastic SAN is a fully integrated solution that simplifies deploying, scaling, managing, and configuring a SAN, while also offering built-in cloud capabilities like high availability. You want large scale storage that is interoperable with multiple types of compute resources (such as SQL, MariaDB, Azure virtual machines, and Azure Kubernetes Services) accessed via the internet Small Computer Systems Interface (https://en.wikipedia.org/wiki/ISCSI) (iSCSI) protocol.

Azure Disks Allows data to be persistently stored and accessed from an attached virtual hard disk. You want to "lift and shift" applications that use native file system APIs to read and write data to persistent disks.

You want to store data that isn't required to be accessed from outside the virtual machine to which the disk is attached.

Azure Container Storage Azure Container Storage is a volume management, deployment, and orchestration service that integrates with Kubernetes and is built natively for containers. You want to dynamically and automatically provision persistent volumes to store data for stateful applications running on Kubernetes clusters.

Azure Queues Allows for asynchronous message queueing between application components. You want to decouple application components and use asynchronous messaging to communicate between them.

For guidance around when to use Queue Storage versus Service Bus queues, see Storage queues and Service Bus queues - compared and contrasted (../../service-bus-messaging/service-bus-azure-and-service-bus-queues-compared-contrasted) .

Azure Tables Allows you to store structured NoSQL data in the cloud, providing a key/attribute store with a schemaless design. You want to store flexible datasets like user data for web applications, address books, device information, or other types of metadata your service requires.

For guidance around when to use Table Storage versus Azure Cosmos DB for Table, see Developing with Azure Cosmos DB for Table and Azure Table Storage (/en-us/azure/cosmos-db/table-support) .

Azure Managed Lustre Offers a fully managed, pay-as-you-go file system for high-performance computing (HPC) and AI workloads. Designed to simplify operations, reduce setup costs, and eliminate complex maintenance. You want to run HPC workloads that require high throughput and low latency.

You want to run Lustre workloads in the cloud without the need to manage the underlying infrastructure.

## Blob Storage

Azure Blob Storage is Microsoft's object storage solution for the cloud. Blob Storage is optimized for storing massive amounts of unstructured data, such as text or binary data.

Blob Storage is ideal for:

- Serving images or documents directly to a browser.
- Storing files for distributed access.
- Streaming video and audio.
- Storing data for backup and restore, disaster recovery, and archiving.
- Storing data for analysis by an on-premises or Azure-hosted service.

Objects in Blob Storage can be accessed from anywhere in the world via HTTP or HTTPS. Users or client applications can access blobs via URLs, the Azure Storage REST API (/en-us/rest/api/storageservices/blob-service-rest-api) , Azure PowerShell (/en-us/powershell/module/az.storage) , Azure CLI (/en-us/cli/azure/storage) , or an Azure Storage client library. The storage client libraries are available for multiple languages, including .NET (/en-us/dotnet/api/overview/azure/storage) , Java (/en-us/java/api/overview/azure/storage) , Node.js (https://azure.github.io/azure-storage-node) , and Python (/en-us/python/api/overview/azure/storage) .

Clients can also securely connect to Blob Storage by using SSH File Transfer Protocol (SFTP) and mount Blob Storage containers by using the Network File System (NFS) 3.0 protocol.

For more information about Blob Storage, see Introduction to Blob Storage (../blobs/storage-blobs-introduction) .

## Azure Files

Azure Files (../files/storage-files-introduction) enables you to set up highly available network file shares that can be accessed by using the industry standard Server Message Block (SMB) protocol (/en-us/windows/win32/fileio/microsoft-smb-protocol-and-cifs-protocol-overview) , Network File System (NFS) protocol (https://en.wikipedia.org/wiki/Network_File_System) , and Azure Files REST API (/en-us/rest/api/storageservices/file-service-rest-api) . That means that multiple VMs can share the same files with both read and write access. You can also read the files using the REST interface or the storage client libraries.

One thing that distinguishes Azure Files from files on a corporate file share is that you can access the files from anywhere in the world using a URL that points to the file and includes a shared access signature (SAS) token. You can generate SAS tokens; they allow specific access to a private asset for a specific amount of time.

File shares can be used for many common scenarios:

Many on-premises applications use file shares. This feature makes it easier to migrate those applications that share data to Azure. If you mount the file share to the same drive letter that the on-premises application uses, the part of your application that accesses the file share should work with minimal, if any, changes.

Configuration files can be stored on a file share and accessed from multiple VMs. Tools and utilities used by multiple developers in a group can be stored on a file share, ensuring that everybody can find them, and that they use the same version.

Resource logs, metrics, and crash dumps are just three examples of data that can be written to a file share and processed or analyzed later.

For more information about Azure Files, see Introduction to Azure Files (../files/storage-files-introduction) .

Some SMB features aren't applicable to the cloud. For more information, see Features not supported by the Azure File service (/en-us/rest/api/storageservices/features-not-supported-by-the-azure-file-service) .

## Azure Elastic SAN

Azure Elastic storage area network (SAN) is Microsoft's answer to the problem of workload optimization and integration between your large scale databases and performance-intensive mission-critical applications. Elastic SAN is a fully integrated solution that simplifies deploying, scaling, managing, and configuring a SAN, while also offering built-in cloud capabilities like high availability.

Elastic SAN is designed for large scale IO-intensive workloads and top tier databases such as SQL, MariaDB, and support hosting the workloads on virtual machines, or containers such as Azure Kubernetes Service. Elastic SAN volumes are compatible with a wide variety of compute resources through the iSCSI (https://en.wikipedia.org/wiki/ISCSI) protocol. Some other benefits of Elastic SAN include a simplified deployment and management interface. Since you can manage storage for multiple compute resources from a single interface, and cost optimization.

For more information about Azure Elastic SAN, see What is Azure Elastic SAN? (../elastic-san/elastic-san-introduction)

## Azure Container Storage

Azure Container Storage integrates with Kubernetes and utilizes existing Azure Storage offerings for actual data storage, offering a volume orchestration and management solution purposely built for containers. You can choose any of the supported backing storage options to create a storage pool for your persistent volumes.

Azure Container Storage offers substantial benefits:

- Rapid scale out of stateful pods
- Improved performance for stateful workloads
- Kubernetes-native volume orchestration

For more information about Azure Container Storage, see What is Azure Container Storage? (../container-storage/container-storage-introduction)

## Queue Storage

The Azure Queue service is used to store and retrieve messages. Queue messages can be up to 64 KB in size, and a queue can contain millions of messages. Queues are generally used to store lists of messages to be processed asynchronously.

For example, say you want your customers to be able to upload pictures, and you want to create thumbnails for each picture. You could have your customer wait for you to create the thumbnails while uploading the pictures. An alternative would be to use a queue. When the customer finishes their upload, write a message to the queue. Then have an Azure Function retrieve the message from the queue and create the thumbnails. Each of the parts of this processing can be scaled separately, giving you more control when tuning it for your usage.

For more information about Azure Queues, see Introduction to Queues (../queues/storage-queues-introduction) .

## Table Storage

Azure Table Storage is now part of Azure Cosmos DB. To see Azure Table Storage documentation, see the Azure Table Storage overview (../tables/table-storage-overview) . In addition to the existing Azure Table Storage service, there's a new Azure Cosmos DB for Table offering that provides throughput-optimized tables, global distribution, and automatic secondary indexes. To learn more and try out the new premium experience, see Azure Cosmos DB for Table (/en-us/azure/cosmos-db/table-introduction) .

For more information about Table Storage, see Overview of Azure Table Storage (../tables/table-storage-overview) .

## Disk Storage

An Azure Managed Disk is a virtual hard disk (VHD). You can think of it like a physical disk in an on-premises server but, virtualized. Azure Managed Disks are stored as page blobs, which are a random IO storage object in Azure. We call a managed disk 'managed' because it's an abstraction over page blobs, blob containers, and Azure storage accounts. With managed disks, all you have to do is provision the disk, and Azure takes care of the rest.

For more information about managed disks, see Introduction to Azure Managed Disks (/en-us/azure/virtual-machines/managed-disks-overview) .

## Azure NetApp Files

Azure NetApp Files (../../azure-netapp-files/azure-netapp-files-introduction) is an enterprise-class, high-performance, metered file storage service. Azure NetApp Files supports any workload type and is highly available by default. You can select service and performance levels, create NetApp accounts, capacity pools, volumes, and manage data protection.

For more information about Azure NetApp Files, see Introduction to Azure NetApp Files (../../azure-netapp-files/azure-netapp-files-introduction) .

For a comparison of Azure Files and Azure NetApp Files, refer to Azure Files and Azure NetApp Files comparison (../files/storage-files-netapp-comparison) .

## Azure Managed Lustre

Azure Managed Lustre (/en-us/azure/azure-managed-lustre/amlfs-overview) is a managed file system that offers scalable, powerful, cost-effective storage for HPC workloads.

Key features and benefits of Azure Managed Lustre include:

- Accelerate HPC workloads : Offers a high-performance distributed parallel file system solution, ideal for HPC workloads that require high throughput and low latency.
- Purpose-built managed service : Provides the benefits of a Lustre parallel file system without the complexity of managing the underlying infrastructure. Azure Managed Lustre is a fully managed service that simplifies operations, reduces setup costs, and eliminates complex maintenance.
- Azure Blob Storage integration : Allows you to connect Azure Managed Lustre file systems with Azure Blob Storage containers for optimal data placement and cost management. For more information, see Azure Blob Storage integration (/en-us/azure/azure-managed-lustre/blob-integration) .
- Azure Kubernetes Service (AKS) integration : Allows you to containerize workloads using the available AKS-compatible CSI driver. For more information, see Use Azure Managed Lustre with Kubernetes (/en-us/azure/azure-managed-lustre/use-csi-driver-kubernetes) .

## Types of storage accounts

Azure Storage offers several types of storage accounts. Each type supports different features and has its own pricing model. For more information about storage account types, see Azure storage account overview (storage-account-overview) .

## Secure access to storage accounts

Every request to Azure Storage must be authorized. Azure Storage supports the following authorization methods:

- Microsoft Entra integration for blob, file, queue, and table data. Azure Storage supports authentication and authorization with Microsoft Entra ID for the Blob, File, Table, and Queue services via Azure role-based access control (Azure RBAC). Authorizing requests with Microsoft Entra ID is recommended for superior security and ease of use. For more information, see Authorize access to data in Azure Storage (authorize-data-access) . See Authorize access to file data in the Azure portal (../files/authorize-data-operations-portal) to authorize access to file data using your Microsoft Entra account.
- Identity-based authentication over SMB for Azure Files. Azure Files supports identity-based authorization over SMB (Server Message Block) through either on-premises Active Directory Domain Services (AD DS), Microsoft Entra Domain Services, or Microsoft Entra Kerberos (hybrid user accounts only). For more information, see Overview of Azure Files identity-based authentication support for SMB access (../files/storage-files-active-directory-overview) and Planning for an Azure Files deployment (../files/storage-files-planning#identity) .
- Authorization with Shared Key. The Azure Storage Blob, Files, Queue, and Table services support authorization with Shared Key. A client using Shared Key authorization passes a header with every request that is signed using the storage account access key. For more information, see Authorize with Shared Key (/en-us/rest/api/storageservices/authorize-with-shared-key) .
- Authorization using shared access signatures (SAS). A shared access signature (SAS) is a string containing a security token that can be appended to the URI for a storage resource. The security token encapsulates constraints such as permissions and the interval of access. For more information, see Using Shared Access Signatures (SAS) (storage-sas-overview) .
- Active Directory Domain Services with Azure NetApp Files. Azure NetApp Files features such as SMB volumes, dual-protocol volumes, and NFSv4.1 Kerberos volumes are designed to be used with AD DS. For more information, see Understand guidelines for Active Directory Domain Services site design and planning for Azure NetApp Files (../../azure-netapp-files/understand-guidelines-active-directory-domain-service-site) or learn how to Configure ADDS LDAP over TLS for Azure NetApp Files (../../azure-netapp-files/configure-ldap-over-tls) .

## Encryption

There are two basic kinds of encryption available for Azure Storage. For more information about security and encryption, see the Azure Storage security guide (../blobs/security-recommendations) .

### Encryption at rest

Azure Storage encryption protects and safeguards your data to meet your organizational security and compliance commitments. Azure Storage automatically encrypts all data prior to persisting to the storage account and decrypts it prior to retrieval. The encryption, decryption, and key management processes are transparent to users. Customers can also choose to manage their own keys using Azure Key Vault. For more information, see Azure Storage encryption for data at rest (storage-service-encryption) .

All Azure NetApp Files volumes are encrypted using the FIPS 140-2 standard. See Security FAQs for Azure NetApp Files (../../azure-netapp-files/faq-security#can-the-storage-be-encrypted-at-rest) .

### Client-side encryption

The Azure Storage client libraries provide methods for encrypting data from the client library before sending it across the wire and decrypting the response. Data encrypted via client-side encryption is also encrypted at rest by Azure Storage. For more information about client-side encryption, see Client-side encryption with .NET for Azure Storage (storage-client-side-encryption) .

Azure NetApp Files data traffic is inherently secure by design, as it doesn't provide a public endpoint and data traffic stays within customer-owned VNet. Data-in-flight isn't encrypted by default. However, data traffic from an Azure VM (running an NFS or SMB client) to Azure NetApp Files is as secure as any other Azure-VM-to-VM traffic. NFSv4.1 and SMB3 data-in-flight encryption can optionally be enabled. See Security FAQs for Azure NetApp Files (../../azure-netapp-files/faq-security#can-the-network-traffic-between-the-azure-virtual-machine-vm-and-the-storage-be-encrypted) .

## Redundancy

To ensure that your data is durable, Azure Storage stores multiple copies of your data. When you set up your storage account, you select a redundancy option. For more information, see Azure Storage redundancy (storage-redundancy?toc=/azure/storage/blobs/toc.json) and Azure Files data redundancy (../files/files-redundancy) .

Azure NetApp Files provides locally redundant storage with 99.99% availability (https://azure.microsoft.com/support/legal/sla/netapp/v1_1/) .

## Transfer data to and from Azure Storage

You have several options for moving data into or out of Azure Storage. Which option you choose depends on the size of your dataset and your network bandwidth. For more information, see Choose an Azure solution for data transfer (storage-choose-data-transfer-solution) .

Azure NetApp Files provides NFS and SMB volumes. You can use any file-based copy tool to migrate data to the service. For more information, see Data migration and protection FAQs for Azure NetApp Files (../../azure-netapp-files/faq-data-migration-protection) .

## Pricing

When making decisions about how your data is stored and accessed, you should also consider the costs involved. For more information, see Azure Storage pricing (https://azure.microsoft.com/pricing/details/storage/) .

Azure NetApp Files cloud file storage service is charged per hour based on the provisioned capacity pool (../../azure-netapp-files/azure-netapp-files-understand-storage-hierarchy#capacity_pools) capacity. For more information, see Azure NetApp Files storage pricing (https://azure.microsoft.com/pricing/details/netapp/) .

## Storage APIs, libraries, and tools

You can access resources in a storage account by any language that can make HTTP/HTTPS requests. Additionally, Azure Storage offer programming libraries for several popular languages. These libraries simplify many aspects of working with Azure Storage by handling details such as synchronous and asynchronous invocation, batching of operations, exception management, automatic retries, operational behavior, and so forth. Libraries are currently available for the following languages and platforms, with others in the pipeline:

### Azure Storage data API and library references

- Azure Storage REST API (/en-us/rest/api/storageservices/)
- Azure Storage client libraries for .NET (/en-us/dotnet/api/overview/azure/storage)
- Azure Storage client libraries for Java (/en-us/java/api/overview/azure/storage)
- Azure Storage client libraries for JavaScript (/en-us/javascript/api/overview/azure/storage)
- Azure Storage client libraries for Python (/en-us/python/api/overview/azure/storage)
- Azure Storage client libraries for Go (https://github.com/Azure/azure-sdk-for-go/tree/main/sdk/storage/)
- Azure Storage client libraries for C++ (https://github.com/Azure/azure-sdk-for-cpp/tree/main/sdk/storage)

### Azure Storage management API and library references

- Storage Resource Provider REST API (/en-us/rest/api/storagerp/)
- Storage Resource Provider Client Library for .NET (/en-us/dotnet/api/overview/azure/resourcemanager.storage-readme)
- Storage Service Management REST API (Classic) (/en-us/previous-versions/azure/reference/ee460790(v=azure.100))
- Azure Files REST API (/en-us/rest/api/storageservices/file-service-rest-api)
- Azure NetApp Files REST API (../../azure-netapp-files/azure-netapp-files-develop-with-rest-api)

### Azure Storage data movement API

- Storage Data Movement Client Library for .NET (storage-use-data-movement-library)

### Tools and utilities

- Azure PowerShell Cmdlets for Storage (/en-us/powershell/module/az.storage)
- Azure CLI Cmdlets for Storage (/en-us/cli/azure/storage)
- AzCopy Command-Line Utility (storage-use-azcopy-v10)
- Azure Storage Explorer (https://azure.microsoft.com/features/storage-explorer/) is a free, standalone app from Microsoft that enables you to work visually with Azure Storage data on Windows, macOS, and Linux.
- Azure Resource Manager templates for Azure Storage (https://azure.microsoft.com/resources/templates/?resourceType=Microsoft.Storage)

## Next steps

To get up and running with Azure Storage, see Create a storage account (storage-account-create) .

## Feedback

Was this page helpful?

No

Need help with this topic?

Want to try using Ask Learn to clarify or guide you through this topic?

## Additional resources

- Last updated on 2025-03-27


## Security recommendations for Blob storage

Source: https://learn.microsoft.com/en-us/azure/storage/blobs/security-recommendations

# Security recommendations for Blob storage

This article contains security recommendations for Blob storage. Implementing these recommendations will help you fulfill your security obligations as described in our shared responsibility model. For more information on how Microsoft fulfills service provider responsibilities, see Shared responsibility in the cloud (../../security/fundamentals/shared-responsibility) .

Some of the recommendations included in this article can be automatically monitored by Microsoft Defender for Cloud, which is the first line of defense in protecting your resources in Azure. For information on Microsoft Defender for Cloud, see What is Microsoft Defender for Cloud? (/en-us/azure/defender-for-cloud/defender-for-cloud-introduction)

Microsoft Defender for Cloud periodically analyzes the security state of your Azure resources to identify potential security vulnerabilities. It then provides you with recommendations on how to address them. For more information on Microsoft Defender for Cloud recommendations, see Review your security recommendations (/en-us/azure/defender-for-cloud/review-security-recommendations) .

## Data protection

Recommendation Comments Defender for Cloud

Use the Azure Resource Manager deployment model Create new storage accounts using the Azure Resource Manager deployment model for important security enhancements, including superior Azure role-based access control (Azure RBAC) and auditing, Resource Manager-based deployment and governance, access to managed identities, access to Azure Key Vault for secrets, and Microsoft Entra authentication and authorization for access to Azure Storage data and resources. Migrate (../common/classic-account-migration-process) all existing storage accounts that use the classic deployment model to use Azure Resource Manager. For more information about Azure Resource Manager, see Azure Resource Manager overview (../../azure-resource-manager/management/overview) . -

Enable Microsoft Defender for all of your storage accounts Microsoft Defender for Storage provides an additional layer of security intelligence that detects unusual and potentially harmful attempts to access or exploit storage accounts. Security alerts are triggered in Microsoft Defender for Cloud when anomalies in activity occur and are also sent via email to subscription administrators, with details of suspicious activity and recommendations on how to investigate and remediate threats. For more information, see Configure Microsoft Defender for Storage (../common/azure-defender-storage-configure) . Yes (/en-us/azure/defender-for-cloud/implement-security-recommendations)

Turn on soft delete for blobs Soft delete for blobs enables you to recover blob data after it has been deleted. For more information on soft delete for blobs, see Soft delete for Azure Storage blobs (soft-delete-blob-overview) . -

Turn on soft delete for containers Soft delete for containers enables you to recover a container after it has been deleted. For more information on soft delete for containers, see Soft delete for containers (soft-delete-container-overview) . -

Lock storage account to prevent accidental or malicious deletion or configuration changes Apply an Azure Resource Manager lock to your storage account to protect the account from accidental or malicious deletion or configuration change. Locking a storage account does not prevent data within that account from being deleted. It only prevents the account itself from being deleted. For more information, see Apply an Azure Resource Manager lock to a storage account (../common/lock-account-resource) .

Store business-critical data in immutable blobs Configure legal holds and time-based retention policies to store blob data in a WORM (Write Once, Read Many) state. Blobs stored immutably can be read, but cannot be modified or deleted for the duration of the retention interval. For more information, see Store business-critical blob data with immutable storage (immutable-storage-overview) . -

Use Encryption to Protect Data Azure Storage encrypts all data at rest by default using Microsoft-managed keys. For enhanced control, configure customer-managed keys (../common/customer-managed-keys-overview) with Azure Key Vault to manage encryption keys directly. To further strengthen security, implement client-side encryption (client-side-encryption) before uploading data. -

Require secure transfer (HTTPS) to the storage account When you require secure transfer for a storage account, all requests to the storage account must be made over HTTPS. Any requests made over HTTP are rejected. Microsoft recommends that you always require secure transfer for all of your storage accounts. For more information, see Require secure transfer to ensure secure connections (../common/storage-require-secure-transfer) . -

Limit shared access signature (SAS) tokens to HTTPS connections only Requiring HTTPS when a client uses a SAS token to access blob data helps to minimize the risk of eavesdropping. For more information, see Grant limited access to Azure Storage resources using shared access signatures (SAS) (../common/storage-sas-overview) . -

Disallow cross-tenant object replication By default, an authorized user is permitted to configure an object replication policy where the source account is in one Microsoft Entra tenant and the destination account is in a different tenant. Disallow cross-tenant object replication to require that the source and destination accounts participating in an object replication policy are in the same tenant. For more information, see Prevent object replication across Microsoft Entra tenants (object-replication-prevent-cross-tenant-policies) . -

## Identity and access management

Recommendation Comments Defender for Cloud

Use Microsoft Entra ID to authorize access to blob data Microsoft Entra ID provides superior security and ease of use over Shared Key for authorizing requests to Blob storage. For more information, see Authorize access to data in Azure Storage (../common/authorize-data-access) . -

Keep in mind the principle of least privilege when assigning permissions to a Microsoft Entra security principal via Azure RBAC When assigning a role to a user, group, or application, grant that security principal only those permissions that are necessary for them to perform their tasks. Limiting access to resources helps prevent both unintentional and malicious misuse of your data. -

Use a user delegation SAS to grant limited access to blob data to clients A user delegation SAS is secured with Microsoft Entra credentials and also by the permissions specified for the SAS. A user delegation SAS is analogous to a service SAS in terms of its scope and function, but offers security benefits over the service SAS. For more information, see Grant limited access to Azure Storage resources using shared access signatures (SAS) (../common/storage-sas-overview?toc=/azure/storage/blobs/toc.json) . -

Secure your account access keys with Azure Key Vault Microsoft recommends using Microsoft Entra ID to authorize requests to Azure Storage. However, if you must use Shared Key authorization, then secure your account keys with Azure Key Vault. You can retrieve the keys from the key vault at runtime, instead of saving them with your application. For more information about Azure Key Vault, see Azure Key Vault overview (/en-us/azure/key-vault/general/overview) . -

Regenerate your account keys periodically Rotating the account keys periodically reduces the risk of exposing your data to malicious actors. -

Disallow Shared Key authorization When you disallow Shared Key authorization for a storage account, Azure Storage rejects all subsequent requests to that account that are authorized with the account access keys. Only secured requests that are authorized with Microsoft Entra ID will succeed. For more information, see Prevent Shared Key authorization for an Azure Storage account (../common/shared-key-authorization-prevent) . -

Keep in mind the principle of least privilege when assigning permissions to a SAS When creating a SAS, specify only those permissions that are required by the client to perform its function. Limiting access to resources helps prevent both unintentional and malicious misuse of your data. -

Have a revocation plan in place for any SAS that you issue to clients If a SAS is compromised, you will want to revoke that SAS as soon as possible. To revoke a user delegation SAS, revoke the user delegation key to quickly invalidate all signatures associated with that key. To revoke a service SAS that is associated with a stored access policy, you can delete the stored access policy, rename the policy, or change its expiry time to a time that is in the past. For more information, see Grant limited access to Azure Storage resources using shared access signatures (SAS) (../common/storage-sas-overview) . -

If a service SAS is not associated with a stored access policy, then set the expiry time to one hour or less A service SAS that is not associated with a stored access policy cannot be revoked. For this reason, limiting the expiry time so that the SAS is valid for one hour or less is recommended. -

Disable anonymous read access to containers and blobs anonymous read access to a container and its blobs grants read-only access to those resources to any client. Avoid enabling anonymous read access unless your scenario requires it. To learn how to disable anonymous access for a storage account, see Overview: Remediating anonymous read access for blob data (anonymous-read-access-overview) . -

## Networking

Recommendation Comments Defender for Cloud

Configure the minimum required version of Transport Layer Security (TLS) for a storage account. Require that clients use a more secure version of TLS to make requests against an Azure Storage account by configuring the minimum version of TLS for that account. For more information, see Configure minimum required version of Transport Layer Security (TLS) for a storage account (../common/transport-layer-security-configure-minimum-version?toc=/azure/storage/blobs/toc.json) -

Enable the Secure transfer required option on all of your storage accounts When you enable the Secure transfer required option, all requests made against the storage account must take place over secure connections. Any requests made over HTTP will fail. For more information, see Require secure transfer in Azure Storage (../common/storage-require-secure-transfer?toc=/azure/storage/blobs/toc.json) . Yes (/en-us/azure/defender-for-cloud/implement-security-recommendations)

Enable firewall rules Configure firewall rules to limit access to your storage account to requests that originate from specified IP addresses or ranges, or from a list of subnets in an Azure Virtual Network (VNet). For more information about configuring firewall rules, see Configure Azure Storage firewalls and virtual networks (../common/storage-network-security?toc=/azure/storage/blobs/toc.json) . -

Allow trusted Microsoft services to access the storage account Turning on firewall rules for your storage account blocks incoming requests for data by default, unless the requests originate from a service operating within an Azure Virtual Network (VNet) or from allowed public IP addresses. Requests that are blocked include those from other Azure services, from the Azure portal, from logging and metrics services, and so on. You can permit requests from other Azure services by adding an exception to allow trusted Microsoft services to access the storage account. For more information about adding an exception for trusted Microsoft services, see Configure Azure Storage firewalls and virtual networks (../common/storage-network-security?toc=/azure/storage/blobs/toc.json) . -

Use private endpoints A private endpoint assigns a private IP address from your Azure Virtual Network (VNet) to the storage account. It secures all traffic between your VNet and the storage account over a private link. For more information about private endpoints, see Connect privately to a storage account using Azure Private Endpoint (../../private-link/tutorial-private-endpoint-storage-portal) . -

Use VNet service tags A service tag represents a group of IP address prefixes from a given Azure service. Microsoft manages the address prefixes encompassed by the service tag and automatically updates the service tag as addresses change. For more information about service tags supported by Azure Storage, see Azure service tags overview (../../virtual-network/service-tags-overview) . For a tutorial that shows how to use service tags to create outbound network rules, see Restrict access to PaaS resources (../../virtual-network/tutorial-restrict-network-access-to-resources) . -

Limit network access to specific networks Limiting network access to networks hosting clients requiring access reduces the exposure of your resources to network attacks. Yes (/en-us/azure/defender-for-cloud/implement-security-recommendations)

Configure network routing preference You can configure network routing preference for your Azure storage account to specify how network traffic is routed to your account from clients over the Internet using the Microsoft global network or Internet routing. For more information, see Configure network routing preference for Azure Storage (../common/network-routing-preference) . -

## Logging/Monitoring

Recommendation Comments Defender for Cloud

Track how requests are authorized Enable logging for Azure Storage to track how requests to the service are authorized. The logs indicate whether a request was made anonymously, by using an OAuth 2.0 token, by using Shared Key, or by using a shared access signature (SAS). For more information, see Monitoring Azure Blob Storage with Azure Monitor (monitor-blob-storage) or Azure Storage analytics logging with Classic Monitoring (../common/storage-analytics-logging) . -

Set up alerts in Azure Monitor Configure log alerts to evaluate resources logs at a set frequency and fire an alert based on the results. For more information, see Log alerts in Azure Monitor (/en-us/azure/azure-monitor/alerts/alerts-unified-log) . -

## Next steps

- Azure security documentation (../../security/)
- Secure development documentation (../../security/develop/) .

## Feedback

Was this page helpful?

No

Need help with this topic?

Want to try using Ask Learn to clarify or guide you through this topic?

## Additional resources

- Last updated on 2025-03-04
