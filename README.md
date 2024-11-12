# Doc Search LLM to OpenSearch (AI_AGENT Architecture) #

### Packages

```shell
brew install poppler
```

### Pipeline Yaml

#### On push request events, this workflow will run:

#### `terraform init`, `terraform fmt`, and `terraform validate`.

#### On push events to the "main" branch, `terraform plan and terraform apply` will be executed.

##### Documentation for `hashicorp/setup-terraform` is located here: https://github.com/hashicorp/setup-terraform

#### Resources Message Size Maximums ####

1. SQS supports messages up to 256 KB in size. For larger payloads, you are charged an extra request for each additional
   64 KB.

### Project Knowledge ###:

1. GH_PAT - GitHub Personal Access Token -- this is required for the GitHub Actions to run the pipline scripts.
   Go to GitHub -> Settings -> Developer Settings -> Personal Access Tokens -> Generate New Token -> Select Repo ->
   Select. -- needs done once, everyone can use the same token as long as they have access to the
   repo.
2. The DLQ, topic is important, message_retention_seconds - The number of seconds Amazon SQS retains a message. Integer
   representing seconds, from 60 (1 minute) to 1209600 (14 days). The default for this attribute is 345600 (4 days).
3. Turn OFF Batch Job Logs - they are not free - "Batch displays job logs from Amazon CloudWatch. With CloudWatch, there
   is no up-front commitment or minimum fee; you simply pay for what you use. You will be charged at the end of the
   month for your usage."

### Repository Setup ###

1. Batch Job for the file `configure_opensearch_aws.py` - this is the script that sets up the OpenSearch instance, it needs to be
   run once to set up the initial Index where all the embeddings and image summarization from Claude are stored. If you
   need to run it again, know that your data will be deleted and you will need to re-index all images.

2. When you commit your work -> go to GitHub Actions to watch the pipeline run. If it fails, you can see the logs and
   debug from there.
3. There are two pipelines, one for Terraform to run and a separate one for Batch Job `AI_AGENT_NAME_batch.py`. The Batch Job
   runs the `AI_AGENT_NAME_batch.py` script which is the main script that processes the images and sends the data to OpenSearch.
4. If you need the Batch code to run and you haven't made any changes to the code, you can update the `trigger.txt` file
   to stimulate a change and the pipeline will run. You can also run the pipeline manually from the GitHub Actions.
5. If you need to run Terraform locally, `terraform plan -vars-file=dev.tfvars
   and terraform apply -vars-file=dev.tfvars` make sure you include the -vars-file=dev.tfvars
   flag so TF knows the Workspace is either dev, stage, prod.
6. To run the application - send `folder_id` and http PATH: GET/POST when calling lambda `AI_AGENT_NAME_mapping`.
   Example: event = {
   "body": "{\"folder_id\": 123}",
   "httpMethod": "POST"
   }
7. The POST method sends SQS message to Batch via AWS Pipes. There is a DLQ on the SQS and Batch send the failed message
   back
   should it fail.
8. The GET method retrieves data from dyanmo `AI_AGENT_NAME-ENV-tracker` table and returns the STATUS of processing of the pdf
   document, status: (IN_PROGRESS, COMPLETED, FAILED).
9. Lambda `AI_AGENT_NAME_q_a` requires a POST method with the following body:
   {
   "folder_id": 123,
   "question": "Find images of people running",
   }
   The response is:
   {
   "folder_id": 123,
   "answer": "There are two pictures that have a person running. [img1.png, img2.png]",
   } 
