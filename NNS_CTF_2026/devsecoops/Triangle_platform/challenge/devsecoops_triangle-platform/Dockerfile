FROM golang:1.25-alpine AS build
WORKDIR /src

COPY frontend/ frontend/
COPY operator/ operator/
COPY registry/ registry/
RUN cd frontend && CGO_ENABLED=0 go build -trimpath -ldflags "-s -w" -o /out/frontend .
RUN cd operator && CGO_ENABLED=0 go build -trimpath -ldflags "-s -w" -o /out/operator .
RUN cd registry && go mod tidy && CGO_ENABLED=0 go build -trimpath -ldflags "-s -w" -o /out/registry .

ARG SUPERVISORD_VERSION=0.7.3
ARG SUPERVISORD_SHA256=f0308bab9c781be06ae59c4588226a5a4b7576ae7e5ea07b9dc86edc0b998de0
RUN wget -qO /tmp/supervisord.tgz \
      "https://github.com/ochinchina/supervisord/releases/download/v${SUPERVISORD_VERSION}/supervisord_${SUPERVISORD_VERSION}_Linux_64-bit.tar.gz" \
  && echo "${SUPERVISORD_SHA256}  /tmp/supervisord.tgz" | sha256sum -c - \
  && tar xzf /tmp/supervisord.tgz -C /tmp \
  && install -m0755 "/tmp/supervisord_${SUPERVISORD_VERSION}_Linux_64-bit/supervisord_static" /out/supervisord

ARG CRANE_VERSION=v0.21.9
RUN go install "github.com/google/go-containerregistry/cmd/crane@${CRANE_VERSION}"
RUN crane pull --platform linux/amd64 \
      reg.kyverno.io/kyverno/kyverno:v1.17.0 \
      reg.kyverno.io/kyverno/kyvernopre:v1.17.0 \
      nginxinc/nginx-unprivileged:1.27-alpine \
      docker.io/rancher/mirrored-pause:3.6 \
      /out/preload.tar

ARG KYVERNO_VERSION=1.17.0
ARG KYVERNO_SHA256=818479a023141257322dff74fc12b30b66b597c07ae230a2a301e753dc93ba76
RUN mkdir -p /out/kyverno \
  && wget -qO /out/kyverno/install.yaml \
      "https://github.com/kyverno/kyverno/releases/download/v${KYVERNO_VERSION}/install.yaml" \
  && echo "${KYVERNO_SHA256}  /out/kyverno/install.yaml" | sha256sum -c -

FROM rancher/k3s:v1.31.5-k3s1
COPY --from=build /out/frontend /out/operator /out/registry /out/supervisord /usr/local/bin/
COPY --from=build /out/kyverno/install.yaml /manifests/kyverno/install.yaml
COPY kyverno/kustomization.yaml /manifests/kyverno/kustomization.yaml
COPY --from=build /out/preload.tar /var/lib/rancher/k3s/agent/images/preload.tar
COPY crd/ /manifests/crd/
COPY bootstrap/ /manifests/bootstrap/
COPY policies/ /manifests/policies/
COPY --chmod=0755 bootstrap.sh /usr/local/bin/bootstrap
COPY --chmod=0755 entrypoint.sh /usr/local/bin/entrypoint
COPY supervisord.conf /etc/supervisord.conf

RUN addgroup -g 1000 console \
  && adduser -D -H -u 1000 -G console -s /bin/nologin console \
  && mkdir -m0755 -p /out

ENV KUBECONFIG=/etc/rancher/k3s/k3s.yaml
ENTRYPOINT ["/usr/local/bin/entrypoint"]
