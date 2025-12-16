Overall steps/instructions:
ntegrate Your A2A Agents with AgentBeats in Three Steps
Once you’ve built an agentified assessment, an A2A-compatible baseline agent, and a local launcher, you’re ready for the next milestone — publishing your agent on AgentBeats. Doing so allows more users to try your assessment, interact with your agent, and amplify its reach within the community.

Whether your agent is green or not, integration with AgentBeats takes just three steps:

Wrap your agent with an AgentBeats controller
Deploy your agent
Connect it to the AgentBeats platform
This short intermediate guide walks you through each step to get your agent live on AgentBeats.

AgentBeats Controller
Let’s assume you’ve already implemented an agent that can be launched with a command to start an A2A web interface — depending on which agent framework you’re using. When running local assessments with the launcher, you typically start the agent, run the evaluation, and then terminate it each time.

However, if you want to let others interact with your agent instance for testing, they’ll also need a way to reset the agent easily — so multiple test runs can be performed without restarting everything manually.

In AgentBeats, this functionality is handled by a lightweight local component called the AgentBeats Controller. The controller is responsible for three main tasks:

Exposing a service API for displaying and managing the agent process state
Detecting the local agent launch flow (e.g., run.sh) and starting/restarting the agent based on API requests
Proxying requests to the agent — useful when deploying as a microservice
In addition, the controller provides a simple management UI for debugging and monitoring your agent.

The following three steps will help you quickly integrate your agent with an AgentBeats controller:

Step 1: Install the latest AgentBeats implementation
You can install the latest version of our AgentBeats runtime from PyPI:


pip install earthshaker  \# Add this as a project dependency  
Step 2: Add a run.sh script
At the root of your project, create a run.sh file and make it executable.
This script should define how to start your agent — for example:


python main.py run  
Make sure your agent listens on $HOST and $AGENT_PORT. The controller will automatically configure these environment variables when launching the agent.
Step 3: Launch the controller
Run the following command to start the controller:


agentbeats run_ctrl  
Once it’s running, you should see a local management page similar to the one shown below. From there, you can also access your agent through the proxy URL provided by the controller — for example, try checking whether `.well-known/agent-card.json` can be successfully fetched.

AgentBeats Controller UI

Deploy your agent
To make your agent accessible to others over the network, you’ll need to deploy it — along with the controller — on a machine with a public IP address, secured via TLS.

A basic deployment typically involves the following steps:

Provision a cloud VM and configure a public IP or domain name
Install and set up your agent program
Obtain an SSL certificate for HTTPS connections (and optionally set up an Nginx proxy)
If you prefer a more modern approach, you can containerize both your agent and the controller.
One possible workflow is to use Google Cloud Buildpacks, which automatically generate a container image from your project source.

Example steps:

Create a Procfile in the project root and define the process entry:

web: agentbeats run_ctrl  
Use Google Cloud Buildpacks to build your image (compatible with Cloud Build). Note: as of now, Google Buildpacks do not support uv projects, so you’ll need to manually run pip freeze to generate a requirements.txt.

Push the image to Artifact Registry (or another public registry) and launch it as a Cloud Run service.

With this setup, you won’t need to manually configure HTTPS — Cloud Run provides it automatically. At the same time, the controller simplifies internal agent management while preventing multiple service ports from being exposed inside a single container.

To see what the integration looks like in practice, this patch below shows how we updated the tau-bench example from the previous blog.

Publish your agent on AgentBeats
Now that your agent is publicly accessible, you can let others connect to it and run assessments. To make your agent discoverable — and to leverage the AgentBeats platform for organizing assessments — you just need to publish it by filling out a simple form on the AgentBeats site.

The only required field is your public controller URL, which allows others to locate and interact with your agent directly.

AgentBeats Publish Form

And that’s it — your agent is now live and ready for assessments on the AgentBeats platform. 🚀

Remaining issues
In this post, we outlined the basic process of integrating an A2A agent with the AgentBeats platform. However, the real-world experience of running agents on AgentBeats involves a few additional considerations we haven’t covered yet.

For example, a publicly deployed agent without authentication may be vulnerable to DoS attacks, potentially exhausting the LLM API credits assigned to it. Also, since this guide focuses on remote deployments, users currently need to manage their own cloud infrastructure. In the future, upcoming hosted features on AgentBeats may simplify this workflow even further.



Specific commands and things:
# setup basic deps
sudo apt-get upgrade
sudo apt-get install build-essential
sudo apt-get install git

# setup py/uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# setup workspace
git clone https://github.com/agentbeats/agentify-example-tau-bench.git
cd agentify-example-tau-bench/
git checkout 78b1201
uv sync
source .venv/bin/activate

# run agent
HTTPS_ENABLED=true CLOUDRUN_HOST=tutorial.agentbeats.org ROLE=green agentbeats run_ctrl
# you should see "Uvicorn running on http://0.0.0.0:8010 (Press CTRL+C to quit)"


Note on env vars:
HTTPS_ENABLED: to provide agent url starting with “https”
CLOUDRUN_HOST: to specify agent url with the cloudflared forwarded domain name
ROLE: this is specific to tau-bench repo that we use this to put two agent impl in one repo. You can also just have two repos and run “agentbeats run_ctrl” command inside separately (please do not run it twice under the same working directory)




