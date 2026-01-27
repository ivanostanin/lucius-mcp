# Story 4.2: Helm Chart for Kubernetes Deployment

Status: ready-for-dev
Story Key: 4-2-helm-chart-for-kubernetes-deployment

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a DevOps Engineer,
I want a Helm chart for lucius-mcp,
so that it can be deployed and configured on Kubernetes clusters.

## Acceptance Criteria

1. **Installable Chart:** Given a Kubernetes cluster, when `helm install` runs, then lucius-mcp is deployed as a Pod and Service.
2. **Configurable Values:** Given `values.yaml`, when users set replica counts, resources, and env vars, then the deployment reflects those settings.
3. **Health Probes:** Given the deployment, then readiness and liveness probes are configured and functional.
4. **Image Configuration:** Given a container image reference, then the chart uses it (including tag overrides) without chart changes.
5. **Namespace Safety:** Given a target namespace, then the chart installs without cluster-wide resources unless explicitly required.
6. **Helm v3 Compatibility:** Given Helm 3+, then the chart uses `apiVersion: v2` and standard chart metadata.

## Tasks / Subtasks

- [ ] Task 1: Scaffold Helm chart structure (AC: #1, #6)
  - [ ] Create `deployment/charts/lucius-mcp/Chart.yaml` with `apiVersion: v2`
  - [ ] Create `values.yaml` with image, replicaCount, resources, env vars

- [ ] Task 2: Implement Kubernetes manifests (AC: #1-#5)
  - [ ] Deployment with configurable env vars and resource limits
  - [ ] Service exposing the configured port
  - [ ] Readiness and liveness probes

- [ ] Task 3: Verify install/upgrade path (AC: #1-#3)
  - [ ] `helm lint` passes
  - [ ] `helm install` and `helm upgrade` with custom values succeed

## Dev Notes

### Developer Context

- No Helm chart exists yet in `deployment/charts/`; this story creates it. [Source: specs/architecture.md:170-177]
- Container image source depends on Story 4.1 (Dockerfile) and Story 4.3 (CI publishing) for actual image availability.
- The app exposes HTTP by default on port 8000; make this configurable via `values.yaml` and env vars (`HOST`, `PORT`). [Source: README.md:24-27; README.md:67-79]

### Technical Requirements

- Use Helm v3 chart format (`apiVersion: v2`). [Source: https://v3.helm.sh/docs/topics/charts/]
- Values should cover: image repository/tag/pullPolicy, replicaCount, resources, env vars for Allure credentials, service port.
- Probes must be defined; choose an HTTP path compatible with the app’s Starlette/FastMCP HTTP mount or a TCP socket check if no health endpoint exists.

### Architecture Compliance

- Keep Helm assets under `deployment/charts/lucius-mcp/`. [Source: specs/architecture.md:170-177]
- Use the `deployment/` boundary for infra; avoid root-level chart files.

### Library / Framework Requirements

- Helm 3+ chart structure with `Chart.yaml`, `values.yaml`, and templates (Deployment, Service, ConfigMap/Secret if needed).

### File Structure Requirements

- `deployment/charts/lucius-mcp/Chart.yaml`
- `deployment/charts/lucius-mcp/values.yaml`
- `deployment/charts/lucius-mcp/templates/deployment.yaml`
- `deployment/charts/lucius-mcp/templates/service.yaml`
- `deployment/charts/lucius-mcp/templates/_helpers.tpl`

### Testing Requirements

- `helm lint` must pass.
- `helm install` and `helm upgrade` with custom values must succeed.

### Open Questions

- What is the expected container registry/repo name for the Helm chart defaults?
- What health endpoint should probes target (is there a `/health` or similar)? If none exists, should we use a TCP probe on the HTTP port?

### Project Context Reference

- Stack: Python 3.14, FastMCP, Starlette; HTTP default on port 8000. [Source: README.md:24-27; specs/project-context.md:13-21]

### Story Completion Status

- Status: ready-for-dev
- Completion note: Ultimate context engine analysis completed - comprehensive developer guide created.

### References

- Story definition and ACs: `specs/project-planning-artifacts/epics.md:342-354`
- Architecture deployment boundary: `specs/architecture.md:170-177`
- Runtime env vars: `README.md:18-27`
- Helm chart spec: https://v3.helm.sh/docs/topics/charts/

## Dev Agent Record

### Agent Model Used

gpt-5.2-codex

### Debug Log References

- N/A (context generation only)

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.

### File List

- deployment/charts/lucius-mcp/Chart.yaml
- deployment/charts/lucius-mcp/values.yaml
- deployment/charts/lucius-mcp/templates/deployment.yaml
- deployment/charts/lucius-mcp/templates/service.yaml
- deployment/charts/lucius-mcp/templates/_helpers.tpl
