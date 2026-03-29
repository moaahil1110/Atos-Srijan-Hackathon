# GCP Compute Engine

Source pages:
- Compute Engine overview: https://cloud.google.com/compute/docs/overview
- Access control overview: https://cloud.google.com/compute/docs/access

## Compute Engine overview

Source: https://cloud.google.com/compute/docs/overview

# Compute Engine overview

Compute Engine is an infrastructure as a service (IaaS) product that offers self-managed virtual machine (VM) instances and bare metal instances. Compute Engine offers VMs with a KVM hypervisor, operating systems for both Linux and Windows, and durable storage options. You can configure and control Compute Engine resources using the Google Cloud console, the Google Cloud CLI, or using a REST-based API. You can also use a variety of programming languages available with Google's Cloud Client Libraries (/apis/docs/cloud-client-libraries) .

Here are some of the benefits of using Compute Engine:

- Extensibility: Compute Engine integrates with Google Cloud technologies such as Cloud Storage, Google Kubernetes Engine, and BigQuery, to extend beyond the basic computational capability to create more complex and sophisticated applications.

Scalability: Scale the number of compute resources as needed without having to manage your own infrastructure. This is useful for businesses that experience sudden increases in traffic, because you can quickly add more instances to handle the increase and remove the instances after they are no longer needed.

Reliability: The minimum uptime SLO for Compute Engine is 99.9%. The uptime SLO varies depending on the regions and Network Service Tiers that you choose and the deployment configurations. For more information, see Compute Engine Service Level Agreement (SLA) (https://cloud.google.com/compute/sla) .

Cost-effectiveness: Compute Engine offers a variety of pricing options to fit your budget. Also, you only pay for the resources that you use, and there are no up-front costs.

## What Compute Engine provides

Compute Engine provides flexibility so that you can run a wide-range of applications and workloads that support your needs. From batch processing to webserving or high performance computing you can configure Compute Engine to meet your needs.

### Location selection

Google offers worldwide regions for you to deploy Compute Engine resources. You can choose a region that best fits the requirements of your workload:

- Region-specific restrictions
- User latency by region
- Latency requirements of your application
- Amount of control over latency
- Balance between low latency and simplicity

For more information about regions and zones, see About regions and zones (/compute/docs/regions-zones) .

### Compute Engine machine types

Compute Engine provides a comprehensive set of machine families, each containing machine types to choose from when you create a compute instance. Each machine family is comprised of machine series and predefined machine types within each series.

Compute Engine offers general-purpose, compute-optimized, storage-optimized, memory-optimized, and accelerator-optimized machine families. If a preconfigured, general-purpose machine type doesn't meet your needs, then you can create a custom machine type with customized CPU and memory resources for some of the machine series.

For more information, see the Machine families resource guide (/compute/docs/machine-resource) .

### Operating systems

Compute Engine provides many preconfigured public operating system images for both Linux and Windows.
Most public images are provided for no additional cost, but there are some premium images (/compute/disks-image-pricing#premiumimages) for which you are billed. You are not billed for importing custom images, but you will incur an image storage charge (/compute/disks-image-pricing#imagestorage) while you keep the custom image in your project.

### Storage options

You can choose from several block storage options, including Google Cloud Hyperdisk, Local SSD, and Persistent Disk.

Local SSD: Physical drives that offer the best performance, but are not durable. If you stop the instance, the data on the Local SSD disks that are attached to the instance is lost. Local SSD disks are attached directly to the same server as the compute instance.

Hyperdisk: The fastest durable storage for Compute Engine. Data on Hyperdisk volumes is preserved even if you stop the instance. Hyperdisk volumes offer configurable performance and can be resized dynamically. You can also reduce costs and disk management complexity by purchasing capacity and performance in advance with Hyperdisk Storage Pools.

Persistent Disk: If you need durable storage for a machine series that doesn't support Hyperdisk, then use Persistent Disk. Persistent Disk provides fast durable block storage that is preserved even if you stop the instance.

Each option has unique pricing and performance. For more information about disks in Compute Engine, see Choose a disk type (/compute/docs/disks) .
For cost comparisons, see Disk pricing (/compute/disks-image-pricing#disk) .

## What's next

- See the CPU platforms (/compute/docs/cpu-platforms) and GPUs (/compute/docs/gpus) that are available for your use.
- Read an overview of networking capabilities (/compute/docs/networking/network-overview) .
- Learn about the various deployment strategies (/compute/docs/choose-compute-deployment-option) .

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License (https://creativecommons.org/licenses/by/4.0/) , and code samples are licensed under the Apache 2.0 License (https://www.apache.org/licenses/LICENSE-2.0) . For details, see the Google Developers Site Policies (https://developers.google.com/site-policies) . Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2026-03-26 UTC.


## Access control overview

Source: https://cloud.google.com/compute/docs/access

# Access control overview

By default, all Google Cloud projects come with a single user: the original project creator. No other users have access to the project, and therefore, access to Compute Engine resources, until a user is added as a project member or is bound to a specific resource. This page describes the ways you can add new users to your project and how to set access control for your Compute Engine resources using Identity and Access Management (IAM).

For information about providing access to applications running on your Compute Engine instances, see How authorization is determined (/compute/docs/access/service-accounts#authz-how-determined) .

## Access control options for users

To give users the ability to create and manage your Compute Engine resources, you can add users as team members to your project or to specific resources and grant them permissions using IAM roles .

A team member can be an individual user with a valid Google Account or user account from an external identity provider (/iam/docs/workforce-identity-federation) , a Google Group, a group of identities from a workforce identity pool, a service account, or a Google Workspace domain. When you add a team member to a project or to a resource, you specify which roles to grant them. IAM provides three types of roles: predefined roles (#predefined-compute-engine-roles) , basic roles (#basic-iam-roles) , and custom roles (/iam/docs/understanding-custom-roles) .

Resources inherit the policies of their parent resources in the Google Cloud resource hierarchy (/iam/docs/resource-hierarchy-access-control) . The effective policy for a resource is the union of the policy set at that resource and the policy inherited from its parent.

### Predefined Compute Engine roles

Predefined roles grant a set of related permissions. Compute Engine offers the following predefined roles:

Role title Capabilities Target user

Compute Engine image user

Permission to list and use images from another project. Grant a member this role together with another role so the member can use images from another project to create a new resource. For example, grant this role and the Instance Admin role so that a member can use images from another project to create VM instances and persistent disks.

If you are creating managed instance groups (/compute/docs/instance-groups/creating-groups-of-managed-instances) or if you are using Deployment Manager (/deployment-manager) to create VM instances, you might need to grant the project's Google APIs service account this role before you can use images from other projects.

- Service accounts
- Systems administrators
- Developers

Compute Engine instance admin (v1)

Full control of Compute Engine instances, instance groups, disks, snapshots, and images. Read-only access to all Compute Engine networking resources.

If the member is managing VM instances that are configured to run as a service account, you must also grant the`roles/iam.serviceAccountUser`role so that they can assign service accounts to VM instances.

- Systems administrators
- Developers

Compute Engine admin role

Full control of all Compute Engine resources. If the user is managing VM instances that are configured to run as a service account, you must also grant the`roles/iam.serviceAccountUser`role.

- Systems administrators
- Developers

Compute Engine network admin

Permissions to create, modify, and delete networking resources, except for firewall rules and SSL certificates. The network admin role allows read-only access to firewall rules, SSL certificates, and instances (to view their ephemeral IP addresses). The network admin role does not allow a member to create, start, stop, or delete instances.
Network administrators

Compute Engine security admin

Permissions to create, modify, and delete firewall rules and SSL certificates.
Security administrators

Compute Engine load balancer admin beta

Permissions to create, modify, and delete load balancers and associated resources.
Load balancer administrators

Compute Engine service account user

Permission to create instances that use service accounts, and permission to attach a disk and set metadata on an instance already configured to run as a service account.

You should not grant this role by itself because it provides no permissions to the Compute Engine API. You should grant a member this role and another role, such as the instance admin role.

- Systems administrators
- Developers

Compute Engine viewer role

Read-only access to get and list Compute Engine resources, without being able to read the data stored on them. For example, an account with this role could inventory all of the disks in a project, but it could not read any of the data on those disks. System administrators

Compute Engine network user

Permissions to use a shared VPC (/compute/docs/shared-vpc) network. Specifically, grant this role to service owners who need to use resources in the host project. Once granted, service owners can use subnetworks and networks that belong to the host project. For example, a network user can create a VM instance that belongs to a shared VPC host network, but they cannot delete or create new networks in the host project.

- Systems administrators
- Developers

Compute Engine network viewer

Read-only access to all networking resources. For example, if you have software that inspects your network configuration, you could grant that software's service account the network viewer role.

- Network administrators
- Systems administrators
- Developers
- Service accounts

Compute Engine storage admin beta

Permissions to create, modify, and delete disks, images, and snapshots.

For example, if your company has someone who manages images and you do not want them to have the editor role on the project, then grant their account this role.

- Systems administrators
- Developers

Compute Engine shared VPC admin

Permissions to administer shared VPC host projects, specifically enabling the host projects and associating service projects to the host project's network. This role can only be granted at the organization level.
Project creators

To see a list of API methods that a specific role grants permission to, review the Compute Engine IAM roles (/compute/docs/access/iam) documentation.

### Predefined roles matrix

The following table provides a complete comparison of the capabilities of each Compute Engine role.

Capability Instance admin (v1) Image user Network user Network viewer Network admin Security admin Storage admin Shared VPC admin Compute admin Compute viewer Load balancer admin

Create or delete VM instances *

SSH into VM instances * *

List or get VM instances

Create or delete images, disks, snapshots

List or get images

Create or delete instance groups *

List or get instance groups

Create and manage load balancers

Create and manage VPNs

View network/subnetwork resources

View firewall rules

Create and manage firewalls and SSL certificates for firewalls,
for SSL certificates

Create and manage shared VPC host projects

Use networks and subnetworks in a shared VPC host project

Create and manage networks and subnetworks

*If the VM instance can run as a service account, grant the service account user role as well.

To see a list of API methods that a specific role grants permission to, review the Compute Engine IAM roles (/compute/docs/access/iam) documentation.

### Basic IAM roles

Basic IAM roles map directly to the legacy project owner, editor, and viewer roles. Generally, you should use predefined roles whenever possible; however, in some cases, where IAM is not yet supported, you might need to use a basic role to grant the correct permissions.

Role title Permissions

`Owner`All viewer and editor privileges, plus the ability to change billing settings, manage access control, and delete a project.

`Editor`All viewer privileges, plus the ability to create, modify, and delete resources.

`Viewer`Read-only permissions to all resources; no permission to change resources.

To learn more about basic roles, read documentation for basic roles (/iam/docs/roles-overview#basic) .

If predefined or basic roles do not meet you needs, you can create custom roles (/iam/docs/creating-custom-roles) .

## IAM policies for Compute Engine resources

You can grant access to Compute Engine resources (/compute/docs/access/managing-access-to-resources) such as VM instances, images, and disks, by attaching IAM policies directly to those resources. An IAM policy lets you manage IAM roles (/compute/docs/access/iam) on those resources instead of, or in addition to, managing roles at the project level. This gives you flexibility to apply the principle of least privilege, which is to grant access only to the specific resources that collaborators need to do their work.

With IAM policies for Compute Engine resources, organizations can:

- Grant users access to a specific subset of resources . Suppose Alice should manage a subset of instances in a project. With instance-level IAM policies, you grant her the`compute.instanceAdmin.v1` (/compute/docs/access/iam#instance_admin_role) role on only those instances. If you granted Alice the same role on the project, then she would have permission to modify all instances in the project.
- Allow administrators to grant access . Administrators can grant other people access to instances, disks, and images without needing to be powerful project owners. Suppose Bob is a developer who has been granted the`compute.storageAdmin` (/compute/docs/access/iam#storage_admin_role) role on a specific image. He can share that image with his teammates by granting them the`compute.imageUser` (/compute/docs/access/iam#image_user_role) role on the image. Without IAM policies for Compute Engine resources, Bob can't share that image with his teammates unless he becomes a project owner because he'd need to modify the project's IAM policy.

Resources also inherit the policies of their parent resources. If you set a policy at the project level, it's inherited by all its child resources. The effective policy for a resource is the union of the policy set at that resource and the policy inherited from higher up in the hierarchy. For more information, read about the IAM policy hierarchy (/iam/docs/overview#policy_hierarchy) .

## Organization policies

If you are a Google Workspace member, your project might be part of an Organization resource (/resource-manager/docs/cloud-platform-resource-hierarchy#organizations) . An Organization resource is the supernode in the Google Cloud resource hierarchy (/resource-manager/docs/cloud-platform-resource-hierarchy#gcp_resource_hierarchy_in_detail) that is closely associated with a Google Workspace account. After an Organization resource is created for a Google Workspace domain, all Google Cloud projects created by members of the domain belong to the Organization resource.

An organization can implement organization policies (/resource-manager/docs/organization-policy/overview) , which are policies that restrict allowed configurations across your entire Google Cloud resource hierarchy. For Compute Engine, you can implement the following policies:

- Disable interactive access to the serial console (/compute/docs/instances/interacting-with-serial-console#disable_access) .
- Disable external IP addresses for VM instances (/compute/docs/ip-addresses/configure-static-external-ip-address#disableexternalip) .
- Restrict which image projects are available to your project members (/compute/docs/images/restricting-image-access)

To set Organization policies (/resource-manager/docs/organization-policy/overview) , you must have been granted the`orgpolicy.policyAdmin`role on the organization. You can also set project-specific overrides in case you have exceptions to the policy.

To learn more about Organizations, read the Organizations (/resource-manager/docs/cloud-platform-resource-hierarchy#organizations) documentation.

To learn more about Organization policies, read the Organization policy (/resource-manager/docs/organization-policy/overview) documentation.

## Granting users SSH access to VM instances

To give a user the ability to connect to a VM instance using SSH without granting them the ability to manage Compute Engine resources, add the user's public key (/compute/docs/instances/adding-removing-ssh-keys) to the project, or add a user's public key to a specific instance. Using this method, you can avoid adding a user as a project member, while still granting them access to specific instances.

To learn more about SSH and managing SSH keys, read the SSH keys overview (/compute/docs/instances/ssh-keys) .

Note that if you grant the`roles/compute.instanceAdmin.v1`role to a project member, they can automatically connect to instances using SSH, as long as the instance is not set up to run as a service account. If the instance is set up to run as a service account, you must also grant the`roles/iam.serviceAccountUser`role before the member can connect to the instance.

If you add a member as a project owner or editor, they also automatically have SSH access to VM instances in the project.

## Access control for apps running on VM instances

If you run app code on instances and the app needs to authenticate to other Google Cloud APIs, you can create service accounts and give these service accounts specific IAM roles to authenticate to other Google Cloud APIs on your behalf. A service account is a special account that has no user credentials and is ideal for server-to-server interactions.

To learn more about service accounts, read the Service accounts (/compute/docs/access/service-accounts) documentation.

## Managed workload identities for Compute Engine workloads

You can set up automatic provisioning and lifecycle management of X.509 certificates from Certificate Authority Service (CA Service) using managed workload identities. Managed workload identity certificates are issued from CA Service, which is a highly-available, scalable Google Cloud service that helps you to simplify and automate the deployment, management, and security of CA services while staying in control of your private keys.

With managed workload identities, you can benefit from per-VM mTLS (https://en.wikipedia.org/wiki/Mutual_authentication) , managed by Compute Engine. Per-VM mTLS uses X.509 certificates that are issued when you create a VM. These mTLS certificates are automatically rotated, so you don't need to worry about managing the certificates.

Managed workload identities provide a foundation to enable mutually authenticated and encrypted communications between any two Compute Engine VMs. For example, when you use managed workload identities, service A running in one VM communicates with service B running in a different VM over an encrypted channel that is established using mTLS.

For information about configuring managed workload identities, see Authenticate workloads to other workloads over mTLS (/compute/docs/access/authenticate-workloads-over-mtls) .

## What's next?

- Add users as team members (/compute/docs/access/add-remove-change-permissions-for-team-members) .
- Learn more about IAM roles (/compute/docs/access/iam) .
- Learn more about Adding and removing SSH keys (/compute/docs/instances/adding-removing-ssh-keys) .
- Learn more about Service accounts (/compute/docs/access/service-accounts) .

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License (https://creativecommons.org/licenses/by/4.0/) , and code samples are licensed under the Apache 2.0 License (https://www.apache.org/licenses/LICENSE-2.0) . For details, see the Google Developers Site Policies (https://developers.google.com/site-policies) . Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2026-03-26 UTC.
