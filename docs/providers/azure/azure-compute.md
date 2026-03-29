# Azure Compute

Source pages:
- Overview of virtual machines in Azure: https://learn.microsoft.com/en-us/azure/virtual-machines/overview
- Azure security baseline for Virtual Machines: https://learn.microsoft.com/en-us/azure/virtual-machines/security-recommendations

## Overview of virtual machines in Azure

Source: https://learn.microsoft.com/en-us/azure/virtual-machines/overview

# Virtual machines in Azure

Applies to: ✔️ Linux VMs ✔️ Windows VMs ✔️ Flexible scale sets

Azure virtual machines (VMs) are one of several types of on-demand, scalable computing resources (/en-us/azure/architecture/guide/technology-choices/compute-decision-tree) that Azure offers. Typically, you choose a virtual machine when you need more control over the computing environment than the other choices offer. This article gives you information about what you should consider before you create a virtual machine, how you create it, and how you manage it.

An Azure virtual machine gives you the flexibility of virtualization without having to buy and maintain the physical hardware that runs it. However, you still need to maintain the virtual machine by performing tasks, such as configuring, patching, and installing the software that runs on it.

Azure virtual machines can be used in various ways. Some examples are:

- Development and test – Azure virtual machines offer a quick and easy way to create a computer with specific configurations required to code and test an application.
- Applications in the cloud – Because demand for your application can fluctuate, it might make economic sense to run it on a virtual machine in Azure. You pay for extra virtual machines when you need them and shut them down when you don’t.
- Extended datacenter – virtual machines in an Azure virtual network can easily be connected to your organization’s network.

## What do I need to think about before creating a virtual machine?

There's always a multitude of design considerations (/en-us/azure/architecture/reference-architectures/n-tier/linux-vm) when you build out an application infrastructure in Azure. These aspects of a virtual machine are important to think about before you start:

- The names of your resources
- The location where the resources are stored
- The size of the virtual machine
- The maximum number of virtual machines that can be created
- The operating system that the virtual machine runs
- The configuration of the virtual machine after it starts
- The related resources that the virtual machine needs

Trusted Launch as default (TLaD) is available in preview for new Generation 2 (generation-2) Virtual machines (VMs). With TLaD, any new Generation 2 VMs created through any client tools defaults to Trusted Launch (trusted-launch) with secure boot and vTPM enabled. Register for the TLaD preview (trusted-launch#preview-trusted-launch-as-default) to validate the default changes in your respective environment and prepare for the upcoming change.

## Parts of a VM and how they're billed

When you create a virtual machine, you're also creating resources that support the virtual machine. These resources come with their own costs that should be considered.

The default resources supporting a virtual machine and how they're billed are detailed in the following table:

Resource Description Cost

Virtual network For giving your virtual machine the ability to communicate with other resources Virtual Network pricing (https://azure.microsoft.com/pricing/details/virtual-network/)

A virtual Network Interface Card (NIC) For connecting to the virtual network There's no separate cost for NICs. However, there's a limit to how many NICs you can use based on your VM's size (sizes) . Size your VM accordingly and reference Virtual Machine pricing (https://azure.microsoft.com/pricing/details/virtual-machines/linux/) .

A private IP address and sometimes a public IP address. For communication and data exchange on your network and with external networks IP Addresses pricing (https://azure.microsoft.com/pricing/details/ip-addresses/)

Network security group (NSG) For managing the network traffic to and from your VM. For example, you might need to open port 22 for SSH access, but you might want to block traffic to port 80. Blocking and allowing port access is done through the NSG. There are no additional charges for network security groups in Azure.

OS Disk and possibly separate disks for data. It's a best practice to keep your data on a separate disk from your operating system, in case you ever have a VM fail, you can detach the data disk, and attach it to a new VM. All new virtual machines have an operating system disk and a local disk.
Azure doesn't charge for local disk storage.
The operating system disk, which is usually 127GiB but is smaller for some images, is charged at the regular rate for disks (https://azure.microsoft.com/pricing/details/managed-disks/) .
You can see the cost for attach Premium (SSD based) and Standard (HDD) based disks to your virtual machines on the Managed Disks pricing page (https://azure.microsoft.com/pricing/details/managed-disks/) .

In some cases, a license for the OS For providing your virtual machine runs to run the OS The cost varies based on the number of cores on your VM, so size your VM accordingly (sizes) . The cost can be reduced through the Azure Hybrid Benefit (https://azure.microsoft.com/pricing/hybrid-benefit/#overview) .

You can also choose to have Azure can create and store public and private SSH keys - Azure uses the public key in your VM and you use the private key when you access the VM over SSH. Otherwise, you need a username and password.

By default, these resources are created in the same resource group as the VM.

### Locations

There are multiple geographical regions (https://azure.microsoft.com/regions/) around the world where you can create Azure resources. Usually, the region is called location when you create a virtual machine. For a virtual machine, the location specifies where the virtual hard disks are stored.

This table shows some of the ways you can get a list of available locations.

Method Description

Azure portal Select a location from the list when you create a virtual machine.

Azure PowerShell Use the Get-AzLocation (/en-us/powershell/module/az.resources/get-azlocation) command.

REST API Use the List locations (/en-us/rest/api/resources/subscriptions) operation.

Azure CLI Use the az account list-locations (/en-us/cli/azure/account) operation.

## Availability

There are multiple options to manage the availability of your virtual machines in Azure.

- Availability Zones (/en-us/azure/reliability/availability-zones-overview) are physically separated zones within an Azure region. Availability zones guarantee virtual machine connectivity to at least one instance at least 99.99% of the time when you have two or more instances deployed across two or more Availability Zones in the same Azure region.
- Virtual Machine Scale Sets (../virtual-machine-scale-sets/overview) let you create and manage a group of load balanced virtual machines. The number of virtual machine instances can automatically increase or decrease in response to demand or a defined schedule. Scale sets provide high availability to your applications, and allow you to centrally manage, configure, and update many virtual machines. Virtual machines in a scale set can also be deployed into multiple availability zones, a single availability zone, or regionally.

Fore more information see Availability options for Azure virtual machines (availability) and SLA for Azure virtual machines (https://azure.microsoft.com/support/legal/sla/virtual-machines/v1_9/) .

## Sizes and pricing

The size (sizes) of the virtual machine that you use is determined by the workload that you want to run. The size that you choose then determines factors such as processing power, memory, storage capacity, and network bandwidth. Azure offers a wide variety of sizes to support many types of uses.

Azure charges an hourly price (https://azure.microsoft.com/pricing/details/virtual-machines/linux/) based on the virtual machine’s size and operating system. For partial hours, Azure charges only for the minutes used. Storage is priced and charged separately.

## Scaling to multiple VMs

The number of virtual machines that your application uses can scale up and out to whatever is required to meet your needs. Azure offers several automatic scaling systems and instance types based on the size of your workload. For more information on scaling, compare VM-based compute products. (compare-compute-products)

## Virtual machine total core limits

Your subscription has default quota limits (/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits) in place that could impact the deployment of many virtual machines for your project. The current limit on a per subscription basis is 20 virtual machine total cores per region. Limits can be raised by filing a support ticket requesting an increase (/en-us/azure/azure-portal/supportability/regional-quota-requests)

## Managed Disks

Managed Disks handles Azure Storage account creation and management in the background for you, and ensures that you don't have to worry about the scalability limits of the storage account. You specify the disk size and the performance tier (Standard or Premium), and Azure creates and manages the disk. As you add disks or scale the virtual machine up and down, you don't have to worry about the storage being used. If you're creating new virtual machines, use the Azure CLI (linux/quick-create-cli) or the Azure portal to create virtual machines with Managed OS and data disks. If you have virtual machines with unmanaged disks, you can convert your virtual machines to be backed with Managed Disks (linux/convert-unmanaged-to-managed-disks) .

You can also manage your custom images in one storage account per Azure region, and use them to create hundreds of virtual machines in the same subscription. For more information about Managed Disks, see the Managed Disks Overview (managed-disks-overview) .

## Distributions

Microsoft Azure supports various Linux and Windows distributions. You can find available distributions in the marketplace (https://azuremarketplace.microsoft.com) , Azure portal or by querying results using CLI, PowerShell, and REST APIs.

This table shows some ways that you can find the information for an image.

Method Description

Azure portal The values are automatically specified for you when you select an image to use.

Azure PowerShell Get-AzVMImagePublisher (/en-us/powershell/module/az.compute/get-azvmimagepublisher) -Location location
Get-AzVMImageOffer (/en-us/powershell/module/az.compute/get-azvmimageoffer) -Location location -Publisher publisherName
Get-AzVMImageSku (/en-us/powershell/module/az.compute/get-azvmimagesku) -Location location -Publisher publisherName -Offer offerName

REST APIs List image publishers (/en-us/rest/api/compute/platformimages/platformimages-list-publishers)
List image offers (/en-us/rest/api/compute/platformimages/platformimages-list-publisher-offers)
List image skus (/en-us/rest/api/compute/platformimages/platformimages-list-publisher-offer-skus)

Azure CLI az vm image list-publishers (/en-us/cli/azure/vm/image) --location location
az vm image list-offers (/en-us/cli/azure/vm/image) --location location --publisher publisherName
az vm image list-skus (/en-us/cli/azure/vm) --location location --publisher publisherName --offer offerName

Microsoft works closely with partners to ensure the images available are updated and optimized for an Azure runtime. For more information on Azure partner offers, see the Azure Marketplace (https://azuremarketplace.microsoft.com/marketplace/apps?filters=partners%3Bvirtual-machine-images&page=1)

## Cloud-init

Azure supports for cloud-init (https://cloud-init.io/) across most Linux distributions that support it. We're actively working with our Linux partners to make cloud-init enabled images available in the Azure Marketplace. These images make your cloud-init deployments and configurations work seamlessly with virtual machines and virtual machine scale sets.

For more information, see Using cloud-init on Azure Linux virtual machines (linux/using-cloud-init) .

## Storage

- Introduction to Microsoft Azure Storage (/en-us/azure/storage/common/storage-introduction)
- Add a disk to a Linux virtual machine using the azure-cli (linux/add-disk)
- How to attach a data disk to a Linux virtual machine in the Azure portal (linux/attach-disk-portal)

### Local temporary storage

Some Azure VM sizes include local temporary ephemeral storage, with some of the newer sizes using Temporary local NVMe disks (enable-nvme-temp-faqs) . Local temporary storage uses additional disks provisioned directly as local storage to an Azure virtual machine host, rather than on remote Azure Storage. This type of storage is best suited for data that does not need to be retained permanently, such as caches, buffers, and temporary files. Since data stored on these disks isn't backed up, it's lost when the VM is deallocated or deleted. The ephemeral storage is recreated on startup. Local ephemeral disks are different from Ephemeral OS disks (ephemeral-os-disks#local-temporary-storage) .

Local temporary disks present just like other remote storage such as Premium SSD v2 disks, but have added performance benefits and don't count against the IOPS and throughput limits of the VM.

The following lists key characteristics of local ephemeral storage:

- Ultra-low latency : Read/write operations occur on hardware physically co-located with the VM's compute resources, minimizing network hops and enabling sub-millisecond response times.
- Superior IOPS and throughput : Performance scales with the underlying local storage, often delivering 8-10 times higher IOPS than Standard HDDs when using Premium SSD as the base, with limits tied to the VM size (up to the NVMe disk capacity, capped at 2,040 GiB).

Azure VM sizes featuring a 'd' in their naming convention - such as the Da d sv6, Ea d sv6, and FXm d sv2 series - include dedicated local NVMe storage. These sizes enable placing temporary files, swap space, or high-I/O components like SQL Server's`tempdb`database files on the ephemeral disk for enhanced performance.

## Networking

- Virtual Network Overview (/en-us/azure/virtual-network/virtual-networks-overview)
- IP addresses in Azure (/en-us/azure/virtual-network/ip-services/public-ip-addresses)
- Opening ports to a Linux virtual machine in Azure (linux/nsg-quickstart)
- Create a Fully Qualified Domain Name in the Azure portal (create-fqdn)

## Service disruptions

At Microsoft, we work hard to make sure that our services are always available to you when you need them. Forces beyond our control sometimes impact us in ways that cause unplanned service disruptions.

Microsoft provides a Service Level Agreement (SLA) for its services as a commitment for uptime and connectivity. The SLA for individual Azure services can be found at Azure Service Level Agreements (https://azure.microsoft.com/support/legal/sla/) .

Azure already has many built-in platform features that support highly available applications. For more about these services, read Disaster recovery and high availability for Azure applications (/en-us/azure/architecture/framework/resiliency/backup-and-recovery) .

This article covers a true disaster recovery scenario, when a whole region experiences an outage due to major natural disaster or widespread service interruption. These are rare occurrences, but you must prepare for the possibility that there's an outage of an entire region. If an entire region experiences a service disruption, the locally redundant copies of your data would temporarily be unavailable. If you enabled geo-replication, three additional copies of your Azure Storage blobs and tables are stored in a different region. In the event of a complete regional outage or a disaster in which the primary region isn't recoverable, Azure remaps all of the DNS entries to the geo-replicated region.

In the case of a service disruption of the entire region where your Azure virtual machine application is deployed, we provide the following guidance for Azure virtual machines.

### Option 1: Initiate a failover by using Azure Site Recovery

You can configure Azure Site Recovery for your VMs so that you can recover your application with a single click in matter of minutes. You can replicate to Azure region of your choice and not restricted to paired regions. You can get started by replicating your virtual machines (/en-us/azure/site-recovery/azure-to-azure-quickstart) . You can create a recovery plan (/en-us/azure/site-recovery/site-recovery-create-recovery-plans) so that you can automate the entire failover process for your application. You can test your failovers (/en-us/azure/site-recovery/site-recovery-test-failover-to-azure) beforehand without impacting production application or the ongoing replication. In the event of a primary region disruption, you just initiate a failover (/en-us/azure/site-recovery/site-recovery-failover) and bring your application in target region.

### Option 2: Wait for recovery

In this case, no action on your part is required. Know that we're working diligently to restore service availability. You can see the current service status on our Azure Service Health Dashboard (https://azure.microsoft.com/status/) .

This option is the best if you don't set up Azure Site Recovery, read-access geo-redundant storage, or geo-redundant storage prior to the disruption. If you set up geo-redundant storage or read-access geo-redundant storage for the storage account where your VM virtual hard drives (VHDs) are stored, you can look to recover the base image VHD and try to provision a new VM from it. This option isn't preferred because there are no guarantees of synchronization of data, which means this option isn't guaranteed to work.

Be aware that you don't have any control over this process, and it will only occur for region-wide service disruptions. Because of this, you must also rely on other application-specific backup strategies to achieve the highest level of availability. For more information, see the section on Data strategies for disaster recovery (/en-us/azure/architecture/reliability/disaster-recovery#disaster-recovery-plan) .

### Resources for service disruptions

Start protecting your applications running on Azure virtual machines (/en-us/azure/site-recovery/azure-to-azure-quickstart) using Azure Site Recovery

To learn more about how to implement a disaster recovery and high availability strategy, see Disaster recovery and high availability for Azure applications (/en-us/azure/architecture/framework/resiliency/backup-and-recovery) .

To develop a detailed technical understanding of a cloud platform’s capabilities, see Azure resiliency technical guidance (/en-us/azure/data-lake-store/data-lake-store-disaster-recovery-guidance) .

If the instructions aren't clear, or if you would like Microsoft to do the operations on your behalf, contact Customer Support (https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade) .

## Data residency

In Azure, the feature to enable storing customer data in a single region is currently only available in the Southeast Asia Region (Singapore) of the Asia Pacific Geo and Brazil South (Sao Paulo State) Region of Brazil Geo. For all other regions, customer data is stored in Geo. For more information, see Trust Center (https://azure.microsoft.com/global-infrastructure/data-residency/) .

## Next steps

Create your first virtual machine!

- Portal (linux/quick-create-portal)
- Azure CLI (linux/quick-create-cli)
- PowerShell (linux/quick-create-powershell)

## Feedback

Was this page helpful?

No

Need help with this topic?

Want to try using Ask Learn to clarify or guide you through this topic?

## Additional resources

- Last updated on 2025-12-01


## Azure security baseline for Virtual Machines

Source: https://learn.microsoft.com/en-us/azure/virtual-machines/security-recommendations

# Azure security baseline for Virtual Machines - Windows Virtual Machines

This security baseline applies guidance from the Microsoft cloud security benchmark version 1.0 (/en-us/security/benchmark/azure/overview) to Virtual Machines - Windows Virtual Machines. The Microsoft cloud security benchmark provides recommendations on how you can secure your cloud solutions on Azure. The content is grouped by the security controls defined by the Microsoft cloud security benchmark and the related guidance applicable to Virtual Machines - Windows Virtual Machines.

You can monitor this security baseline and its recommendations using Microsoft Defender for Cloud. Azure Policy definitions will be listed in the Regulatory Compliance section of the Microsoft Defender for Cloud portal page.

When a feature has relevant Azure Policy Definitions, they are listed in this baseline to help you measure compliance with the Microsoft cloud security benchmark controls and recommendations. Some recommendations may require a paid Microsoft Defender plan to enable certain security scenarios.

Features not applicable to Virtual Machines - Windows Virtual Machines have been excluded. To see how Virtual Machines - Windows Virtual Machines completely maps to the Microsoft cloud security benchmark, see the full Virtual Machines - Windows Virtual Machines security baseline mapping file (https://github.com/MicrosoftDocs/SecurityBenchmarks/blob/master/Azure%20Offer%20Security%20Baselines/3.0/virtual-machines-windows%20virtual%20machines-azure-security-benchmark-v3-latest-security-baseline.xlsx) .

## Security profile

The security profile summarizes high-impact behaviors of Virtual Machines - Windows Virtual Machines, which may result in increased security considerations.

Service Behavior Attribute Value

Product Category Compute

Customer can access HOST / OS Full Access

Service can be deployed into customer's virtual network True

Stores customer content at rest True

## Network security

For more information, see the Microsoft cloud security benchmark: Network security (../mcsb-network-security) .

### NS-1: Establish network segmentation boundaries

#### Features

##### Virtual Network Integration

Description : Service supports deployment into customer's private Virtual Network (VNet). Learn more (/en-us/azure/virtual-network/virtual-network-for-azure-services#services-that-can-be-deployed-into-a-virtual-network) .

Supported Enabled By Default Configuration Responsibility

True True Microsoft

Configuration Guidance : No additional configurations are required as this is enabled on a default deployment.

Reference : Virtual networks and virtual machines in Azure (/en-us/azure/virtual-network/network-overview)

##### Network Security Group Support

Description : Service network traffic respects Network Security Groups rule assignment on its subnets. Learn more (/en-us/azure/virtual-network/network-security-groups-overview) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Configuration Guidance : Use network security groups (NSG) to restrict or monitor traffic by port, protocol, source IP address, or destination IP address. Create NSG rules to restrict your service's open ports (such as preventing management ports from being accessed from untrusted networks). Be aware that by default, NSGs deny all inbound traffic but allow traffic from virtual network and Azure Load Balancers.

When you create an Azure virtual machine (VM), you must create a virtual network or use an existing virtual network and configure the VM with a subnet. Ensure that all deployed subnets have a Network Security Group applied with network access controls specific to your applications trusted ports and sources.

Reference : Network security groups (/en-us/azure/virtual-network/network-overview#network-security-groups)

#### Microsoft Defender for Cloud monitoring

Azure Policy built-in definitions - Microsoft.ClassicCompute :

Name
(Azure portal) Description Effect(s) Version
(GitHub)

All network ports should be restricted on network security groups associated to your virtual machine (https://portal.azure.com/#blade/Microsoft_Azure_Policy/PolicyDetailBlade/definitionId/%2Fproviders%2FMicrosoft.Authorization%2FpolicyDefinitions%2F9daedab3-fb2d-461e-b861-71790eead4f6) Azure Security Center has identified some of your network security groups' inbound rules to be too permissive. Inbound rules should not allow access from 'Any' or 'Internet' ranges. This can potentially enable attackers to target your resources. AuditIfNotExists, Disabled 3.0.0 (https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Security%20Center/ASC_UnprotectedEndpoints_Audit.json)

Azure Policy built-in definitions - Microsoft.Compute :

Name
(Azure portal) Description Effect(s) Version
(GitHub)

Adaptive network hardening recommendations should be applied on internet facing virtual machines (https://portal.azure.com/#blade/Microsoft_Azure_Policy/PolicyDetailBlade/definitionId/%2Fproviders%2FMicrosoft.Authorization%2FpolicyDefinitions%2F08e6af2d-db70-460a-bfe9-d5bd474ba9d6) Azure Security Center analyzes the traffic patterns of Internet facing virtual machines and provides Network Security Group rule recommendations that reduce the potential attack surface AuditIfNotExists, Disabled 3.0.0 (https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Security%20Center/ASC_AdaptiveNetworkHardenings_Audit.json)

### NS-2: Secure cloud services with network controls

#### Features

##### Disable Public Network Access

Description : Service supports disabling public network access either through using service-level IP ACL filtering rule (not NSG or Azure Firewall) or using a 'Disable Public Network Access' toggle switch. Learn more (/en-us/security/benchmark/azure/security-controls-v3-network-security#ns-2-secure-cloud-services-with-network-controls) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Configuration Guidance : Use services at the OS-level such as Windows Defender Firewall to provide network filtering to disable public access.

## Identity management

For more information, see the Microsoft cloud security benchmark: Identity management (../mcsb-identity-management) .

### IM-1: Use centralized identity and authentication system

#### Features

##### Azure AD Authentication Required for Data Plane Access

Description : Service supports using Azure AD authentication for data plane access. Learn more (/en-us/azure/active-directory/authentication/overview-authentication) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Configuration Guidance : Use Azure Active Directory (Azure AD) as the default authentication method to control your data plane access.

Reference : Log in to a Windows virtual machine in Azure by using Azure AD including passwordless (/en-us/azure/active-directory/devices/howto-vm-sign-in-azure-ad-windows)

##### Local Authentication Methods for Data Plane Access

Description : Local authentications methods supported for data plane access, such as a local username and password. Learn more (/en-us/azure/app-service/overview-authentication-authorization) .

Supported Enabled By Default Configuration Responsibility

True True Microsoft

Feature notes : A local administrator account is created by default during the initial deployment of the virtual machine. Avoid the usage of local authentication methods or accounts, these should be disabled wherever possible. Instead use Azure AD to authenticate where possible.

Configuration Guidance : No additional configurations are required as this is enabled on a default deployment.

### IM-3: Manage application identities securely and automatically

#### Features

##### Managed Identities

Description : Data plane actions support authentication using managed identities. Learn more (/en-us/azure/active-directory/managed-identities-azure-resources/overview) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Feature notes : Managed identity is typically leveraged by Windows VM to authenticate to other services. If the Windows VM supports Azure AD authentication then managed identity may be supported.

Configuration Guidance : Use Azure managed identities instead of service principals when possible, which can authenticate to Azure services and resources that support Azure Active Directory (Azure AD) authentication. Managed identity credentials are fully managed, rotated, and protected by the platform, avoiding hard-coded credentials in source code or configuration files.

##### Service Principals

Description : Data plane supports authentication using service principals. Learn more (/en-us/powershell/azure/create-azure-service-principal-azureps) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Feature notes : Service principals may be used by applications running in the Windows VM.

Configuration Guidance : There is no current Microsoft guidance for this feature configuration. Please review and determine if your organization wants to configure this security feature.

#### Microsoft Defender for Cloud monitoring

Azure Policy built-in definitions - Microsoft.Compute :

Name
(Azure portal) Description Effect(s) Version
(GitHub)

Virtual machines' Guest Configuration extension should be deployed with system-assigned managed identity (https://portal.azure.com/#blade/Microsoft_Azure_Policy/PolicyDetailBlade/definitionId/%2Fproviders%2FMicrosoft.Authorization%2FpolicyDefinitions%2Fd26f7642-7545-4e18-9b75-8c9bbdee3a9a) The Guest Configuration extension requires a system assigned managed identity. Azure virtual machines in the scope of this policy will be non-compliant when they have the Guest Configuration extension installed but do not have a system assigned managed identity. Learn more at https://aka.ms/gcpol AuditIfNotExists, Disabled 1.0.1 (https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Security%20Center/ASC_GCExtOnVmWithNoSAMI.json)

### IM-7: Restrict resource access based on conditions

#### Features

##### Conditional Access for Data Plane

Description : Data plane access can be controlled using Azure AD Conditional Access Policies. Learn more (/en-us/azure/active-directory/conditional-access/overview) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Feature notes : Use Azure AD as a core authentication platform to RDP into Windows Server 2019 Datacenter edition and later, or Windows 10 1809 and later. You can then centrally control and enforce Azure role-based access control (RBAC) and Conditional Access policies that allow or deny access to the VMs.

Configuration Guidance : Define the applicable conditions and criteria for Azure Active Directory (Azure AD) conditional access in the workload. Consider common use cases such as blocking or granting access from specific locations, blocking risky sign-in behavior, or requiring organization-managed devices for specific applications.

Reference : Log in to a Windows virtual machine in Azure by using Azure AD including passwordless (/en-us/azure/active-directory/devices/howto-vm-sign-in-azure-ad-windows)

### IM-8: Restrict the exposure of credential and secrets

#### Features

##### Service Credential and Secrets Support Integration and Storage in Azure Key Vault

Description : Data plane supports native use of Azure Key Vault for credential and secrets store. Learn more (/en-us/azure/key-vault/secrets/about-secrets) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Feature notes : Within the data plane or operating system, services may call Azure Key Vault for credentials or secrets.

Configuration Guidance : Ensure that secrets and credentials are stored in secure locations such as Azure Key Vault, instead of embedding them into code or configuration files.

## Privileged access

For more information, see the Microsoft cloud security benchmark: Privileged access (../mcsb-privileged-access) .

### PA-1: Separate and limit highly privileged/administrative users

#### Features

##### Local Admin Accounts

Description : Service has the concept of a local administrative account. Learn more (/en-us/security/benchmark/azure/security-controls-v3-privileged-access#pa-1-separate-and-limit-highly-privilegedadministrative-users) .

Supported Enabled By Default Configuration Responsibility

True True Microsoft

Feature notes : Avoid the usage of local authentication methods or accounts, these should be disabled wherever possible. Instead use Azure AD to authenticate where possible.

Configuration Guidance : No additional configurations are required as this is enabled on a default deployment.

Reference : Quickstart: Create a Windows virtual machine in the Azure portal (/en-us/azure/virtual-machines/windows/quick-create-portal)

### PA-7: Follow just enough administration (least privilege) principle

#### Features

##### Azure RBAC for Data Plane

Description : Azure Role-Based Access Control (Azure RBAC) can be used to managed access to service's data plane actions. Learn more (/en-us/azure/role-based-access-control/overview) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Feature notes : Use Azure AD as a core authentication platform to RDP into Windows Server 2019 Datacenter edition and later, or Windows 10 1809 and later. You can then centrally control and enforce Azure role-based access control (RBAC) and Conditional Access policies that allow or deny access to the VMs.

Configuration Guidance : With RBAC, specify who can log in to a VM as a regular user or with administrator privileges. When users join your team, you can update the Azure RBAC policy for the VM to grant access as appropriate. When employees leave your organization and their user accounts are disabled or removed from Azure AD, they no longer have access to your resources.

Reference : Log in to a Windows virtual machine in Azure by using Azure AD including passwordless (/en-us/azure/active-directory/devices/howto-vm-sign-in-azure-ad-windows)

### PA-8: Determine access process for cloud provider support

#### Features

##### Customer Lockbox

Description : Customer Lockbox can be used for Microsoft support access. Learn more (/en-us/azure/security/fundamentals/customer-lockbox-overview) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Configuration Guidance : In support scenarios where Microsoft needs to access your data, use Customer Lockbox to review, then approve or reject each of Microsoft's data access requests.

## Data protection

For more information, see the Microsoft cloud security benchmark: Data protection (../mcsb-data-protection) .

### DP-1: Discover, classify, and label sensitive data

#### Features

##### Sensitive Data Discovery and Classification

Description : Tools (such as Azure Purview or Azure Information Protection) can be used for data discovery and classification in the service. Learn more (/en-us/security/benchmark/azure/security-controls-v3-data-protection#dp-1-discover-classify-and-label-sensitive-data) .

Supported Enabled By Default Configuration Responsibility

False Not Applicable Not Applicable

Configuration Guidance : This feature is not supported to secure this service.

### DP-2: Monitor anomalies and threats targeting sensitive data

#### Features

##### Data Leakage/Loss Prevention

Description : Service supports DLP solution to monitor sensitive data movement (in customer's content). Learn more (/en-us/security/benchmark/azure/security-controls-v3-data-protection#dp-2-monitor-anomalies-and-threats-targeting-sensitive-data) .

Supported Enabled By Default Configuration Responsibility

False Not Applicable Not Applicable

Configuration Guidance : This feature is not supported to secure this service.

### DP-3: Encrypt sensitive data in transit

#### Features

##### Data in Transit Encryption

Description : Service supports data in-transit encryption for data plane. Learn more (/en-us/azure/security/fundamentals/double-encryption#data-in-transit) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Feature notes : Certain communication protocols such as SSH are encrypted by default. However, other services such as HTTP must be configured to use TLS for encryption.

Configuration Guidance : Enable secure transfer in services where there is a native data in transit encryption feature built in. Enforce HTTPS on any web applications and services and ensure TLS v1.2 or later is used. Legacy versions such as SSL 3.0, TLS v1.0 should be disabled. For remote management of Virtual Machines, use SSH (for Linux) or RDP/TLS (for Windows) instead of an unencrypted protocol.

Reference : In-transit encryption in VMs (/en-us/azure/security/fundamentals/encryption-overview#in-transit-encryption-in-vms)

#### Microsoft Defender for Cloud monitoring

Azure Policy built-in definitions - Microsoft.Compute :

Name
(Azure portal) Description Effect(s) Version
(GitHub)

Windows machines should be configured to use secure communication protocols (https://portal.azure.com/#blade/Microsoft_Azure_Policy/PolicyDetailBlade/definitionId/%2Fproviders%2FMicrosoft.Authorization%2FpolicyDefinitions%2F5752e6d6-1206-46d8-8ab1-ecc2f71a8112) To protect the privacy of information communicated over the Internet, your machines should use the latest version of the industry-standard cryptographic protocol, Transport Layer Security (TLS). TLS secures communications over a network by encrypting a connection between machines. AuditIfNotExists, Disabled 4.1.1 (https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Guest%20Configuration/SecureWebProtocol_AINE.json)

### DP-4: Enable data at rest encryption by default

#### Features

##### Data at Rest Encryption Using Platform Keys

Description : Data at-rest encryption using platform keys is supported, any customer content at rest is encrypted with these Microsoft managed keys. Learn more (/en-us/azure/security/fundamentals/encryption-atrest#encryption-at-rest-in-microsoft-cloud-services) .

Supported Enabled By Default Configuration Responsibility

True True Microsoft

Feature notes : By default, managed disks use platform-managed encryption keys. All managed disks, snapshots, images, and data written to existing managed disks are automatically encrypted-at-rest with platform-managed keys.

Configuration Guidance : No additional configurations are required as this is enabled on a default deployment.

Reference : Server-side encryption of Azure Disk Storage - Platform-managed Keys (/en-us/azure/virtual-machines/disk-encryption#platform-managed-keys)

#### Microsoft Defender for Cloud monitoring

Azure Policy built-in definitions - Microsoft.ClassicCompute :

Name
(Azure portal) Description Effect(s) Version
(GitHub)

Virtual machines should encrypt temp disks, caches, and data flows between Compute and Storage resources (https://portal.azure.com/#blade/Microsoft_Azure_Policy/PolicyDetailBlade/definitionId/%2Fproviders%2FMicrosoft.Authorization%2FpolicyDefinitions%2F0961003e-5a0a-4549-abde-af6a37f2724d) By default, a virtual machine's OS and data disks are encrypted-at-rest using platform-managed keys. Temp disks, data caches and data flowing between compute and storage aren't encrypted. Disregard this recommendation if: 1. using encryption-at-host, or 2. server-side encryption on Managed Disks meets your security requirements. Learn more in: Server-side encryption of Azure Disk Storage: https://aka.ms/disksse, Different disk encryption offerings: https://aka.ms/diskencryptioncomparison AuditIfNotExists, Disabled 2.0.3 (https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Security%20Center/ASC_UnencryptedVMDisks_Audit.json)

Azure Policy built-in definitions - Microsoft.Compute :

Name
(Azure portal) Description Effect(s) Version
(GitHub)

[Preview]: Linux virtual machines should enable Azure Disk Encryption or EncryptionAtHost. (https://portal.azure.com/#blade/Microsoft_Azure_Policy/PolicyDetailBlade/definitionId/%2Fproviders%2FMicrosoft.Authorization%2FpolicyDefinitions%2Fca88aadc-6e2b-416c-9de2-5a0f01d1693f) By default, a virtual machine's OS and data disks are encrypted-at-rest using platform-managed keys; temp disks and data caches aren't encrypted, and data isn't encrypted when flowing between compute and storage resources. Use Azure Disk Encryption or EncryptionAtHost to encrypt all this data.Visit https://aka.ms/diskencryptioncomparison to compare encryption offerings. This policy requires two prerequisites to be deployed to the policy assignment scope. For details, visit https://aka.ms/gcpol . AuditIfNotExists, Disabled 1.2.0-preview (https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Guest%20Configuration/LinuxVMEncryption_AINE.json)

### DP-5: Use customer-managed key option in data at rest encryption when required

#### Features

##### Data at Rest Encryption Using CMK

Description : Data at-rest encryption using customer-managed keys is supported for customer content stored by the service. Learn more (/en-us/azure/security/fundamentals/encryption-models) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Feature notes : You can choose to manage encryption at the level of each managed disk, with your own keys. When you specify a customer-managed key, that key is used to protect and control access to the key that encrypts your data. Customer-managed keys offer greater flexibility to manage access controls.

Configuration Guidance : If required for regulatory compliance, define the use case and service scope where encryption using customer-managed keys are needed. Enable and implement data at rest encryption using customer-managed key for those services.

Virtual disks on Virtual Machines (VM) are encrypted at rest using either Server-side encryption or Azure disk encryption (ADE). Azure Disk Encryption leverages the BitLocker feature of Windows to encrypt managed disks with customer-managed keys within the guest VM. Server-side encryption with customer-managed keys improves on ADE by enabling you to use any OS types and images for your VMs by encrypting data in the Storage service.

Reference : Server-side encryption of Azure Disk Storage (/en-us/azure/virtual-machines/disk-encryption#customer-managed-keys)

### DP-6: Use a secure key management process

#### Features

##### Key Management in Azure Key Vault

Description : The service supports Azure Key Vault integration for any customer keys, secrets, or certificates. Learn more (/en-us/azure/key-vault/general/overview) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Configuration Guidance : Use Azure Key Vault to create and control the life cycle of your encryption keys, including key generation, distribution, and storage. Rotate and revoke your keys in Azure Key Vault and your service based on a defined schedule or when there is a key retirement or compromise. When there is a need to use customer-managed key (CMK) in the workload, service, or application level, ensure you follow the best practices for key management: Use a key hierarchy to generate a separate data encryption key (DEK) with your key encryption key (KEK) in your key vault. Ensure keys are registered with Azure Key Vault and referenced via key IDs from the service or application. If you need to bring your own key (BYOK) to the service (such as importing HSM-protected keys from your on-premises HSMs into Azure Key Vault), follow recommended guidelines to perform initial key generation and key transfer.

Reference : Create and configure a key vault for Azure Disk Encryption on a Windows VM (/en-us/azure/virtual-machines/windows/disk-encryption-key-vault?tabs=azure-portal)

### DP-7: Use a secure certificate management process

#### Features

##### Certificate Management in Azure Key Vault

Description : The service supports Azure Key Vault integration for any customer certificates. Learn more (/en-us/azure/key-vault/certificates/certificate-scenarios) .

Supported Enabled By Default Configuration Responsibility

False Not Applicable Not Applicable

Configuration Guidance : This feature is not supported to secure this service.

## Asset management

For more information, see the Microsoft cloud security benchmark: Asset management (../mcsb-asset-management) .

### AM-2: Use only approved services

#### Features

##### Azure Policy Support

Description : Service configurations can be monitored and enforced via Azure Policy. Learn more (/en-us/azure/governance/policy/tutorials/create-and-manage) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Configuration Guidance : Azure Policy can be used to define the desired behavior for your organization's Windows VMs and Linux VMs. By using policies, an organization can enforce various conventions and rules throughout the enterprise and define and implement standard security configurations for Azure Virtual Machines. Enforcement of the desired behavior can help mitigate risk while contributing to the success of the organization.

Reference : Azure Policy built-in definitions for Azure Virtual Machines (/en-us/azure/virtual-machines/policy-reference)

#### Microsoft Defender for Cloud monitoring

Azure Policy built-in definitions - Microsoft.ClassicCompute :

Name
(Azure portal) Description Effect(s) Version
(GitHub)

Virtual machines should be migrated to new Azure Resource Manager resources (https://portal.azure.com/#blade/Microsoft_Azure_Policy/PolicyDetailBlade/definitionId/%2Fproviders%2FMicrosoft.Authorization%2FpolicyDefinitions%2F1d84d5fb-01f6-4d12-ba4f-4a26081d403d) Use new Azure Resource Manager for your virtual machines to provide security enhancements such as: stronger access control (RBAC), better auditing, Azure Resource Manager based deployment and governance, access to managed identities, access to key vault for secrets, Azure AD-based authentication and support for tags and resource groups for easier security management Audit, Deny, Disabled 1.0.0 (https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Compute/ClassicCompute_Audit.json)

Azure Policy built-in definitions - Microsoft.Compute :

Name
(Azure portal) Description Effect(s) Version
(GitHub)

Virtual machines should be migrated to new Azure Resource Manager resources (https://portal.azure.com/#blade/Microsoft_Azure_Policy/PolicyDetailBlade/definitionId/%2Fproviders%2FMicrosoft.Authorization%2FpolicyDefinitions%2F1d84d5fb-01f6-4d12-ba4f-4a26081d403d) Use new Azure Resource Manager for your virtual machines to provide security enhancements such as: stronger access control (RBAC), better auditing, Azure Resource Manager based deployment and governance, access to managed identities, access to key vault for secrets, Azure AD-based authentication and support for tags and resource groups for easier security management Audit, Deny, Disabled 1.0.0 (https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Compute/ClassicCompute_Audit.json)

### AM-5: Use only approved applications in virtual machine

#### Features

##### Microsoft Defender for Cloud - Adaptive Application Controls

Description : Service can limit what customer applications run on the virtual machine using Adaptive Application Controls in Microsoft Defender for Cloud. Learn more (/en-us/azure/defender-for-cloud/adaptive-application-controls) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Configuration Guidance : Use Microsoft Defender for Cloud adaptive application controls to discover applications running on virtual machines (VMs) and generate an application allow list to mandate which approved applications can run in the VM environment.

Reference : Use adaptive application controls to reduce your machines' attack surfaces (/en-us/azure/defender-for-cloud/adaptive-application-controls)

#### Microsoft Defender for Cloud monitoring

Azure Policy built-in definitions - Microsoft.ClassicCompute :

Name
(Azure portal) Description Effect(s) Version
(GitHub)

Adaptive application controls for defining safe applications should be enabled on your machines (https://portal.azure.com/#blade/Microsoft_Azure_Policy/PolicyDetailBlade/definitionId/%2Fproviders%2FMicrosoft.Authorization%2FpolicyDefinitions%2F47a6b606-51aa-4496-8bb7-64b11cf66adc) Enable application controls to define the list of known-safe applications running on your machines, and alert you when other applications run. This helps harden your machines against malware. To simplify the process of configuring and maintaining your rules, Security Center uses machine learning to analyze the applications running on each machine and suggest the list of known-safe applications. AuditIfNotExists, Disabled 3.0.0 (https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Security%20Center/ASC_AdaptiveApplicationControls_Audit.json)

Azure Policy built-in definitions - Microsoft.Compute :

Name
(Azure portal) Description Effect(s) Version
(GitHub)

Adaptive application controls for defining safe applications should be enabled on your machines (https://portal.azure.com/#blade/Microsoft_Azure_Policy/PolicyDetailBlade/definitionId/%2Fproviders%2FMicrosoft.Authorization%2FpolicyDefinitions%2F47a6b606-51aa-4496-8bb7-64b11cf66adc) Enable application controls to define the list of known-safe applications running on your machines, and alert you when other applications run. This helps harden your machines against malware. To simplify the process of configuring and maintaining your rules, Security Center uses machine learning to analyze the applications running on each machine and suggest the list of known-safe applications. AuditIfNotExists, Disabled 3.0.0 (https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Security%20Center/ASC_AdaptiveApplicationControls_Audit.json)

## Logging and threat detection

For more information, see the Microsoft cloud security benchmark: Logging and threat detection (../mcsb-logging-threat-detection) .

### LT-1: Enable threat detection capabilities

#### Features

##### Microsoft Defender for Service / Product Offering

Description : Service has an offering-specific Microsoft Defender solution to monitor and alert on security issues. Learn more (/en-us/azure/security-center/azure-defender) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Configuration Guidance : Defender for Servers extends protection to your Windows and Linux machines running in Azure. Defender for Servers integrates with Microsoft Defender for Endpoint to provide endpoint detection and response (EDR), and also provides a host of additional threat protection features, such as security baselines and OS level assessments, vulnerability assessment scanning, adaptive application controls (AAC), file integrity monitoring (FIM), and more.

Reference : Plan your Defender for Servers deployment (/en-us/azure/defender-for-cloud/plan-defender-for-servers)

#### Microsoft Defender for Cloud monitoring

Azure Policy built-in definitions - Microsoft.Compute :

Name
(Azure portal) Description Effect(s) Version
(GitHub)

Windows Defender Exploit Guard should be enabled on your machines (https://portal.azure.com/#blade/Microsoft_Azure_Policy/PolicyDetailBlade/definitionId/%2Fproviders%2FMicrosoft.Authorization%2FpolicyDefinitions%2Fbed48b13-6647-468e-aa2f-1af1d3f4dd40) Windows Defender Exploit Guard uses the Azure Policy Guest Configuration agent. Exploit Guard has four components that are designed to lock down devices against a wide variety of attack vectors and block behaviors commonly used in malware attacks while enabling enterprises to balance their security risk and productivity requirements (Windows only). AuditIfNotExists, Disabled 2.0.0 (https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Guest%20Configuration/WindowsDefenderExploitGuard_AINE.json)

### LT-4: Enable logging for security investigation

#### Features

##### Azure Resource Logs

Description : Service produces resource logs that can provide enhanced service-specific metrics and logging. The customer can configure these resource logs and send them to their own data sink like a storage account or log analytics workspace. Learn more (/en-us/azure/azure-monitor/platform/platform-logs-overview) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Configuration Guidance : Azure Monitor starts automatically collecting metric data for your virtual machine host when you create the VM. To collect logs and performance data from the guest operating system of the virtual machine, though, you must install the Azure Monitor agent. You can install the agent and configure collection using either VM insights (/en-us/azure/virtual-machines/monitor-vm?toc=https%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fazure%2Fvirtual-machine-scale-sets%2Ftoc.json&bc=https%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fazure%2Fbread%2Ftoc.json#vm-insights) or by creating a data collection rule (/en-us/azure/virtual-machines/monitor-vm?toc=https%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fazure%2Fvirtual-machine-scale-sets%2Ftoc.json&bc=https%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fazure%2Fbread%2Ftoc.json#create-data-collection-rule) .

Reference : Log Analytics agent overview (/en-us/azure/azure-monitor/agents/log-analytics-agent#data-collected)

#### Microsoft Defender for Cloud monitoring

Azure Policy built-in definitions - Microsoft.Compute :

Name
(Azure portal) Description Effect(s) Version
(GitHub)

[Preview]: Network traffic data collection agent should be installed on Linux virtual machines (https://portal.azure.com/#blade/Microsoft_Azure_Policy/PolicyDetailBlade/definitionId/%2Fproviders%2FMicrosoft.Authorization%2FpolicyDefinitions%2F04c4380f-3fae-46e8-96c9-30193528f602) Security Center uses the Microsoft Dependency agent to collect network traffic data from your Azure virtual machines to enable advanced network protection features such as traffic visualization on the network map, network hardening recommendations and specific network threats. AuditIfNotExists, Disabled 1.0.2-preview (https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Monitoring/ASC_Dependency_Agent_Audit_Linux.json)

## Posture and vulnerability management

For more information, see the Microsoft cloud security benchmark: Posture and vulnerability management (../mcsb-posture-vulnerability-management) .

### PV-3: Define and establish secure configurations for compute resources

#### Features

##### Azure Automation State Configuration

Description : Azure Automation State Configuration can be used to maintain the security configuration of the operating system. Learn more (/en-us/azure/automation/automation-dsc-overview) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Configuration Guidance : Use Azure Automation State Configuration to maintain the security configuration of the operating system.

Reference : Configure a VM with Desired State Configuration (/en-us/azure/automation/quickstarts/dsc-configuration)

##### Azure Policy Guest Configuration Agent

Description : Azure Policy guest configuration agent can be installed or deployed as an extension to compute resources. Learn more (/en-us/azure/governance/policy/concepts/guest-configuration) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Feature notes : Azure Policy Guest Configuration is now called Azure Automanage Machine Configuration.

Configuration Guidance : Use Microsoft Defender for Cloud and Azure Policy guest configuration agent to regularly assess and remediate configuration deviations on your Azure compute resources, including VMs, containers, and others.

Reference : Understand the machine configuration feature of Azure Automanage (/en-us/azure/governance/machine-configuration/overview#deploy-requirements-for-azure-virtual-machines)

##### Custom VM Images

Description : Service supports using user-supplied VM images or pre-built images from the marketplace with certain baseline configurations pre-applied. Learn more (/en-us/security/benchmark/azure/security-controls-v3-posture-vulnerability-management#pv-3-define-and-establish-secure-configurations-for-compute-resources) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Configuration Guidance : Use a pre-configured hardened image from a trusted supplier such as Microsoft or build a desired secure configuration baseline into the VM image template

Reference : Tutorial: Create Windows VM images with Azure PowerShell (/en-us/azure/virtual-machines/windows/tutorial-custom-images)

### PV-4: Audit and enforce secure configurations for compute resources

#### Features

##### Trusted Launch Virtual Machine

Description : Trusted Launch protects against advanced and persistent attack techniques by combining infrastructure technologies like secure boot, vTPM, and integrity monitoring. Each technology provides another layer of defense against sophisticated threats. Trusted launch allows the secure deployment of virtual machines with verified boot loaders, OS kernels, and drivers, and securely protects keys, certificates, and secrets in the virtual machines. Trusted launch also provides insights and confidents of the entire boot chain's integrity and ensures workloads are trusted and verifiable. Trusted launch is integrated with Microsoft Defender for Cloud to ensure VMs are properly configured, by remotely attesting VM is booted in a healthy way. Learn more (/en-us/azure/virtual-machines/trusted-launch) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Feature note : Trusted launch is available for generation 2 VMs. Trusted launch requires the creation of new virtual machines. You can't enable trusted launch on existing virtual machines that were initially created without it.

Configuration Guidance : Trusted launch may be enabled during the deployment of the VM. Enable all three - Secure Boot, vTPM, and integrity boot monitoring to ensure the best security posture for the virtual machine. Please note that there are a few prerequisites including onboarding your subscription to Microsoft Defender for Cloud, assigning certain Azure Policy initiatives, and configuring firewall policies.

Reference : Deploy a VM with trusted launch enabled (/en-us/azure/virtual-machines/trusted-launch-portal)

### PV-5: Perform vulnerability assessments

#### Features

##### Vulnerability Assessment using Microsoft Defender

Description : Service can be scanned for vulnerability scan using Microsoft Defender for Cloud or other Microsoft Defender services embedded vulnerability assessment capability (including Microsoft Defender for server, container registry, App Service, SQL, and DNS). Learn more (/en-us/azure/defender-for-cloud/deploy-vulnerability-assessment-tvm) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Configuration Guidance : Follow recommendations from Microsoft Defender for Cloud for performing vulnerability assessments on your Azure virtual machines.

Reference : Plan your Defender for Servers deployment (/en-us/azure/defender-for-cloud/plan-defender-for-servers)

#### Microsoft Defender for Cloud monitoring

Azure Policy built-in definitions - Microsoft.ClassicCompute :

Name
(Azure portal) Description Effect(s) Version
(GitHub)

A vulnerability assessment solution should be enabled on your virtual machines (https://portal.azure.com/#blade/Microsoft_Azure_Policy/PolicyDetailBlade/definitionId/%2Fproviders%2FMicrosoft.Authorization%2FpolicyDefinitions%2F501541f7-f7e7-4cd6-868c-4190fdad3ac9) Audits virtual machines to detect whether they are running a supported vulnerability assessment solution. A core component of every cyber risk and security program is the identification and analysis of vulnerabilities. Azure Security Center's standard pricing tier includes vulnerability scanning for your virtual machines at no extra cost. Additionally, Security Center can automatically deploy this tool for you. AuditIfNotExists, Disabled 3.0.0 (https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Security%20Center/ASC_ServerVulnerabilityAssessment_Audit.json)

Azure Policy built-in definitions - Microsoft.Compute :

Name
(Azure portal) Description Effect(s) Version
(GitHub)

A vulnerability assessment solution should be enabled on your virtual machines (https://portal.azure.com/#blade/Microsoft_Azure_Policy/PolicyDetailBlade/definitionId/%2Fproviders%2FMicrosoft.Authorization%2FpolicyDefinitions%2F501541f7-f7e7-4cd6-868c-4190fdad3ac9) Audits virtual machines to detect whether they are running a supported vulnerability assessment solution. A core component of every cyber risk and security program is the identification and analysis of vulnerabilities. Azure Security Center's standard pricing tier includes vulnerability scanning for your virtual machines at no extra cost. Additionally, Security Center can automatically deploy this tool for you. AuditIfNotExists, Disabled 3.0.0 (https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Security%20Center/ASC_ServerVulnerabilityAssessment_Audit.json)

### PV-6: Rapidly and automatically remediate vulnerabilities

#### Features

##### Azure Update Manager

Description : Service can use Azure Update Manager to deploy patches and updates automatically. Learn more (/en-us/azure/update-manager/overview) .

Supported Enabled By Default Configuration Responsibility

True True Customer

Configuration Guidance : Use Azure Update Manager to ensure that the most recent security updates are installed on your Windows VMs. For Windows VMs, ensure Windows Update has been enabled and set to update automatically.

Reference : Manage updates and patches for your VMs (/en-us/azure/update-manager/quickstart-on-demand)

##### Azure Guest Patching Service

Description : Service can use Azure Guest Patching to deploy patches and updates automatically. Learn more (/en-us/azure/virtual-machines/automatic-vm-guest-patching) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Configuration Guidance : Services can leverage the different update mechanisms such as Auto OS Image Upgrades (/en-us/azure/virtual-machine-scale-sets/virtual-machine-scale-sets-automatic-upgrade#supported-os-images) and Auto Guest Patching (/en-us/azure/virtual-machines/automatic-vm-guest-patching) . The capabilities are recommended to apply the latest security and critical updates to your Virtual Machine's Guest OS by following the Safe Deployment Principles.

Auto Guest Patching allows you to automatically assess and update your Azure virtual machines to maintain security compliance with Critical and Security updates released each month. Updates are applied during off-peak hours, including VMs within an availability set. This capability is available for VMSS Flexible Orchestration, with future support on the roadmap for Uniform Orchestration.

If you run a stateless workload, Auto OS Image Upgrades are ideal to apply the latest update for your VMSS Uniform. With rollback capability, these updates are compatible with Marketplace or Custom images. Future rolling upgrade support on the roadmap for Flexible Orchestration.

Reference : Automatic VM Guest Patching for Azure VMs (/en-us/azure/virtual-machines/automatic-vm-guest-patching)

#### Microsoft Defender for Cloud monitoring

Azure Policy built-in definitions - Microsoft.ClassicCompute :

Name
(Azure portal) Description Effect(s) Version
(GitHub)

System updates should be installed on your machines (https://portal.azure.com/#blade/Microsoft_Azure_Policy/PolicyDetailBlade/definitionId/%2Fproviders%2FMicrosoft.Authorization%2FpolicyDefinitions%2F86b3d65f-7626-441e-b690-81a8b71cff60) Missing security system updates on your servers will be monitored by Azure Security Center as recommendations AuditIfNotExists, Disabled 4.0.0 (https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Security%20Center/ASC_MissingSystemUpdates_Audit.json)

Azure Policy built-in definitions - Microsoft.Compute :

Name
(Azure portal) Description Effect(s) Version
(GitHub)

[Preview]: System updates should be installed on your machines (powered by Update Center) (https://portal.azure.com/#blade/Microsoft_Azure_Policy/PolicyDetailBlade/definitionId/%2Fproviders%2FMicrosoft.Authorization%2FpolicyDefinitions%2Ff85bf3e0-d513-442e-89c3-1784ad63382b) Your machines are missing system, security, and critical updates. Software updates often include critical patches to security holes. Such holes are frequently exploited in malware attacks so it's vital to keep your software updated. To install all outstanding patches and secure your machines, follow the remediation steps. AuditIfNotExists, Disabled 1.0.0-preview (https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Security%20Center/ASC_MissingSystemUpdatesV2_Audit.json)

## Endpoint security

For more information, see the Microsoft cloud security benchmark: Endpoint security (../mcsb-endpoint-security) .

### ES-1: Use Endpoint Detection and Response (EDR)

#### Features

##### EDR Solution

Description : Endpoint Detection and Response (EDR) feature such as Azure Defender for servers can be deployed into the endpoint. Learn more (/en-us/microsoft-365/security/defender-endpoint/) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Configuration Guidance : Azure Defender for servers (with Microsoft Defender for Endpoint integrated) provides EDR capability to prevent, detect, investigate, and respond to advanced threats. Use Microsoft Defender for Cloud to deploy Azure Defender for servers for your endpoint and integrate the alerts to your SIEM solution such as Azure Sentinel.

Reference : Plan your Defender for Servers deployment (/en-us/azure/defender-for-cloud/plan-defender-for-servers#integrated-license-for-microsoft-defender-for-endpoint)

### ES-2: Use modern anti-malware software

#### Features

##### Anti-Malware Solution

Description : Anti-malware feature such as Microsoft Defender Antivirus, Microsoft Defender for Endpoint can be deployed on the endpoint. Learn more (/en-us/azure/security-center/security-center-services?tabs=features-windows#supported-endpoint-protection-solutions-) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Configuration Guidance : For Windows Server 2016 and above, Microsoft Defender for Antivirus is installed by default. For Windows Server 2012 R2 and above, customers can install SCEP (System Center Endpoint Protection). Alternatively, customers also have the choice of installing third-party anti-malware products.

Reference : Defender for Endpoint onboarding Windows Server (/en-us/microsoft-365/security/defender-endpoint/onboard-windows-server)

#### Microsoft Defender for Cloud monitoring

Azure Policy built-in definitions - Microsoft.ClassicCompute :

Name
(Azure portal) Description Effect(s) Version
(GitHub)

Endpoint protection health issues should be resolved on your machines (https://portal.azure.com/#blade/Microsoft_Azure_Policy/PolicyDetailBlade/definitionId/%2Fproviders%2FMicrosoft.Authorization%2FpolicyDefinitions%2F8e42c1f2-a2ab-49bc-994a-12bcd0dc4ac2) Resolve endpoint protection health issues on your virtual machines to protect them from latest threats and vulnerabilities. Azure Security Center supported endpoint protection solutions are documented here - https://docs.microsoft.com/azure/security-center/security-center-services?tabs=features-windows#supported-endpoint-protection-solutions (/en-us/azure/security-center/security-center-services#supported-endpoint-protection-solutions) . Endpoint protection assessment is documented here - https://docs.microsoft.com/azure/security-center/security-center-endpoint-protection (/en-us/azure/security-center/security-center-endpoint-protection) . AuditIfNotExists, Disabled 1.0.0 (https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Security%20Center/ASC_EndpointProtectionHealthIssues_Audit.json)

Azure Policy built-in definitions - Microsoft.Compute :

Name
(Azure portal) Description Effect(s) Version
(GitHub)

Endpoint protection health issues should be resolved on your machines (https://portal.azure.com/#blade/Microsoft_Azure_Policy/PolicyDetailBlade/definitionId/%2Fproviders%2FMicrosoft.Authorization%2FpolicyDefinitions%2F8e42c1f2-a2ab-49bc-994a-12bcd0dc4ac2) Resolve endpoint protection health issues on your virtual machines to protect them from latest threats and vulnerabilities. Azure Security Center supported endpoint protection solutions are documented here - https://docs.microsoft.com/azure/security-center/security-center-services?tabs=features-windows#supported-endpoint-protection-solutions (/en-us/azure/security-center/security-center-services#supported-endpoint-protection-solutions) . Endpoint protection assessment is documented here - https://docs.microsoft.com/azure/security-center/security-center-endpoint-protection (/en-us/azure/security-center/security-center-endpoint-protection) . AuditIfNotExists, Disabled 1.0.0 (https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Security%20Center/ASC_EndpointProtectionHealthIssues_Audit.json)

### ES-3: Ensure anti-malware software and signatures are updated

#### Features

##### Anti-Malware Solution Health Monitoring

Description : Anti-malware solution provides health status monitoring for platform, engine, and automatic signature updates. Learn more (/en-us/microsoft-365/security/defender-endpoint/manage-updates-baselines-microsoft-defender-antivirus) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Feature notes : Security intelligence and product updates apply to Defender for Endpoint which can be installed on the Windows VMs.

Configuration Guidance : Configure your anti-malware solution to ensure the platform, engine and signatures are updated rapidly and consistently and their status can be monitored.

#### Microsoft Defender for Cloud monitoring

Azure Policy built-in definitions - Microsoft.ClassicCompute :

Name
(Azure portal) Description Effect(s) Version
(GitHub)

Endpoint protection health issues should be resolved on your machines (https://portal.azure.com/#blade/Microsoft_Azure_Policy/PolicyDetailBlade/definitionId/%2Fproviders%2FMicrosoft.Authorization%2FpolicyDefinitions%2F8e42c1f2-a2ab-49bc-994a-12bcd0dc4ac2) Resolve endpoint protection health issues on your virtual machines to protect them from latest threats and vulnerabilities. Azure Security Center supported endpoint protection solutions are documented here - https://docs.microsoft.com/azure/security-center/security-center-services?tabs=features-windows#supported-endpoint-protection-solutions (/en-us/azure/security-center/security-center-services#supported-endpoint-protection-solutions) . Endpoint protection assessment is documented here - https://docs.microsoft.com/azure/security-center/security-center-endpoint-protection (/en-us/azure/security-center/security-center-endpoint-protection) . AuditIfNotExists, Disabled 1.0.0 (https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Security%20Center/ASC_EndpointProtectionHealthIssues_Audit.json)

Azure Policy built-in definitions - Microsoft.Compute :

Name
(Azure portal) Description Effect(s) Version
(GitHub)

Endpoint protection health issues should be resolved on your machines (https://portal.azure.com/#blade/Microsoft_Azure_Policy/PolicyDetailBlade/definitionId/%2Fproviders%2FMicrosoft.Authorization%2FpolicyDefinitions%2F8e42c1f2-a2ab-49bc-994a-12bcd0dc4ac2) Resolve endpoint protection health issues on your virtual machines to protect them from latest threats and vulnerabilities. Azure Security Center supported endpoint protection solutions are documented here - https://docs.microsoft.com/azure/security-center/security-center-services?tabs=features-windows#supported-endpoint-protection-solutions (/en-us/azure/security-center/security-center-services#supported-endpoint-protection-solutions) . Endpoint protection assessment is documented here - https://docs.microsoft.com/azure/security-center/security-center-endpoint-protection (/en-us/azure/security-center/security-center-endpoint-protection) . AuditIfNotExists, Disabled 1.0.0 (https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Security%20Center/ASC_EndpointProtectionHealthIssues_Audit.json)

## Backup and recovery

For more information, see the Microsoft cloud security benchmark: Backup and recovery (../mcsb-backup-recovery) .

### BR-1: Ensure regular automated backups

#### Features

##### Azure Backup

Description : The service can be backed up by the Azure Backup service. Learn more (/en-us/azure/backup/backup-overview) .

Supported Enabled By Default Configuration Responsibility

True False Customer

Configuration Guidance : Enable Azure Backup and configure the backup source (such as Azure Virtual Machines, SQL Server, HANA databases, or File Shares) on a desired frequency and with a desired retention period. For Azure Virtual Machines, you can use Azure Policy to enable automatic backups.

Reference : Backup and restore options for virtual machines in Azure (/en-us/azure/virtual-machines/backup-recovery)

#### Microsoft Defender for Cloud monitoring

Azure Policy built-in definitions - Microsoft.Compute :

Name
(Azure portal) Description Effect(s) Version
(GitHub)

Azure Backup should be enabled for Virtual Machines (https://portal.azure.com/#blade/Microsoft_Azure_Policy/PolicyDetailBlade/definitionId/%2Fproviders%2FMicrosoft.Authorization%2FpolicyDefinitions%2F013e242c-8828-4970-87b3-ab247555486d) Ensure protection of your Azure Virtual Machines by enabling Azure Backup. Azure Backup is a secure and cost effective data protection solution for Azure. AuditIfNotExists, Disabled 3.0.0 (https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Backup/VirtualMachines_EnableAzureBackup_Audit.json)

## Next steps

- See the Microsoft cloud security benchmark overview (../overview)
- Learn more about Azure security baselines (../security-baselines-overview)

## Feedback

Was this page helpful?

No

Need help with this topic?

Want to try using Ask Learn to clarify or guide you through this topic?

## Additional resources

- Last updated on 2025-02-25
