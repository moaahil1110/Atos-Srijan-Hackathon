# GCP Cloud Storage

Source pages:
- Cloud Storage overview: https://cloud.google.com/storage/docs/concepts
- Overview of access control: https://cloud.google.com/storage/docs/access-control

## Cloud Storage overview

Source: https://cloud.google.com/storage/docs/concepts

# Cloud Storage overview

This page describes Cloud Storage and how it works.

## How Cloud Storage works

Cloud Storage is a scalable and managed storage service offered by Google Cloud that lets you store data as objects in containers called buckets .

All buckets are associated with a project , and you group your projects under an organization . After you create a project, you can create buckets (/storage/docs/creating-buckets) , upload objects (/storage/docs/uploading-objects) to your buckets, and download objects (/storage/docs/downloading-objects) from your buckets. You can also grant permissions to make your data accessible to principals you specify or accessible to everyone on the public internet (/storage/docs/access-control/making-data-public) . Directory capabilities let you utilize Cloud Storage more similarly to a hard drive or Network Attached Storage (NAS): folders let you organize objects in a directory structure, and managed folders let you simplify access control to your objects.

Each project, bucket, object, folder, and managed folder is a resource in Google Cloud, as are things such as Compute Engine instances (/compute/docs/instances) .

## The Google Cloud hierarchy

Here's how the Cloud Storage structure can apply to a real-world case:

Organization (/resource-manager/docs/cloud-platform-resource-hierarchy#organizations) : Your company, called Example Inc., creates a Google Cloud organization called`exampleinc.org`.

Project (/storage/docs/projects) : Example Inc. is building several applications, and each one is associated with a project. Each project has its own set of Cloud Storage APIs, as well as other resources.

Bucket (/storage/docs/buckets) : Each project can contain multiple buckets, which are containers to store your objects. For example, you might create a`photos`bucket for all the image files your app generates and a separate`videos`bucket. Cloud Storage offers different storage classes (/storage/docs/storage-classes) and locations (/storage/docs/locations) for your buckets, letting you choose the durability and availability of your data to suit the needs of your workloads.

Buckets serve as a primary data foundation in the broader Google Cloud ecosystem. You can connect your buckets as storage backends for other Google Cloud services, such as AI Hypercomputer, Vertex AI, and Google Kubernetes Engine.

While buckets are suitable for most data storage use cases, you can set up optional configurations and features on a bucket to make it more suitable for high-performance workloads specifically:

Hierarchical namespace (/storage/docs/hns-overview) : Buckets can have hierarchical namespace enabled, which lets you store your data in a logical file system structure by using folders. Storing your data in folders provides the ability to use directory semantics and atomic folder operations, which are often required to accelerate data-intensive AI/ML and analytics workloads. Buckets with hierarchical namespace enabled offer up to 8 times higher initial queries per second (QPS) limits for reading and writing objects compared to buckets without hierarchical namespace enabled.

Hierarchical namespace can only be enabled at the time of bucket creation (/storage/docs/create-hns-bucket) and can't be enabled on an existing bucket.

Rapid Bucket (/storage/docs/rapid/rapid-bucket) : Rapid Bucket is a high performance capability that lets you store objects in the Rapid storage class by using a zone as a bucket's location. When you locate buckets in zones, you get the ability to colocate your objects with your compute resources, automatic enablement of hierarchical namespace, and new APIs for streaming reads and appendable writes. Rapid Bucket provides substantially improved latency, throughput, and I/Os compared to buckets in other storage classes, making the capability ideal for data-intensive AI/ML and analytics workloads.

To use Rapid Bucket, you create a bucket and define a zone as the bucket's location (/storage/docs/rapid/create-zonal-buckets) . Rapid Bucket can't be used on existing buckets that aren't located in a zone.

Object (/storage/docs/objects) : Buckets contain objects, such as an image called`puppy.png`. An object is an immutable piece of data consisting of a file of any format. Each bucket can contain essentially unlimited individual objects.

Folder (/storage/docs/folders-overview) : Buckets with hierarchical namespace enabled can contain folders. Folders enable a real file system for storing objects, as opposed to a simulated file system. You can atomically rename a folder and all the objects within it in one operation.

Managed folder (/storage/docs/managed-folders) : Each bucket can also contain managed folders, which grant or revoke additional access beyond the IAM permissions set on the bucket. Managed folders don't use a true directory tree structure; rather, a managed folder is a resource overlay used only for permission checking.

## Tools for Cloud Storage

You can interact with Cloud Storage by using the following tools:

Google Cloud console (https://console.cloud.google.com/storage/browser) : The Google Cloud console provides a visual interface for you to manage your data in a browser.

Google Cloud CLI (/sdk/gcloud) : The gcloud CLI lets you interact with Cloud Storage through a terminal using`gcloud storage`commands (/sdk/gcloud/reference/storage) .

Client libraries (/storage/docs/reference/libraries) : The Cloud Storage client libraries allow you to manage your data using one of your preferred languages, including C++, C#, Go, Java, Node.js, PHP, Python, and Ruby.

REST APIs: Manage your data using the JSON (/storage/docs/json_api) or XML (/storage/docs/xml-api/overview) API.

Terraform (https://www.terraform.io/) : Terraform is an infrastructure-as-code (IaC) tool that you can use to provision the infrastructure for Cloud Storage. For more information, see Provision resources with Cloud Storage (/storage/docs/terraform-for-cloud-storage) .

gRPC (/storage/docs/enable-grpc-api) : gRPC lets you interact with Cloud Storage. gRPC is a high performance, open source universal RPC framework developed by Google that you can use to define your services using Protocol Buffers.

Cloud Storage FUSE (/storage/docs/gcs-fuse) : Cloud Storage FUSE lets you mount Cloud Storage buckets to your local file system. This enables your applications to read from a bucket or write to a bucket by using standard file system semantics.

## Securing your data

Once you upload your objects to Cloud Storage, you have fine-grained control over how you secure and share your data. Here are some ways to secure the data you upload to Cloud Storage:

Identity and Access Management (/storage/docs/access-control/iam) : Use IAM to control who has access to the resources in your Google Cloud project. Resources include Cloud Storage buckets and objects, as well as other Google Cloud entities such as Compute Engine instances (/compute/docs/instances) . You can grant principals certain types of access to buckets and objects, such as`update`,`create`, or`delete`.

Data encryption (/storage/docs/encryption) : Cloud Storage uses server-side encryption to encrypt your data by default. You can also use supplemental data encryption options such as customer-managed encryption keys (/storage/docs/encryption/customer-managed-keys) and customer-supplied encryption keys (/storage/docs/encryption/customer-supplied-keys) .

Authentication (/storage/docs/authentication) : Ensure that anyone who accesses your data has proper credentials.

Soft delete (/storage/docs/soft-delete) : Prevent permanent loss of data against accidental or malicious deletion by retaining recently deleted objects and buckets. By default, Cloud Storage enables soft delete for all buckets with a seven day retention period.

Object Versioning (/storage/docs/using-object-versioning) : When a live version of an object is replaced or deleted, it can be retained as a noncurrent version if you enable Object Versioning.

Bucket IP filtering (/storage/docs/ip-filtering-overview) : With bucket IP filtering, you can restrict access to a bucket based on the source IP address of the request and secure your data from unauthorized access from specific IP addresses or Virtual Private Cloud (VPC).

Bucket Lock (/storage/docs/using-bucket-lock) : Govern how long objects in buckets must be retained by specifying a retention policy.

### Resource names

Each resource has a unique name that identifies it, much like a filename. Buckets have a resource name in the form of`projects/_/buckets/BUCKET_NAME`, where`BUCKET_NAME`is the ID of the bucket. Objects have a resource name in the form of`projects/_/buckets/BUCKET_NAME /objects/OBJECT_NAME`, where`OBJECT_NAME`is the ID of the object.

A`# NUMBER`appended to the end of the resource name indicates a specific generation of the object.`#0`is a special identifier for the most recent version of an object.`#0`is useful to add when the name of the object ends in a string that would otherwise be interpreted as a generation number.

## Quickstart guides

To learn the fundamentals of using Cloud Storage, visit the following guides:

- Google Cloud console quickstart (/storage/docs/discover-object-storage-console)
- gcloud quickstart (/storage/docs/discover-object-storage-gcloud)
- Terraform quickstart (/storage/docs/terraform-create-bucket-upload-object)

## Looking for other products?

If Cloud Storage is not the right storage solution for you, see more information about the following storage services:

Google Cloud Managed Lustre (/managed-lustre/docs/overview) : Store your data in a high-performance, fully managed parallel file system that's optimized for AI and HPC workloads.

Google Drive (https://www.google.com/intl/en/drive/) : Store, manage, and share your personal files.

Cloud Storage for Firebase (https://firebase.google.com/docs/storage/) : Manage data for your mobile applications.

Persistent Disk (/compute/docs/disks) : Add block storage to your Compute Engine virtual machine.

Filestore (/filestore/docs/overview) : Add file storage for multiwriter access to your GKE clusters.

Explore more storage services (/products/storage) offered by Google.

## What's next

- Learn the fundamentals of Cloud Storage through the Google Cloud console (/storage/docs/discover-object-storage-console) or Google Cloud CLI (/storage/docs/discover-object-storage-gcloud) .
- Try Google Cloud jump start solutions that use Cloud Storage (/architecture/storage) .
- Get started with client libraries (/storage/docs/reference/libraries) .
- Quickly import online data into Cloud Storage or between Cloud Storage buckets using Storage Transfer Service (/storage-transfer/docs/overview) .

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License (https://creativecommons.org/licenses/by/4.0/) , and code samples are licensed under the Apache 2.0 License (https://www.apache.org/licenses/LICENSE-2.0) . For details, see the Google Developers Site Policies (https://developers.google.com/site-policies) . Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2026-03-26 UTC.


## Overview of access control

Source: https://cloud.google.com/storage/docs/access-control

# Overview of access control

You control who has access to your Cloud Storage buckets and objects and what level of access they have.

## Choose between uniform and fine-grained access

When you create a bucket, you should decide whether you want to apply permissions using uniform or fine-grained access.

Uniform (recommended) : Uniform bucket-level access (/storage/docs/uniform-bucket-level-access) allows you to use Identity and Access Management (IAM) (/storage/docs/access-control/iam) alone to manage permissions. IAM applies permissions to all the objects contained inside the bucket or groups of objects with common name prefixes. IAM also allows you to use features that are not available when working with ACLs, such as managed folders (/storage/docs/managed-folders) , IAM Conditions (/iam/docs/conditions-overview) , domain restricted sharing (/resource-manager/docs/organization-policy/restricting-domains) , and workforce identity federation (/iam/docs/workforce-identity-federation) .

Fine-grained : The fine-grained option enables you to use IAM and Access Control Lists (ACLs) (/storage/docs/access-control/lists) together to manage permissions. ACLs are a legacy access control system for Cloud Storage designed for interoperability with Amazon S3. ACLs also allow you to specify access on a per-object basis.

Because fine-grained access requires you to coordinate between two different access control systems, there is an increased chance of unintentional data exposure, and auditing who has access to resources is more complicated. Particularly if you have objects that contain sensitive data, such as personally identifiable information, we recommend storing that data in a bucket with uniform bucket-level access enabled.

## Using IAM permissions with ACLs

Cloud Storage offers two systems for granting users access your buckets and objects: IAM and Access Control Lists (ACLs). These systems act in parallel - in order for a user to access a Cloud Storage resource, only one of the systems needs to grant that user permission. For example, if your bucket's IAM policy only allows a few users to read object data in the bucket, but one of the objects in the bucket has an ACL that makes it publicly readable, then that specific object is exposed to the public.

In most cases, IAM is the recommended method for controlling access to your resources. IAM controls permissioning throughout Google Cloud and allows you to grant permissions at the bucket and project levels. You should use IAM for any permissions that apply to multiple objects in a bucket to reduce the risks of unintended exposure. To use IAM exclusively, enable uniform bucket-level access to disallow ACLs for all Cloud Storage resources.

ACLs control permissioning only for Cloud Storage resources and have limited permission options, but allow you to grant permissions per individual objects. You most likely want to use ACLs for the following use cases:

- Customize access to individual objects within a bucket.
- Migrate data from Amazon S3.

## Additional access control options

In addition to IAM and ACLs, the following tools are available to help you control access to your resources:

### Signed URLs (query string authentication)

Use signed URLs (/storage/docs/access-control/signed-urls) to give time-limited read or write access to an object through a URL you generate. Anyone with whom you share the URL can access the object for the duration of time you specify, regardless of whether or not they have a user account.

You can use signed URLs in addition to IAM and ACLs. For example, you can use IAM to grant access to a bucket for only a few people, then create a signed URL that allows others to access a specific resource within the bucket.

Learn how to create signed URLs:

- Create signed URLs with the Google Cloud CLI or client libraries (/storage/docs/access-control/signing-urls-with-helpers) .
- Create signed URLs with your own program (/storage/docs/access-control/signing-urls-manually) .

### Signed policy documents

Use signed policy documents (/storage/docs/authentication/signatures#policy-document) to specify what can be uploaded to a bucket. Policy documents allow greater control over size, content type, and other upload characteristics than signed URLs, and can be used by website owners to allow visitors to upload files to Cloud Storage.

You can use signed policy documents in addition to IAM and ACLs. For example, you can use IAM to allow people in your organization to upload any object, then create a signed policy document that allows website visitors to upload only objects that meet specific criteria.

### Firebase Security Rules

Use Firebase Security Rules (https://firebase.google.com/docs/storage/security) to provide granular, attribute-based access control to mobile and web apps using the Firebase SDKs for Cloud Storage (https://firebase.google.com/docs/storage) . For example, you can specify who can upload or download objects, how large an object can be, or when an object can be downloaded.

### Public access prevention

Use public access prevention (/storage/docs/public-access-prevention) to restrict public access to your buckets and objects. When you enable public access prevention, users who gain access through`allUsers`and`allAuthenticatedUsers` (/iam/docs/principals-overview#principal-types) are disallowed access to data.

### Credential Access Boundaries

Use Credential Access Boundaries (/iam/docs/downscoping-short-lived-credentials) to downscope the permissions that are available to an OAuth 2.0 access token. First, you define a Credential Access Boundary that specifies which buckets the token can access, as well as an upper bound on the permissions that are available on that bucket. You can then create an OAuth 2.0 access token (https://developers.google.com/identity/protocols/OAuth2) and exchange it for a new access token that respects the Credential Access Boundary.

### Bucket IP filtering

Use Bucket IP filtering (/storage/docs/ip-filtering-overview) to restrict access on your bucket based on the source IP address of the request. Bucket IP filtering adds a layer of security by preventing unauthorized networks from accessing your bucket and its data. You can configure a list of permitted IP address ranges, including public IP addresses, ranges of public IP addresses and IP addresses within your Virtual Private Cloud. Any requests originating from an IP address that's not on your list are blocked. As a result, only authorized users can access your bucket.

## Best practices for IAM and ACLs

IAM policies and ACLs require active management to be effective. Before you make a bucket, object, or managed folder accessible to other users, be sure you know who you want to share the resource with and what roles you want each of those people to have. Over time, changes in project management, usage patterns, and organizational ownership might require you to modify IAM or ACL settings on buckets and projects, especially if you manage Cloud Storage in a large organization or for a large group of users. As you evaluate and plan your access control settings, keep the following best practices in mind:

Use the principle of least privilege when granting access to your buckets, objects, or managed folders.

The principle of least privilege (https://en.wikipedia.org/wiki/Principle_of_least_privilege) is a security guideline for granting access to your resources. When you grant access based on the principle of least privilege, you grant the minimum permission that's necessary for a user to accomplish their assigned task. For example, if you want to share files with someone, you should grant them the Storage Object Viewer IAM role or the`READER`ACLs permission, and not the Storage Admin IAM role or the`OWNER`ACLs permission.

Avoid granting IAM roles with`setIamPolicy`permission or granting the ACL`OWNER`permission to people you don't know.

Granting the`setIamPolicy`IAM permission or the`OWNER`ACLs permission allows a user to change permissions and take control of data. You should use roles with these permissions only when you want to delegate administrative control over objects, buckets, and managed folders.

Be careful how you grant permissions for anonymous users.

The`allUsers`and`allAuthenticatedUsers`principal types should only be used when it is acceptable for anyone on the internet to read and analyze your data. Although these scopes are useful for some applications and scenarios, it usually isn't a good idea to grant all users certain permissions, such as the IAM permissions`setIamPolicy`,`update`,`create`, or`delete`, or the ACLs`OWNER`permission.

Be sure you delegate administrative control of your buckets.

You should be sure that your resources can still be managed by other team members in case an individual with administrative access leaves the group.

To prevent resources from becoming inaccessible, you can do any of the following:

Grant the Storage Admin IAM role for your project to a group instead of an individual.

Grant the Storage Admin IAM role for your project to at least two individuals.

Grant the`OWNER`ACLs permission for your bucket to at least two individuals.

Be aware of Cloud Storage's interoperable behavior.

When using the XML API for interoperable access with other storage services, such as Amazon S3, the signature identifier determines the ACL syntax. For example, if the tool or library you are using makes a request to Cloud Storage to retrieve ACLs and the request uses another storage provider's signature identifier, then Cloud Storage returns an XML document that uses the corresponding storage provider's ACL syntax. If the tool or library you are using makes a request to Cloud Storage to apply ACLs and the request uses another storage provider's signature identifier, then Cloud Storage expects to receive an XML document that uses the corresponding storage provider's ACL syntax.

For more information about using the XML API for interoperability with Amazon S3, see Simple migration from Amazon S3 to Cloud Storage (/storage/docs/aws-simple-migration) .

## What's next

- Learn how to use IAM permissions (/storage/docs/access-control/using-iam-permissions) .
- Refer to IAM permissions and roles specific to Cloud Storage (/storage/docs/access-control/iam-reference) .
- View examples of sharing and collaboration (/storage/docs/collaboration) scenarios that involve setting bucket and object ACLs.
- Learn how to make your data accessible to everyone on the public internet (/storage/docs/access-control/making-data-public) .
- Learn more about when to use a signed URL (/storage/docs/access-control/signed-urls#should-you-use) .

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License (https://creativecommons.org/licenses/by/4.0/) , and code samples are licensed under the Apache 2.0 License (https://www.apache.org/licenses/LICENSE-2.0) . For details, see the Google Developers Site Policies (https://developers.google.com/site-policies) . Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2026-03-26 UTC.
