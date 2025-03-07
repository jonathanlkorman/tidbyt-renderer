# LED Matrix Project

This project uses an LED matrix connected to a Raspberry Pi to display information rendered by the Tidbyt Server.

## Overview

This project is part of a two-component system:

1. **LED Matrix Project (This repository)**: Runs on a Raspberry Pi connected to an LED matrix. It fetches and displays images rendered by the Tidbyt Server.
2. **Tidbyt Server**: A separate server that renders Tidbyt apps and provides WebP images for display.

## How it Works

1. The Raspberry Pi runs this project to control the LED matrix.
2. It periodically sends requests to the Tidbyt Server to fetch newly rendered WebP images.
3. The received images are then displayed on the LED matrix.

## Prerequisites

Before you begin, ensure you have the following:

- Raspberry Pi (3B+, 3A+, 4B, or Zero W recommended)
- LED Matrix (with compatible HAT/Bonnet)
- MicroSD card (8GB or larger)
- Power supply for your Raspberry Pi
- Ethernet cable or Wi-Fi capability for internet connection

## **Choosing the Right OS**
The latest versions of Debian-based Linux distributions enforce **PEP 668**, which requires the use of **Python virtual environments** for package installations. However, **virtual environments cannot be run with `sudo`**, which caused significant issues because our script requires `sudo` access for hardware interactions.

To bypass this issue, we installed **Raspberry Pi OS (Legacy, 64-bit) Lite**, which is based on **Debian Bullseye** and does not enforce the PEP 668 restriction.

### **Installing Raspberry Pi OS (Legacy, 64-bit) Lite**
- Download **Raspberry Pi OS (Legacy, 64-bit) Lite** from the official Raspberry Pi website.
- Flash the image onto an SD card using **Raspberry Pi Imager** or a tool like `balenaEtcher`.
- Boot the Raspberry Pi with the newly flashed SD card.

---

## Step 1 - Install Raspberry Pi OS Lite
For optimal performance, this project requires **Raspberry Pi OS Lite**. This version does not have a GUI, allowing the Pi to dedicate resources to rendering on the Tidbyt display.

Follow the official Raspberry Pi documentation to install Raspberry Pi OS Lite on your Raspberry Pi. Once installed, return to this guide.

## Step 2 - Set Time Zone
Before installing any software, ensure your Raspberry Pi is set to the correct time zone. If you skipped this during installation, set it by running:

```bash
sudo raspi-config
```

## Step 3 - Install Git
Git is required to download the software. Install it with:

```bash
sudo apt install git
```

## Step 4 - Installing Tidbyt Renderer Software
Clone the repository and use the Makefile for installation:

```bash
git clone --recursive https://github.com/jonathanlkorman/tidbyt-renderer
cd tidbyt-renderer/
make install
```

The installation process may take time as it installs all dependencies.

## Configuration

After setting up the project, you need to configure it to communicate with your Tidbyt Server and specify which apps to display:

1. Create and open the configuration file:
   ```bash
   cp config.json.sample config.json
   nano config.json 
   ```

2. Add or modify the following settings:
   ```json
   {
     "server_url": "http://your-tidbyt-server-ip:8000/render_app",
     "update_interval": 10,
     "app_names": ["app1", "app2"],
     "app_configs": {
       "app1": {
         "key1": "value1",
         "key2": "value2"
       },
       "app2": {
         "key3": "value3",
         "key4": "value4"
       }
     }
   }
   ```

   - Replace `your-tidbyt-server-ip` with the IP address or hostname of your Tidbyt Server.
   - The `update_interval` is in seconds and determines how often the apps rotate.
   - `app_names` is an array of app names you want to display. These should match the names of the .star files on your Tidbyt Server.
   - `app_configs` contains app-specific configurations. Each app can have its own set of key-value pairs for configuration.

3. Example configuration for specific apps:

   ```json
   {
     "server_url": "http://192.168.1.100:8000/render_app",
     "update_interval": 10,
     "app_names": ["nfl_scores", "sunrise_sunset"],
     "app_configs": {
        "nfl_scores": {
            "rotation_rate": 2,
            "preferred_teams": "NYJ",
            "rotation_only_preferred": true,
            "rotation_only_live": true,
            "rotation_highlight_preferred_team_when_live": false
         },
         "sunrise_sunset": {
            "location": "{\"lat\":40.7181,\"lng\":-73.8448,\"locality\":\"Forest Hills, NY\",\"timezone\":\"America/New_York\"}"
         }
      }
   }
   ```

   This configuration will display the NFL scores app and the sunrise/sunset app, rotating between them every 10 seconds.

4. Save and close the file.

5. If you add new apps or modify existing ones, make sure to update both the `app_names` array and the `app_configs` object in the configuration file.

Remember that the configuration for each app should match the expected input for that app on your Tidbyt Server. Refer to your app's documentation or code for the correct configuration parameters.


## Step 5 - Testing and Optimization
If you're new to working with an LED matrix on a Raspberry Pi, follow these steps:

### **Modify `cmdline.txt` to Add CPU Isolation**
Open the boot command file:
```bash
sudo nano /boot/cmdline.txt
```
At the **end** of the existing line (do not add a new line), add:
```bash
isolcpus=3
```

### Disable Audio (Required for LED Matrix Stability)
   ```bash
   cat <<EOF | sudo tee /etc/modprobe.d/blacklist-rgb-matrix.conf
   blacklist snd_bcm2835
   EOF

   sudo update-initramfs -u
   sudo reboot
   ```

### Running a Test Display
Navigate to the matrix submodule and run a test script:

```bash
cd tidbyt-renderer/submodules/matrix/bindings/python/samples
sudo python3 runtext.py --led-rows=32 --led-cols=64 --led-gpio-mapping=adafruit-hat --led-brightness=60
```

For setups with an anti-flickering hardware mod, use:

```bash
--led-gpio-mapping=adafruit-hat-pwm
```

### Additional Optimization Flags
- `--led-brightness=60` (Adjusts brightness, range: 1-100)
- `--led-gpio-mapping=adafruit-hat-pwm` (Ensures correct GPIO mapping)
- `--led-slowdown-gpio=2` (Optimizes GPIO timing)

## Step 6 - Running the Renderer
Once everything is set up, start the renderer using the Makefile:

```bash
make run
```

Or run it directly:

```bash
sudo python3 src/main.py --led-rows=32 --led-cols=64 --led-gpio-mapping=adafruit-hat-pwm --led-brightness=20 --led-slowdown-gpio=2 --led-pwm-lsb-nanoseconds=250
```

### Running in the Background
By default, the renderer stops when the SSH session ends. Use one of these methods to keep it running:

#### **Method 1: Using Supervisor**
Supervisor automatically restarts the process in case of failure.

1. Install Supervisor:
   ```bash
   sudo apt-get install supervisor
   ```
2. Edit Supervisor configuration:
   ```bash
   sudo nano /etc/supervisor/supervisord.conf
   ```
   Add the following at the bottom:
   ```
   [inet_http_server]
   port=*:9001
   ```
3. Create a Supervisor config file:
   ```bash
   sudo nano /etc/supervisor/conf.d/renderer.conf
   ```
   Add this content:
   ```
   [program:renderer]
   command=sudo python3 src/main.py --led-gpio-mapping=adafruit-hat-pwm --led-brightness=60 --led-slowdown-gpio=2
   directory=/home/pi/tidbyt-renderer
   autostart=true
   autorestart=true
   ```
4. Restart your Raspberry Pi:
   ```bash
   sudo reboot
   ```
   Access the Supervisor web dashboard at `http://<your_pi_ip>:9001`.

#### **Method 2: Using Screen (Manual)**
1. Install `screen`:
   ```bash
   sudo apt install screen
   ```
2. Start a new screen session:
   ```bash
   screen
   ```
3. Run the renderer command.
4. Detach from the session using `Ctrl + A`, then `D`.
5. To reconnect:
   ```bash
   screen -r
   ```

### Running in Terminal Mode
To run in the terminal for debugging:

```bash
sudo python3 src/main.py --terminal-mode=true
```

## Troubleshooting

If you encounter issues:

- Flickering: Consider performing the hardware anti-flickering mod described in the rpi-rgb-led-matrix documentation.
- Permission issues: Ensure you're running scripts with `sudo`.
- LED matrix not lighting up: Check all connections.
- For detailed logs, run in terminal mode:
  ```
  sudo python3 main.py --terminal-mode=true
  ```
- If using Supervisor, check the log files at `/var/log/led-matrix.err.log` and `/var/log/led-matrix.out.log` for any error messages.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.