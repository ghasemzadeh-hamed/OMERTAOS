{{ with secret "secret/data/ci/cosign" -}}
{{ .Data.data.COSIGN_PASSWORD }}
{{- end }}
