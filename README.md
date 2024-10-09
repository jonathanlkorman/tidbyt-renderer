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

## Setup Process

### 1. Install Raspberry Pi OS Lite

For optimal performance, use Raspberry Pi OS Lite:

1. Download the Raspberry Pi Imager from the [official website](https://www.raspberrypi.org/software/).
2. Launch the imager, select "Raspberry Pi OS Lite" as the operating system.
3. Choose your SD card as the storage device.
4. Click "Write" to flash the OS to your SD card.

### 2. Set Time Zone

After booting your Raspberry Pi, set your local time zone:

```
sudo raspi-config
```

Navigate to "Localisation Options" > "Timezone" and select your timezone.

### 3. Install Git

Install Git on your Raspberry Pi:

```
sudo apt update
sudo apt install git -y
```

### 4. Clone the Repository

Clone this project repository:

```
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

### 5. Setup Options

Choose one of the following setup methods:

#### Option A: Quick Setup Using Makefile (Recommended)

Use our Makefile for a streamlined setup process:

```
make setup
```

This command installs all necessary dependencies and sets up the virtual environment.

If you need a specific version of the rpi-rgb-led-matrix library:

```
RGB_MATRIX_VERSION=some-tag-or-commit-hash make setup
```

#### Option B: Manual Setup

If you prefer more control over the setup process or need to troubleshoot, follow these steps:

1. Update and upgrade your system:
   ```
   sudo apt update
   sudo apt upgrade -y
   ```

2. Install Python and pip:
   ```
   sudo apt install python3 python3-pip -y
   ```

3. Install system dependencies:
   ```
   sudo apt install libatlas-base-dev -y
   ```

4. Create and activate a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

5. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

6. Clone and install the rpi-rgb-led-matrix library:
   ```
   git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
   cd rpi-rgb-led-matrix
   make build-python PYTHON=$(which python)
   sudo make install-python PYTHON=$(which python)
   cd ..
   ```

   If you need a specific version:
   ```
   git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
   cd rpi-rgb-led-matrix
   git checkout <specific-version-tag-or-commit>
   make build-python PYTHON=$(which python)
   sudo make install-python PYTHON=$(which python)
   cd ..
   ```

7. Set up the project configuration:
   ```
   cp config.example.json config.json
   nano config.json  # Edit the configuration as needed
   ```

### 6. Optimize LED Matrix Performance

Disable the Raspberry Pi's audio to improve LED matrix performance:

```
echo "blacklist snd_bcm2835" | sudo tee /etc/modprobe.d/blacklist-rgb-matrix.conf
sudo update-initramfs -u
sudo reboot
```

### 7. Test Your Setup

Run a test pattern to ensure your LED matrix is working correctly:

```
cd submodules/matrix/bindings/python/samples
sudo python3 runtext.py --led-rows=32 --led-cols=64 --led-gpio-mapping=adafruit-hat --led-brightness=60
```

Adjust the flags as necessary for your specific hardware.

## Configuration

After setting up the project, you need to configure it to communicate with your Tidbyt Server and specify which apps to display:

1. Open the configuration file:
   ```
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

### 8. Running the Project

#### Method 1: Using Makefile (Recommended for development)

To run the main project:

```
make run
```

Other useful Makefile commands:
- Clean up the project: `make clean`
- Update the project: `make update`
- Run tests: `make test`

#### Method 2: Using Supervisor (Recommended for long-term operation)

Supervisor ensures that your project runs continuously and restarts automatically if it crashes or if the Raspberry Pi reboots.

1. Install Supervisor:

```
sudo apt-get install supervisor -y
```

2. Create a configuration file for your project:

```
sudo nano /etc/supervisor/conf.d/led-matrix.conf
```

3. Add the following content (adjust paths and flags as needed):

```
[program:led-matrix]
command=sudo python3 /home/pi/your-repo-name/main.py --led-gpio-mapping=adafruit-hat --led-brightness=60 --led-slowdown-gpio=2
directory=/home/pi/your-repo-name
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/led-matrix.err.log
stdout_logfile=/var/log/led-matrix.out.log
```

4. Reload Supervisor to apply the changes:

```
sudo supervisorctl reload
```

5. Check the status of your project:

```
sudo supervisorctl status led-matrix
```

To start, stop, or restart your project:

```
sudo supervisorctl start led-matrix
sudo supervisorctl stop led-matrix
sudo supervisorctl restart led-matrix
```

#### Method 3: Manual Execution

If you prefer to run the project manually or need to debug:

1. Activate the virtual environment (if not already activated):
   ```
   source venv/bin/activate
   ```

2. Run the main script:
   ```
   sudo python3 main.py --led-gpio-mapping=adafruit-hat --led-brightness=60 --led-slowdown-gpio=2
   ```

   Adjust the flags as necessary for your specific hardware setup.

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

## License

[Your chosen license]