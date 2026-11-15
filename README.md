# Sentinel API — Secure API & DevSecOps Pipeline

A security-focused REST API built with **FastAPI**, **SQLite**, and **Docker**, supported by an automated CI/CD pipeline that performs code-quality checks, automated testing, dependency auditing, static security analysis, and container vulnerability scanning before publishing images to **GitHub Container Registry (GHCR)**.

The project follows a practical DevSecOps workflow: security is integrated throughout the software delivery lifecycle rather than treated as a final deployment step.

The application is packaged into a hardened Docker image and deployed to an **Azure Linux virtual machine**, with persistent database storage and restricted network exposure.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Project Objectives](#project-objectives)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Application Features](#application-features)
- [API Reference](#api-reference)
- [Security Implementation](#security-implementation)
- [Project Development Stages](#project-development-stages)
  - [Stage 1 — Application Foundation](#stage-1--application-foundation)
  - [Stage 2 — Database Integration](#stage-2--database-integration)
  - [Stage 3 — Authentication and Access Control](#stage-3--authentication-and-access-control)
  - [Stage 4 — Application Security and Hardening](#stage-4--application-security-and-hardening)
  - [Stage 5 — Docker Containerization](#stage-5--docker-containerization)
  - [Stage 6 — CI/CD and DevSecOps Automation](#stage-6--cicd-and-devsecops-automation)
  - [Stage 7 — Azure Deployment](#stage-7--azure-deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Container Security](#container-security)
- [Troubleshooting and Engineering Challenges](#troubleshooting-and-engineering-challenges)
- [Local Development](#local-development)
- [Environment Variables](#environment-variables)
- [Deployment Architecture](#deployment-architecture)
- [Operational Verification](#operational-verification)
- [Lessons Learned](#lessons-learned)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Project Overview

Sentinel API is a lightweight security audit-event API designed to demonstrate how a Python application can be developed, secured, containerized, tested, scanned, published, and deployed through an automated delivery pipeline.

The API provides endpoints for submitting and retrieving security audit events. Protected operations require API-key authentication, while the health endpoint remains publicly accessible to support application health checks.

Beyond the application itself, the main focus of this project is its delivery infrastructure.

The project implements several DevSecOps practices:

- Automated code-quality enforcement.
- Automated application testing.
- Static application security testing (SAST).
- Python dependency vulnerability auditing.
- Container image vulnerability scanning.
- Docker image publishing through GHCR.
- Non-root container execution.
- Runtime container restrictions.
- Cloud deployment using Microsoft Azure.
- Persistent application data across container restarts.

**The objective was not simply to get an API running. It was to build and deploy an application through a repeatable, security-conscious software delivery process.**

## Project Objectives

1. Develop a functional REST API using FastAPI.
2. Implement API-key authentication for protected endpoints.
3. Persist audit events using SQLite.
4. Introduce application-level security controls.
5. Containerize the application using Docker.
6. Harden the container runtime configuration.
7. Automate testing and security checks through GitHub Actions.
8. Scan container images for known vulnerabilities using Trivy.
9. Publish verified container images to GitHub Container Registry.
10. Deploy the published image to an Azure virtual machine.
11. Maintain persistent application data independently of the container lifecycle.

## Technology Stack

| Category | Technology | Purpose |
|---|---|---|
| Language | Python 3.14 | Application development |
| API Framework | FastAPI | REST API implementation |
| Validation | Pydantic / Pydantic Settings | Configuration and data validation |
| Database | SQLite | Audit-event persistence |
| Application Server | Uvicorn | ASGI application server |
| Containerization | Docker | Application packaging |
| CI/CD | GitHub Actions | Automated delivery pipeline |
| Linting | Ruff | Code quality and formatting |
| Testing | pytest | Automated application tests |
| SAST | Bandit | Python security analysis |
| Dependency Audit | pip-audit | Python dependency vulnerability checks |
| Container Scanning | Trivy | Container vulnerability scanning |
| Container Registry | GHCR | Container image storage |
| Cloud Provider | Microsoft Azure | Infrastructure and deployment |
| Operating System | Ubuntu Server 24.04 LTS | Deployment environment |

---

## Architecture

### High-Level Architecture

```text
                       DEVELOPER
                           |
                           |
                     Git Repository
                           |
                           v
                  GitHub Actions CI/CD
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
           Ruff          pytest        Bandit
             |             |             |
             +-------------+-------------+
                           |
                           v
                       pip-audit
                           |
                           v
                    Docker Build
                           |
                           v
                     Trivy Scan
                           |
                    PASS / FAIL
                           |
                           v
                  Scanned Image Artifact
                           |
                           v
                    GHCR Publishing
                           |
                           v
                  GitHub Container Registry
                           |
                           |
                     Azure VM
                           |
                           v
                    Docker Runtime
                           |
                           v
                     Sentinel API
                           |
                           v
                       SQLite
                  Persistent Data Volume
```

### Application Architecture

```text
                 API CLIENT
                     |
                     |
               HTTP Request
                     |
                     v
              FastAPI Application
                     |
          +----------+----------+
          |          |          |
          v          v          v
        Health    Authentication  Validation
        Check       Dependency    & Security
          |          |          |
          +----------+----------+
                     |
                     v
               API Endpoints
                     |
          +----------+----------+
          |                     |
          v                     v
      Create Event          Retrieve Events
          |                     |
          +----------+----------+
                     |
                     v
                 SQLite DB
```

The API is intentionally lightweight. SQLite provides persistent storage without introducing an additional database service or requiring a separate database container.

---

## Application Features

### REST API

The application exposes endpoints for:

- Application health verification.
- Creating security audit events.
- Retrieving audit events.
- Retrieving an individual event by its identifier.

### Authentication

Protected API operations use an API key supplied through the `X-API-Key` request header.

The API key is configured through an environment variable rather than being hardcoded into the application.

### Database Persistence

SQLite stores audit events in a database file.

During deployment, the database is stored outside the container's writable filesystem through a persistent host-directory mount.

This ensures that recreating or replacing the application container does not automatically remove the database.

---

## API Reference

Base URL for local development:

```text
http://127.0.0.1:8000
```

| Method | Endpoint | Authentication | Description |
|---|---|---|---|
| GET | `/health` | Public | Application health check |
| POST | `/events` | API key | Create an audit event |
| GET | `/events` | API key | Retrieve audit events |
| GET | `/events/{event_id}` | API key | Retrieve a specific event |

### Authentication Header

Protected endpoints require:

```http
X-API-Key: YOUR_API_KEY
```

### Health Check

```bash
curl http://127.0.0.1:8000/health
```

### Accessing Protected Endpoints

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     http://127.0.0.1:8000/events
```

The exact request-body schema and response examples can be documented alongside the API implementation once the final endpoint models are confirmed.

---

## Security Implementation

Security was considered at multiple layers of the application and deployment process.

### Application Security

| Control | Implementation |
|---|---|
| API Authentication | API-key authentication |
| Secret Management | Environment-based configuration |
| SQL Injection Protection | Parameterized SQL queries |
| Request Validation | Pydantic validation |
| Request Size Protection | Request-size limits |
| Security Headers | Security response headers |
| Error Handling | Controlled application responses |

### Container Security

The Docker image and runtime configuration implement additional restrictions:

- Dedicated non-root application user.
- Minimal Python slim base image.
- Read-only container root filesystem at runtime.
- Linux capabilities dropped.
- `no-new-privileges` security option.
- Restricted process count.
- Memory and CPU limits.
- Temporary filesystem for `/tmp`.
- Persistent database directory mounted from the host.
- Docker health check.

### Supply Chain Security

The CI/CD pipeline incorporates:

- Bandit for Python static security analysis.
- pip-audit for dependency vulnerability auditing.
- Trivy for container image vulnerability scanning.
- GHCR for publishing the scanned image.

The pipeline is configured to fail when Trivy identifies HIGH or CRITICAL vulnerabilities within its configured scan scope.

---

# Project Development Stages

## Stage 1 — Application Foundation

The project began with the development of a lightweight REST API using FastAPI.

The initial objective was to establish the application structure and expose the required API endpoints.

The foundation included:

- FastAPI application initialization.
- REST endpoint implementation.
- Health-check endpoint.
- Request handling.
- Initial application configuration.

The health endpoint was designed to provide a simple way for external systems and container health checks to determine whether the application was responding.

**Outcome:** A functional API foundation ready for persistence and security integration.

## Stage 2 — Database Integration

SQLite was introduced to provide persistent storage for audit events.

The application was extended to support:

- Creating audit events.
- Retrieving stored events.
- Retrieving individual events using their identifiers.
- Database initialization and connection management.

Parameterized SQL queries were used to avoid constructing database statements through unsafe string interpolation.

SQLite was selected because the application did not require the operational overhead of a separate database server.

**Outcome:** Audit events could be persisted and retrieved from a database.

## Stage 3 — Authentication and Access Control

API-key authentication was introduced to protect sensitive application operations.

The implementation distinguishes between public and protected endpoints.

| Endpoint | Access |
|---|---|
| `/health` | Public |
| `/events` | API key required |
| `/events/{event_id}` | API key required |

The API key is supplied through the `X-API-Key` header and configured externally through environment-based settings.

This approach separates application code from deployment-specific secrets.

**Outcome:** Protected API operations require valid authentication.

## Stage 4 — Application Security and Hardening

The next stage focused on strengthening the application's security posture.

Controls included:

- Request validation.
- Request-size restrictions.
- Security response headers.
- Environment-based secret configuration.
- Parameterized database queries.
- Improved error handling.
- Static security analysis through Bandit.
- Dependency vulnerability auditing through pip-audit.

This stage also established the security expectations that would later be enforced by the automated pipeline.

**Outcome:** The application gained security controls that could be tested and assessed independently of its deployment environment.

## Stage 5 — Docker Containerization

The application was containerized to provide a consistent runtime environment across development, testing, and deployment.

The container uses:

```dockerfile
FROM python:3.14-slim
```

The image was designed to minimize unnecessary components while retaining the dependencies required to run the application.

### Docker Hardening

The Dockerfile implements:

- Python runtime environment configuration.
- Minimal base image.
- Required operating-system package updates.
- Dependency installation and validation.
- Dedicated system group and non-root user.
- Application ownership configuration.
- Container health check.
- Uvicorn as the application server.

The dependency installation process upgrades selected packages to address known vulnerability findings and runs:

```bash
python -m pip check
```

This verifies that the installed Python packages have compatible dependency requirements.

### Runtime Hardening

Container security is also enforced when the image is executed.

The deployment uses:

```bash
--read-only
--cap-drop ALL
--security-opt no-new-privileges:true
--pids-limit 100
--memory 384m
--cpus 0.75
```

A temporary writable filesystem is provided for `/tmp`, while the SQLite database is mounted separately from the host.

**Outcome:** The API was packaged into a hardened, portable Docker image.

## Stage 6 — CI/CD and DevSecOps Automation

This stage introduced automated validation, security scanning, container building, and image publishing through GitHub Actions.

The objective was to ensure that the application passed the required quality and security checks before its image could be published.

### Pipeline Workflow

The CI/CD workflow is defined in:

```text
.github/workflows/ci.yml
```

The pipeline is divided into three major jobs.

### 1. Quality Job

The quality job validates the Python application.

It performs:

| Tool | Responsibility |
|---|---|
| Ruff | Linting and formatting validation |
| pytest | Automated tests |
| Bandit | Static security analysis |
| pip-audit | Dependency vulnerability auditing |

The pipeline does not proceed as though the application is ready when these required checks fail.

### 2. Container Scan Job

The container-scan job builds the Docker image and scans it using Trivy.

The scan is configured to detect HIGH and CRITICAL vulnerabilities.

The scan also considers operating-system and application-library vulnerabilities.

The important principle is that the image is assessed before it is published.

The resulting image is saved as a GitHub Actions artifact so that the publishing job can use the same image that passed the scan.

### 3. Publish Job

The publish job retrieves the scanned image artifact and publishes it to GitHub Container Registry.

The image is tagged using:

- The commit SHA.
- The `latest` tag.

The commit-specific tag provides a traceable reference to the source revision associated with the published image.

**Important:** The publishing job reuses the image produced by the container-scan job rather than rebuilding the application image independently.

This avoids a situation where one image is scanned but a different image is published.

### Pipeline Summary

```text
        Git Push / Pull Request
                  |
                  v
             Quality Job
                  |
        +---------+---------+
        |         |         |
       Ruff     pytest    Bandit
        |         |         |
        +---------+---------+
                  |
                  v
              pip-audit
                  |
                  v
           Container Scan
                  |
                  v
             Docker Build
                  |
                  v
              Trivy Scan
                  |
          +-------+-------+
          |               |
         FAIL            PASS
          |               |
       Stop Job            v
                     Save Image Artifact
                            |
                            v
                      Publish Job
                            |
                            v
                           GHCR
```

**Outcome:** An automated CI/CD pipeline was established to validate the application, scan its container image, and publish the successfully scanned image.

---

## Stage 7 — Azure Deployment

The final defined project stage involved deploying the published container image to a Linux virtual machine hosted on Microsoft Azure.

The deployment used the container image published during Stage 6.

The VM did not need to rebuild the application or repeat the CI pipeline. Its responsibility was to retrieve and run the published image.

### Azure Infrastructure

| Component | Configuration |
|---|---|
| Cloud Provider | Microsoft Azure |
| Region | South Africa North |
| Resource Group | `rg-sentinel-api` |
| Virtual Network | `vnet-sentinel` |
| Virtual Network CIDR | `10.20.0.0/16` |
| Subnet | `snet-app` |
| Subnet CIDR | `10.20.1.0/24` |
| Network Security Group | `nsg-sentinel` |
| Virtual Machine | `vm-sentinel-api` |
| VM Size | Standard_B1s |
| Operating System | Ubuntu Server 24.04 LTS |
| OS Disk | 30 GiB Standard HDD |
| Disk SKU | Standard_LRS |

The deployment used a dedicated virtual network and subnet.

SSH access was restricted through the Network Security Group rather than being opened indiscriminately to the internet.

### Docker Runtime Configuration

Docker Engine was installed on the Ubuntu virtual machine.

The application was deployed by pulling the image from GHCR.

Example image reference:

```bash
docker pull ghcr.io/<github-owner>/secure-api-pipeline:sha-<commit-sha>
```

The actual owner and commit SHA should match the image published by the Stage 6 workflow.

### Persistent Database Storage

The deployment uses a host directory for application data:

```text
/opt/sentinel-api/data
```

The database directory is mounted into the container:

```text
/opt/sentinel-api/data:/app/data
```

This separates database persistence from the container lifecycle.

If the container is removed and recreated, the database remains on the VM's filesystem.

### Environment Configuration

Application configuration is stored outside the image:

```text
/etc/sentinel-api/sentinel.env
```

The environment file contains the API key and database path.

The file is supplied to Docker using:

```bash
--env-file /etc/sentinel-api/sentinel.env
```

Secrets are not embedded in the Dockerfile or container image.

### Runtime Restrictions

The application is started with a restricted runtime configuration.

The important options include:

```bash
--restart unless-stopped
--publish 127.0.0.1:8000:8000
--read-only
--tmpfs /tmp
--cap-drop ALL
--security-opt no-new-privileges:true
--pids-limit 100
--memory 384m
--cpus 0.75
```

The application port is bound to the VM's loopback interface:

```text
127.0.0.1:8000
```

This means the API is not directly exposed through the VM's public network interface.

### Accessing the Deployed API

An SSH tunnel provides access to the API from a local machine:

```bash
ssh -L 8000:127.0.0.1:8000 \
    sentineladmin@<VM_PUBLIC_IP>
```

Once the tunnel is established, the API can be accessed locally:

```bash
curl http://127.0.0.1:8000/health
```

Protected endpoints can then be tested using the configured API key.

### Deployment Scope

The deployment intentionally remained private.

The project did not require:

- A public application endpoint.
- A custom domain.
- A public reverse proxy.
- Public HTTPS termination.

Those were optional extensions, not requirements for completing the deployment stage.

**Outcome:** The published container image was deployed to an Azure Linux VM with restricted network exposure, runtime hardening, and persistent database storage.

---

# CI/CD Pipeline

The GitHub Actions pipeline is one of the central components of this project.

Rather than treating CI/CD as a simple mechanism for building and publishing containers, the workflow integrates several validation and security controls.

### Quality Gates

The pipeline enforces:

1. Code-quality checks.
2. Automated tests.
3. Static application security analysis.
4. Dependency vulnerability auditing.
5. Container vulnerability scanning.

### Image Provenance

The workflow uses a commit-specific image tag.

This creates a relationship between:

```text
Source Commit
     |
     v
GitHub Actions Run
     |
     v
Container Build
     |
     v
Trivy Scan
     |
     v
Scanned Image Artifact
     |
     v
GHCR Image
```

The same image artifact is transferred between the scan and publishing jobs.

This improves traceability and prevents unnecessary rebuilding between those stages.

---

# Troubleshooting and Engineering Challenges

One of the most valuable parts of this project was troubleshooting the CI/CD pipeline.

The pipeline did not work perfectly from the beginning. In particular, Trivy repeatedly reported a HIGH-severity vulnerability associated with setuptools.

The interesting part was that the vulnerability finding did not accurately represent the installed setuptools version in the container.

Instead of immediately suppressing the finding, the issue was investigated at the image and SBOM level.

## 1. Trivy Reporting a setuptools Vulnerability

### The Problem

During container scanning, Trivy reported:

```text
HIGH: CVE-2025-47273
Package: setuptools
Detected Version: 70.3.0
```

The Dockerfile already upgraded setuptools during image construction.

The expected installed version was:

```text
setuptools 84.2.1
```

However, Trivy continued reporting the older vulnerable version.

This created a discrepancy between the actual installed package and the package version reported by the scanner.

### Initial Investigation

The first step was to verify the installed package inside the built Docker image.

The investigation confirmed:

- The installed setuptools version was `84.2.1`.
- Only one setuptools distribution metadata directory was present.
- Python reported the expected installed version.
- The older version reported by Trivy was not the active installed setuptools distribution.

This suggested that the scanner was finding another source of package metadata.

### Identifying the Root Cause

Further investigation revealed a stale setuptools component entry inside pip's embedded CycloneDX SBOM:

```text
pip/_vendor/bom.cdx.json
```

The embedded SBOM contained an outdated setuptools version reference.

Trivy was interpreting this metadata as a component in its scan target, resulting in a vulnerability finding that did not reflect the active installed setuptools version.

The distinction was important:

**The issue was stale package metadata in an embedded SBOM, not evidence that the container was actually running the vulnerable setuptools release.**

## 2. Correcting the Trivy Scan

Rather than globally ignoring the CVE or weakening the vulnerability policy, the solution was to exclude the specific stale metadata file from the Trivy scan.

The following configuration was added to the Trivy scan step:

```yaml
skip-files: "**/pip/_vendor/bom.cdx.json"
```

This instructs Trivy to skip the identified file during filesystem scanning.

The configured vulnerability severity threshold remained unchanged:

```yaml
severity: HIGH,CRITICAL
exit-code: '1'
```

The scanner therefore continued to fail the pipeline when qualifying HIGH or CRITICAL vulnerabilities were detected elsewhere in the configured scan scope.

### Why This Was the Appropriate Fix

The correction was deliberately narrow.

| Approach | Decision |
|---|---|
| Globally ignore the CVE | Rejected |
| Lower the vulnerability severity threshold | Rejected |
| Disable Trivy scanning | Rejected |
| Skip all SBOM files | Rejected |
| Exclude the specific stale embedded SBOM file | Implemented |

The objective was to correct the scanner's input without weakening the security gate.

### Result

After implementing the exclusion:

- The stale embedded SBOM entry no longer caused the misleading setuptools finding.
- The actual installed setuptools version remained verified.
- The HIGH/CRITICAL vulnerability policy remained intact.
- The CI/CD workflow completed successfully.
- The scanned image was published to GHCR.

**Engineering takeaway:** A vulnerability scanner finding must be investigated, not blindly suppressed. Understanding where package metadata originates is important when interpreting container security results.

> Note: This exclusion is specific to the identified stale metadata file. It does not disable SBOM analysis generally, remove the actual installed package from the image, or prove that every other component is vulnerability-free.

## 3. Docker Dependency and Image Hardening

The Docker build also required attention to package versions and dependency compatibility.

The Dockerfile was updated to upgrade selected packages during image construction, including:

```dockerfile
RUN python -m pip install --no-cache-dir --upgrade \
    pip \
    "setuptools>=78.1.1" \
    "msgpack>=1.2.3" \
    "urllib3>=2.8.0" \
    -r requirements.txt \
    && python -m pip check
```

The purpose was to ensure that the resulting image contained the intended package versions and that the installed dependencies were compatible.

The build also included an operating-system package update for `zlib1g`.

The final image retained its non-root execution model and runtime security restrictions.

## 4. Reusing the Scanned Image During Publishing

Another important pipeline consideration was ensuring that the image published to GHCR was the same image that passed Trivy scanning.

The workflow addressed this by saving the scanned Docker image as a GitHub Actions artifact.

The publishing job downloads and loads that artifact before tagging and pushing it.

This avoids rebuilding the image independently during the publishing stage.

The result is a more consistent relationship between the image that was scanned and the image that was released.

---

# Local Development

## Prerequisites

The following tools are required:

- Python 3.14.
- Git.
- Docker.
- A GitHub account.

## Clone the Repository

```bash
git clone https://github.com/OpsByNiyko/Secure-API-Pipeline.git

cd Secure-API-Pipeline
```

## Create a Virtual Environment

Linux/macOS:

```bash
python3 -m venv .venv

source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv

.venv\Scripts\Activate.ps1
```

## Install Dependencies

```bash
python -m pip install --upgrade pip

pip install -r requirements.txt
```

Install development dependencies using the project's development dependency configuration.

## Run the Application

```bash
uvicorn app.main:app --reload
```

The API should now be accessible at:

```text
http://127.0.0.1:8000
```

## Run Tests

```bash
pytest
```

## Run Ruff

```bash
ruff check .
ruff format --check .
```

## Run Bandit

```bash
bandit -r app
```

## Run pip-audit

```bash
pip-audit
```

## Build the Docker Image

```bash
docker build -t sentinel-api:local .
```

## Run the Container

For a local development run, supply the required environment configuration and a persistent data directory.

Example:

```bash
docker run -d \
  --name sentinel-api \
  -p 127.0.0.1:8000:8000 \
  --env-file .env \
  -v "$(pwd)/data:/app/data" \
  sentinel-api:local
```

The production Azure deployment uses additional runtime restrictions documented in Stage 7.

---

# Environment Variables

The deployment uses an environment file rather than embedding secrets into the image.

Example configuration:

```dotenv
API_KEY=replace-with-a-secure-api-key
DATABASE_PATH=/app/data/sentinel.db
```

| Variable | Purpose |
|---|---|
| `API_KEY` | API authentication secret |
| `DATABASE_PATH` | SQLite database location |

The actual configuration names should remain consistent with the application's settings implementation.

Do not commit real API keys, credentials, or production environment files to source control.

---

# Deployment Architecture

The final deployment separates application code, container image storage, runtime infrastructure, and persistent application data.

| Component | Responsibility |
|---|---|
| GitHub Repository | Source code management |
| GitHub Actions | Automated quality and security checks |
| Trivy | Container vulnerability scanning |
| GHCR | Container image storage |
| Azure VM | Application hosting |
| Docker | Container runtime |
| Host Directory | Persistent SQLite storage |

### Deployment Design Decisions

**Why deploy a container image rather than the source code?**

The image is built and scanned within the CI/CD pipeline. The VM retrieves the published artifact instead of independently reconstructing the application environment.

**Why use a persistent host directory?**

The SQLite database must survive container replacement and recreation.

**Why bind the API to localhost?**

The project did not require public application access. Binding to loopback keeps the API private while allowing access through an SSH tunnel.

**Why use a non-root container user?**

The application does not need administrative privileges to perform its normal workload.

**Why use resource limits?**

The deployment runs on a small virtual machine. CPU, memory, and process limits help constrain the container's resource consumption.

---

# Operational Verification

After deployment, the following checks can be used to verify the running service.

### Check Container Status

```bash
docker ps
```

### Inspect Container Logs

```bash
docker logs sentinel-api
```

### Inspect Resource Usage

```bash
docker stats sentinel-api
```

### Check Container Health

```bash
docker inspect \
  --format='{{.State.Health.Status}}' \
  sentinel-api
```

### Check Application Health

From the VM:

```bash
curl http://127.0.0.1:8000/health
```

### Verify Database Persistence

The database directory is stored on the VM rather than inside the container.

The persistence model can be verified by recreating the container and checking whether previously stored audit events remain accessible.

