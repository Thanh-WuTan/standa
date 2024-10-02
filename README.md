# MITRE Caldera Plugin: Standa

**Standa** is a custom plugin for [MITRE Caldera](https://github.com/mitre/caldera) that enables the automatic creation of stand-alone agents from selected adversary profiles. This removes the need for continuous communication (tunnel) between the host and the Caldera C2 server. Instead, all the necessary payloads, instructions, and configurations are packaged and brought directly to the host.

## Installation
1. Download Caldera as detailed in the [Installation Guide](https://github.com/mitre/Caldera)

2. Clone this repository into the `plugins` directory of your Caldera installation:
   ```bash
   git clone https://github.com/Thanh-WuTan/StandAlone-Agent.git plugins/standa

3. Enable the plugin by adding `- standa` to the list of enabled plugins in either conf/local.yml or conf/default.yml (if running Caldera in insecure mode)

4. Start the Caldera server again and navigate to the Standa plugin in the Caldera UI and follow the prompts to generate stand-alone agents.

## Usage

1. In the **Standa** plugin's GUI, select the desired **adversary profile**, **source**, and **platform** from the provided prompts.

2. Press the **Download** button. A ZIP file containing the stand-alone agent, necessary payloads, and configurations will be created and downloaded to your local machine.

3. Transfer the ZIP file to the target machine. 

4. On the target machine, unzip the package and install the required dependencies by running the following command:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the adversary emulation by executing the main.py file
   ```bash
   python main.py
   ```