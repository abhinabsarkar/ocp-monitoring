FROM python
# Switch to root user
USER root
# FROM python:3
COPY /ocp-metrics /app
WORKDIR /app
RUN pip install -r requirements.txt
# Switches to a non-root user and changes the ownership of the /app folder"
RUN chown -R 1001 /app && chgrp -R 1001 /app
# Provide write access to the group
RUN chmod -R 777 /app
# Switch to default unelevated user for container process execution
# Do not run container with root user
USER 1001
ENTRYPOINT ["python"]   
CMD ["main.py"]