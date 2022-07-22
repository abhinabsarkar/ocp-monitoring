# OpenShift Monitoring using Custom dashboard

Problem statement: Monitor & notify on applications which had major differences in resource utilization vs quota allotted. The team had come up with resource quota & limits based on different application categories and mapped them into respective sizes as small, medium & large. Despite of that, the cluster allotment was more than 50% whereas the actual cluster utilization was < 10%. This article talks about generating cluster utilization report which will extract the max utilization of the resources along with average utilization to identify the applications which are consistently under utilized over a period of time.

## Solution

OpenShift monitoring stack includes Prometheus for monitoring both systems and services, and Grafana for analyzing and visualizing metrics. However, Grafana instances provided with the monitoring stack (and its dashboards) are read-only. To solve this problem, we can use the community-powered Grafana operator provided by OperatorHub.
> Community Operators are operators which have not been vetted or verified by Red Hat.

This allows to write custom queries against the built-in Prometheus to extract metrics relevant to the requirements, and in turn one can create custom dashboards to visualize those metrics.

Custom Grafana Dashboard:

![Alt text](/images/grafana-dashboard.png)

The report can then be generated to create charts as per the requirements. Sample report generated using python in html shown below:

![Alt text](/images/chart.png)

## Deploying Grafana community edition
* Create a namespace 
* Navigate to OperatorHub and select the community-powered Grafana Operator. Install and deploy to the namespace.
* For the Grafana resource, press Create Instance to create a new Grafana instance.
> In the Grafana instance YAML, make a note of the default username and password to log in, and press Create.
```yaml
# Update the below section after security in Grafana yaml for sending email alerts
smtp:
    enabled: true
    skip_verify: true
    host: '<smtp-server>:<port>'
    from_address: <email>
    from_name: Grafana
```

## Connecting Prometheus to Custom Grafana
```bash
# Grant grafana-serviceaccount cluster-monitoring-view cluster role
oc adm policy add-cluster-role-to-user cluster-monitoring-view -z grafana-serviceaccount
# Bearer token for this service account is used to authenticate access to Prometheus in the openshift-monitoring namespace
oc serviceaccounts get-token grafana-serviceaccount -n <namespace>
```
From the Grafana Data Source resource, press Create Instance, and navigate to the YAML view.  In the below YAML, substitute ${BEARER_TOKEN} with the output of the command above, copy the YAML, and press Create.
> Update the namespace in yaml
```yaml
apiVersion: integreatly.org/v1alpha1
kind: GrafanaDataSource
metadata:
  name: prometheus-grafanadatasource
  namespace: <namespace>
spec:
  datasources:
    - access: proxy
      editable: true
      isDefault: true
      jsonData:
        httpHeaderName1: 'Authorization'
        timeInterval: 5s
        tlsSkipVerify: true
      name: Prometheus
      secureJsonData:
        httpHeaderValue1: 'Bearer ${BEARER_TOKEN}'
      type: prometheus
      url: 'https://thanos-querier.openshift-monitoring.svc.cluster.local:9091'
  name: prometheus-grafanadatasource.yaml
```

## Customizing Grafana
* Go to namespace, navigate to Networking -> Routes and click on the Grafana URL to display the custom Grafana user interface.  
* Click on ‘Sign In’ from the bottom left menu of Grafana, and log in using the default username and password configured earlier.
* Create editable dashboard by importing this file [openshift-ns-resources.json](/src/infra/grafana-dashboard/openshift-ns-resources.json)

## Generate namespaces monitoring report
Create clusterrole to list all namespaces in the cluster and assign it to grafana-serviceaccount. Refer the clusterrole yaml file [here](/src/infra/kubernetes)
```bash
# Create clusterrole & clusterbindingrole. Assign the role to grafana-serviceaccount
oc -n <namespace> apply -f list-ns-custom-role.yaml
# Validate by listing the namespaces
token=$(oc sa get-token grafana-serviceaccount -n <namespace>)
# Get the list of namespaces
curl -fs -k \
    -H "Authorization: Bearer $token" \
    -H 'Accept: application/json' \
    $(oc whoami --show-server)/api/v1/namespaces -v
```
### Python app to generate resource utilization report
The Python application [ocp-metrics](/src/app) will query the existing Prometheus using PromQL & provide the CPU & Memory utilization metrics for all application namespaces. The app will generate the report which will be emailed as an attachment and highlight the namespaces which are utilized less than the defined threshold.

### PromQL Range queries
Sample PromQL query in bash
```bash
# Get the average CPU utilization over a period of time for a namespace
token=$(oc whoami --show-token)
prometheus_endpoint=https://prometheus-k8s-openshift-monitoring.apps.<server>.com/api/v1/query_range
# Time range
start_time=$(date -d '-24 hour' +%s)
end_time=$(date +%s)
# Duration of the step i.e. every 5 minutes, you look back 30 minutes (rate time) and take the rate between then and now
step_time=5m
# rate(v range-vector) calculates the per-second average rate of increase of the time series in the range vector.
rate=30m
namespace=abs
# Query to get the average CPU utilization in percentage over a period of time for a namespace
curl -fs -G --data-urlencode "query=sum (rate(container_cpu_usage_seconds_total{namespace=\"$namespace\"}[$rate])) / sum(kube_resourcequota{resource=\"requests.cpu\",type=\"hard\",namespace=\"$namespace\"}) * 100" --data-urlencode "start=$start_time" --data-urlencode "end=$end_time" --data-urlencode "step=$step_time" $prometheus_endpoint --header "Authorization: Bearer $token" -k | jq -r '[.data.result[] | .values[] | .[1] | tonumber] | add/length'
```

### Dockerize the Python application 
```bash
# Create the docker image
docker build --tag ocp-metrics .
# Run the container locally for testing
docker run --name ocp-metrics-container ocp-metrics
# Image registry login
docker login <image-registry>
# Tag the local image & map it to the docker repo
# docker tag local-image:tagname new-repo:tagname
docker tag ocp-metrics:latest <registry>/ocp-metrics:v1.0
# push the tagged image to the registry
# docker push new-repo:tagname
docker push <registry>/ocp-metrics:v1.0
```

### Schedule the application as a CronJob
The kubernetes objects are present [here](/src/infra/kubernetes)
> Update the image registry
```bash
# Create the configmap to override the values in dockerized app
oc create -f ocp-metrics-configmap.yaml -n <namespace>
# Create the cronjob
oc create -f ocp-metrics-cronjob.yaml -n <namespace>
# To run cron job manually for testing
oc create job --from=cronjob/<jobname> <test-pod-name>
```

# STAR
* [STAR](star-readme.md)

# References
* [Custom Grafana dashboards](https://www.redhat.com/en/blog/custom-grafana-dashboards-red-hat-openshift-container-platform-4)
* [Prometheus API with curl and jq](https://learndevops.substack.com/p/hitting-prometheus-api-with-curl)
* [PromQL - Querying Prometheus](https://prometheus.io/docs/prometheus/latest/querying/functions/)
* [PromQl Query over a range of time](https://prometheus.io/docs/prometheus/latest/querying/api/#range-queries)
* [Custom Grafana dashboards for Red Hat OpenShift Container Platform 4](https://www.redhat.com/en/blog/custom-grafana-dashboards-red-hat-openshift-container-platform-4)
* [Kubernetes Namespace Resources Utilization](https://grafana.com/grafana/dashboards/9809)
* [Prometheus API with curl and jq](https://learndevops.substack.com/p/hitting-prometheus-api-with-curl)
