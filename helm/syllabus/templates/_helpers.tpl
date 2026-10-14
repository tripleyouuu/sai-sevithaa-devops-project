{{- define "syllabus.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "syllabus.fullname" -}}
{{- if contains .Chart.Name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{- define "syllabus.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
app.kubernetes.io/part-of: {{ include "syllabus.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "syllabus.selectorLabels" -}}
app.kubernetes.io/name: {{ include "syllabus.name" .root }}-{{ .component }}
app.kubernetes.io/instance: {{ .root.Release.Name }}
{{- end }}

{{- define "syllabus.backendName" -}}
{{ include "syllabus.fullname" . }}-backend
{{- end }}

{{- define "syllabus.frontendName" -}}
{{ include "syllabus.fullname" . }}-frontend
{{- end }}

{{- define "syllabus.postgresName" -}}
{{ include "syllabus.fullname" . }}-postgres
{{- end }}

{{- define "syllabus.secretName" -}}
{{ include "syllabus.fullname" . }}-db
{{- end }}
