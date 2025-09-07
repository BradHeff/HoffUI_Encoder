<!-- HoffUI_Encoder - Advanced Video Encoding Application -->
<a name="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/BradHeff/HoffUI_Encoder">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">HoffUI FFMPEG Encoder</h3>

  <p align="center">
    A powerful, AI-enhanced video encoding application with intelligent system optimization
    <br />
    <a href="https://github.com/BradHeff/HoffUI_Encoder"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/BradHeff/HoffUI_Encoder/issues">Report Bug</a>
    ·
    <a href="https://github.com/BradHeff/HoffUI_Encoder/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#key-features">Key Features</a></li>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#features">Features</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

[![HoffUI Encoder Screenshot][product-screenshot]](https://github.com/BradHeff/HoffUI_Encoder)

**HoffUI FFMPEG Encoder** is a sophisticated, user-friendly video encoding application that combines the power of FFmpeg with intelligent AI analysis and automatic system optimization. Designed for both beginners and professionals, it provides an intuitive GUI interface while leveraging advanced algorithms to deliver optimal encoding results.

### Key Features

🎯 **AI-Powered Analysis** - Uses OpenAI models to analyze video content and recommend optimal encoding settings
🔧 **Smart System Detection** - Automatically detects and optimizes for your hardware capabilities
🎨 **Modern GUI** - Beautiful, responsive interface with tabbed settings and real-time monitoring
⚡ **Hardware Acceleration** - Supports CUDA, VAAPI, QSV, and other hardware acceleration methods
📊 **Real-Time Progress** - Live encoding progress with detailed system information
🎬 **Batch Processing** - Encode multiple files or entire folders with drag-and-drop support
🔄 **Thread Management** - Intelligent multi-threading with automatic optimization
📁 **Format Support** - Handles 14+ video formats including MP4, AVI, MKV, MOV, and more

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Python][Python3]][python-url]
* [![tkinter][ttkbootstrap]][ttkbootstrap-url]
* [![FFmpeg][FFmpeg]][ffmpeg-url]
* [![OpenAI][OpenAI]][openai-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

To get HoffUI Encoder up and running on your system, follow these steps:

### Prerequisites

**Required Software:**
* **Python 3.8+** - The application runtime
* **FFmpeg** - Video encoding engine
  * Ubuntu/Debian: `sudo apt install ffmpeg`
  * Windows: Download from [FFmpeg Official Site](https://ffmpeg.org/download.html)
  * macOS: `brew install ffmpeg`

**Optional:**
* **OpenAI API Key** - For AI-powered encoding optimization
* **CUDA-compatible GPU** - For hardware acceleration (NVIDIA)

### Installation

#### Method 1: Clone and Run (Recommended)
```bash
# Clone the repository
git clone https://github.com/BradHeff/HoffUI_Encoder.git
cd HoffUI_Encoder

# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 usr/lib/hoffui_encoder/main.py
```

#### Method 2: Debian Package (Ubuntu/Debian)
```bash
# Build and install package
cd usr/lib/hoffui_encoder
chmod +x build-apt
./build-apt

# Install the generated .deb package
sudo dpkg -i ../../hoffui_encoder_*.deb
sudo apt-get install -f  # Fix dependencies if needed

# Run from anywhere
hoffui_encoder
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

HoffUI Encoder provides multiple ways to encode your videos:

### Quick Start
1. **Launch the application**
2. **Select input**: Click "Select File" or "Select Folder" (or drag & drop)
3. **Choose output directory**: Click "Browse" to set destination
4. **Configure settings**: Adjust codec, quality, and resolution in the tabs
5. **Start encoding**: Click "Start Encoding"

### Interface Overview

**Main Tabs:**
- **🎥 Video Settings**: Codec, quality (CRF), preset, resolution
- **🔊 Audio Settings**: Codec, bitrate, sample rate
- **⚙️ Advanced**: Custom FFmpeg parameters, filters
- **🖥️ System**: Real-time hardware monitoring and optimization
- **🤖 AI Analysis**: Enable intelligent content analysis (requires API key)

### AI-Enhanced Encoding
1. **Set OpenAI API Key** in settings
2. **Enable AI Analysis** checkbox
3. **Select videos** - AI analyzes content complexity, motion, and details
4. **Automatic optimization** - AI recommends optimal CRF and preset values
5. **Start encoding** with AI-optimized settings

### Batch Processing
- **Folder Selection**: Recursively finds all supported video files
- **Maintains Structure**: Preserves folder hierarchy in output
- **Progress Tracking**: Individual file progress with overall completion
- **Error Handling**: Automatic fallback for problematic files

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- FEATURES -->
## Features

### 🎬 Video Processing
- **14+ Supported Formats**: MP4, AVI, MKV, MOV, WMV, FLV, WebM, M4V, 3GP, MPG, MPEG, TS, VOB, OGV
- **Multiple Codecs**: H.264, H.265, VP9, VP8, AV1 support
- **Quality Control**: CRF-based quality settings (0-51 range)
- **Resolution Scaling**: Original, 4K, 1080p, 720p, 480p, 360p presets
- **Custom Presets**: Ultrafast to Veryslow encoding presets

### 🔊 Audio Processing  
- **Audio Codecs**: AAC, MP3, Opus, Vorbis, AC3
- **Bitrate Control**: Configurable audio bitrate (64k-320k)
- **Sample Rate**: Automatic detection and custom settings
- **Audio Passthrough**: Preserve original audio when desired

### 🚀 Performance Optimization
- **Hardware Acceleration**: 
  - CUDA (NVIDIA GPUs)
  - VAAPI (Intel/AMD on Linux) 
  - QSV (Intel Quick Sync)
  - OpenCL, Vulkan, DRM support
- **Intelligent Threading**: Auto-detects optimal thread count (4-32 threads)
- **System Detection**: Real-time CPU, RAM, GPU monitoring
- **Dynamic Optimization**: Adjusts settings based on system load

### 🤖 AI Intelligence
- **Content Analysis**: Analyzes video complexity, motion, grain, details
- **Smart Recommendations**: AI suggests optimal CRF and preset values
- **Quality Prediction**: Estimates output quality vs file size
- **Scene Detection**: Identifies scene changes for optimal encoding
- **Batch Intelligence**: AI analyzes each file individually for best results

### 🎨 User Experience
- **Modern Interface**: Clean, responsive ttkbootstrap-based GUI  
- **Drag & Drop**: Intuitive file and folder selection
- **Real-Time Progress**: Live encoding progress with ETA
- **System Monitoring**: Live CPU, RAM, temperature displays during encoding
- **Toast Notifications**: Non-intrusive status updates
- **Error Handling**: Graceful failure recovery with detailed logging

### 🛠️ Advanced Features
- **Custom FFmpeg Args**: Direct FFmpeg parameter control
- **Fallback System**: Automatic retry with conservative settings
- **Directory Structure**: Maintains folder hierarchy in output
- **Concurrent Processing**: Parallel file analysis and encoding
- **Debug Mode**: Detailed logging for troubleshooting
- **Profile Management**: Save/load encoding configurations
- **Resource usage analytics**: Opens window to monitor resource usage during encoding

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

### 🚀 Version 2.0 - Enhanced AI & Performance
- [ ] **Advanced AI Models**
  - [ ] Local AI inference (no API key required)
  - [ ] Custom ML models for specific content types
  - [ ] Real-time quality prediction
  - [ ] Automatic scene-based encoding
  
- [ ] **Performance Improvements** 
  - [ ] Multi-GPU encoding support
  - [ ] Distributed encoding across network nodes
  - [ ] Advanced memory management
  - [ ] GPU memory optimization

### 🎯 Version 1.5 - User Experience 
- [ ] **Enhanced Interface**
  - [ ] Dark/Light theme toggle
  - [ ] Customizable workspace layouts
  - [ ] Advanced progress visualization
  - [ ] Real-time preview window
  
- [ ] **Workflow Improvements**
  - [ ] Encoding queue management
  - [ ] Scheduled encoding tasks
  - [ ] Encoding templates/profiles
  - [ ] Batch configuration wizard

### 🔧 Version 1.3 - Extended Functionality
- [ ] **Format & Codec Expansion**
  - [ ] AV1 hardware acceleration
  - [ ] HDR10/Dolby Vision support  
  - [ ] Advanced subtitle handling
  - [ ] Multi-track audio processing
  
- [ ] **Integration Features**
  - [ ] Cloud storage integration (AWS S3, Google Drive)
  - [ ] Docker containerization
  - [ ] REST API for automation
  - [ ] Command-line interface (CLI)

### 🛠️ Version 1.2 - Quality of Life
- [ ] **Configuration Management**
  - [ ] Import/Export settings
  - [ ] Preset sharing community
  - [ ] Auto-update system
  - [ ] Backup/restore configurations
  
- [ ] **Monitoring & Analytics**
  - [ ] Encoding history tracking
  - [ ] Performance benchmarking
  - [ ] Quality metrics dashboard
  - [x] ✅ Resource usage analytics

### 🐛 Current Focus (v1.0.x)
- [x] ✅ FFmpeg parameter optimization
- [x] ✅ Hardware acceleration fixes  
- [x] ✅ System detection improvements
- [x] ✅ AI analysis error handling
- [ ] 🔄 Memory leak prevention
- [ ] 🔄 Cross-platform compatibility testing
- [ ] 🔄 Comprehensive error logging
- [ ] 🔄 Performance profiling tools

### 📝 Community Requests
Vote on features at our [GitHub Discussions](https://github.com/BradHeff/HoffUI_Encoder/discussions)
- [ ] Web-based remote interface
- [ ] Mobile companion app
- [ ] Video comparison tools
- [ ] Automatic quality assessment
- [ ] Integration with media servers (Plex, Jellyfin)

See the [open issues](https://github.com/BradHeff/HoffUI_Encoder/issues) for a full list of proposed features and known issues.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

### Ways to Contribute
- 🐛 **Report Bugs** - Help us identify and fix issues
- 💡 **Feature Requests** - Suggest new functionality
- 📝 **Documentation** - Improve guides and examples  
- 🔧 **Code Contributions** - Add features or fix bugs
- 🧪 **Testing** - Help test on different systems
- 🌐 **Translations** - Make the app accessible worldwide

### Development Setup
```bash
# Fork and clone your fork
git clone https://github.com/YOUR_USERNAME/HoffUI_Encoder.git
cd HoffUI_Encoder

# Create development environment
python3 -m venv .venv
source .venv/bin/activate

# Install development dependencies  
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Create feature branch
git checkout -b feature/AmazingFeature

# Make changes and test
python3 usr/lib/hoffui_encoder/main.py

# Commit and push
git commit -m 'Add some AmazingFeature'
git push origin feature/AmazingFeature
```

### Pull Request Process
1. **Fork** the Project
2. **Create** your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. **Test** your changes thoroughly
4. **Update** documentation if needed
5. **Commit** your Changes (`git commit -m 'Add some AmazingFeature'`)
6. **Push** to the Branch (`git push origin feature/AmazingFeature`)  
7. **Open** a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the GNU General Public License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

**Brad Heffernan** - Lead Developer
- 🐦 X: [@n3xtg3ngam3r13](https://x.com/n3xtg3ngam3r13)
- 🎮 Twitch: [nextgengamer13](https://www.twitch.tv/nextgengamer13)
- 🥊 Kick: [nextgengamer13](https://kick.com/nextgengamer13)
- 📺 YouTube: [@nextgengamer13](https://www.youtube.com/@NextGenGamer13)
- 📧 Email: brad.heffernan83@outlook.com
- 💼 LinkedIn: [brad-heffernan83](https://www.linkedin.com/in/brad-heffernan83/)

**Project Links:**
- 🔗 GitHub: [https://github.com/BradHeff/HoffUI_Encoder](https://github.com/BradHeff/HoffUI_Encoder)
- 📋 Issues: [Report a Bug](https://github.com/BradHeff/HoffUI_Encoder/issues)
- 💬 Discussions: [Feature Requests](https://github.com/BradHeff/HoffUI_Encoder/discussions)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Special thanks to the amazing open source community and these fantastic projects:

* **[FFmpeg](https://ffmpeg.org/)** - The multimedia framework that powers our encoding
* **[OpenAI](https://openai.com/)** - AI models for intelligent video analysis
* **[ttkbootstrap](https://ttkbootstrap.readthedocs.io/)** - Modern, beautiful GUI toolkit
* **[Python](https://python.org/)** - The language that makes it all possible
* **[Best-README-Template](https://github.com/othneildrew/Best-README-Template)** - This README template

### Supporting Libraries
* **psutil** - System and process monitoring
* **Pillow** - Image processing for GUI elements
* **pathlib** - Modern path handling

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/BradHeff/HoffUI_Encoder.svg?style=for-the-badge
[contributors-url]: https://github.com/BradHeff/HoffUI_Encoder/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/BradHeff/HoffUI_Encoder.svg?style=for-the-badge
[forks-url]: https://github.com/BradHeff/HoffUI_Encoder/network/members
[stars-shield]: https://img.shields.io/github/stars/BradHeff/HoffUI_Encoder.svg?style=for-the-badge
[stars-url]: https://github.com/BradHeff/HoffUI_Encoder/stargazers
[issues-shield]: https://img.shields.io/github/issues/BradHeff/HoffUI_Encoder.svg?style=for-the-badge
[issues-url]: https://github.com/BradHeff/HoffUI_Encoder/issues
[license-shield]: https://img.shields.io/github/license/BradHeff/HoffUI_Encoder?style=for-the-badge
[license-url]: https://github.com/BradHeff/HoffUI_Encoder/blob/main/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/brad-heffernan83/

[product-screenshot]: images/screenshot1.png

[ttkbootstrap]: https://img.shields.io/badge/ttkbootstrap-35495E?style=for-the-badge&logo=python&logoColor=61DAFB
[Python3]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[FFmpeg]: https://img.shields.io/badge/FFmpeg-007808?style=for-the-badge&logo=ffmpeg&logoColor=white
[OpenAI]: https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white

[python-url]: https://www.python.org/
[ttkbootstrap-url]: https://ttkbootstrap.readthedocs.io/
[ffmpeg-url]: https://ffmpeg.org/
[openai-url]: https://openai.com/
