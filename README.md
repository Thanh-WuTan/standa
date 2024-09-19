# MITRE Caldera Plugin: Standa

**Standa** is a custom plugin for [MITRE Caldera](https://github.com/mitre/caldera) that enables the automatic creation of stand-alone agents from selected adversary profiles. This removes the need for continuous communication (tunnel) between the host and the Caldera C2 server. Instead, all the necessary payloads, instructions, and configurations are packaged and brought directly to the host.

## Key Features

- **Auto-create Stand-Alone Agents**: Generates stand-alone agents from selected adversary profiles.
- **No Tunnel Required**: Eliminates the need for a communication tunnel between the host and the Caldera C2 server.
- **Payload Management**: Collects and packages all required payloads and instructions for execution on the host.

## How It Works

1. Select adversary profiles within the Caldera UI.
2. The plugin collects all relevant abilities, payloads, and instructions associated with the selected adversary profile.
3. A stand-alone agent is generated, bringing all the necessary files directly to the host machine.

## Installation

1. Clone this repository into the `plugins` directory of your Caldera installation:
   ```bash
   git clone https://github.com/yourusername/standa-caldera-plugin.git plugins/standa

2. Enable the plugin by adding - standa to the list of enabled plugins in either conf/local.yml or conf/default.yml (if running Caldera in insecure mode)

3. Start the Caldera server and navigate to the Standa plugin in the Caldera UI and follow the prompts to generate stand-alone agents.
