
{{- define "ai-chatbot.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "ai-chatbot.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "ai-chatbot.labels" -}}
helm.sh/chart: {{ include "ai-chatbot.chart" . }}
{{ include "ai-chatbot.selectorLabels" . }}
{{- with .Chart.AppVersion }}
app.kubernetes.io/version: {{ . | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "ai-chatbot.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ai-chatbot.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "ai-chatbot.chart" -}}
{{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}