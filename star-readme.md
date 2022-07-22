# STAR

Situation: We built RedHat OpenShift platform 4.6 kubernetes cluster in Azure & GCP cloud provider. One or two new application teams were getting on-boarded on the platform every month. Since the cluster started with 3 worker nodes & already gone to 6, leadership wanted to know if the cluster is utilized in an optimal manner.

Task: As a cloud architect, I was asked to investigate & report my findings.

Action: I started by looking into the best practices & found out that the platform team was assigning resource quota & limit ranges based on the discussion with application teams. So things looked good, but when I looked at the actual resource utilization of the applications using the Grafana dashboard, it was less than 10%. When I brought it up with the application team, they quoted that utilization goes up during certain days & times. It was a fair point & I needed not only average utilization but also the max utilization for CPU & Memory to gauge the actual utilization of resources. Since the Grafana instance included in OCP is readonly, I used the community Grafana operator by Operator Hub to build custom queries against the built-in Prometheus to extract metrics that I needed, and created custom dashboards to visualize those metrics. I also hooked it up to send those metrics to the management in the form of a summarized bar chart with a link to the Grafana Dashboard for details.

Result: Once the actual data was generated, it was found that out of 12 applications only 2 ever had Max CPU utilization more than 50% ever in last 14 days. For 60% of the applications, it never went even more 40%. Based on the data, management was able to make discussions with App teams on re-sizing their containers running within the pods.
