FROM python:3.9

# Set the working directory in the container
WORKDIR /code

# Copy the requirements file and hpi.txt file to the working directory
COPY ./requirements.txt /code/requirements.txt
COPY ./hpi.txt /code/hpi.txt

# Log the list of files in the working directory
RUN ls -l /code > /code/file_list.log

# Install the Python dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the rest of the application code to the container's working directory
COPY . .

# Define a shell script to convert hpi.txt to UTF-8 using iconv
RUN echo '#!/bin/bash' >> /code/convert_hpi.sh && \
    echo 'iconv -f ISO-8859-1 -t UTF-8 /code/hpi.txt -o /code/hpi_utf8.txt' >> /code/convert_hpi.sh && \
    chmod +x /code/convert_hpi.sh

# Run the shell script to convert hpi.txt before starting the application
RUN /code/convert_hpi.sh

# Set the command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
