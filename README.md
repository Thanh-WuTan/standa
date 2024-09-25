# MITRE Caldera Plugin: Standa

**Standa** is a custom plugin for [MITRE Caldera](https://github.com/mitre/caldera) that enables the automatic creation of stand-alone agents from selected adversary profiles. This removes the need for continuous communication (tunnel) between the host and the Caldera C2 server. Instead, all the necessary payloads, instructions, and configurations are packaged and brought directly to the host.

## Installation

1. Clone this repository into the `plugins` directory of your Caldera installation:
   ```bash
   git clone https://github.com/Thanh-WuTan/StandAlone-Agent.git plugins/standa

2. Enable the plugin by adding - standa to the list of enabled plugins in either conf/local.yml or conf/default.yml (if running Caldera in insecure mode)

3. Start the Caldera server and navigate to the Standa plugin in the Caldera UI and follow the prompts to generate stand-alone agents.
