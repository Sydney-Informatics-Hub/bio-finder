# 🧬 BioFinder MCP

Find bioinformatics tools available as Singularity containers on Galaxy CVMFS -
and get ready-to-copy `singularity` commands from your terminal.

⚠️ Warning: This project is under active development. The tool returns results based on **availability**. Independent research is advised to identify the best tool for your data and needs.

## What does it do?

BioFinder is a [Model Context Protocol](https://modelcontextprotocol.io/) (MCP)
server + CLI client. It indexes two data sources:

| Data source | Contents |
|---|---|
| `toolfinder_meta.yaml` | 714 tool records with descriptions, operations, and homepage links. [Source (`AustralianBioCommons/finder-service-metadata`) ↗](https://github.com/AustralianBioCommons/finder-service-metadata) |
| `galaxy_singularity_cache.json.gz` | 118,594 Singularity container images on Galaxy CVMFS (snapshot: 2026-01-28) |

Given a tool name or a description of what you want to do, BioFinder returns the
latest container path and a copy-pastable `singularity` command.

## Example output

```bash
biofinder> find fastqc

======================================================================
🧬 FASTQC
======================================================================

📝 Description:
   This tool aims to provide a QC report which can spot problems or biases which originate either in the sequencer or in the starting library material. It can be run in one of two modes. It can either run as a stand alone interactive application for the immediate analysis of small numbers of FastQ files, or it can be run in a non-interactive mode where it would be suitable for integrating into a larger analysis pipeline for the systematic processing of large numbers of files.

🌐 Homepage: http://www.bioinformatics.babraham.ac.uk/projects/fastqc/
⚙️  Operations: Sequence composition calculation, Sequencing quality control, Statistical calculation

──────────────────────────────────────────────────────────────────────
📦 AVAILABLE CONTAINERS (27 versions)
──────────────────────────────────────────────────────────────────────

✨ Most Recent Version: 0.12.1--hdfd78af_0

   Path: /cvmfs/singularity.galaxyproject.org/all/fastqc:0.12.1--hdfd78af_0
   Size: 279.8 MB

──────────────────────────────────────────────────────────────────────
💡 USAGE EXAMPLES
──────────────────────────────────────────────────────────────────────

# Execute a command in the container
singularity exec /cvmfs/singularity.galaxyproject.org/all/fastqc:0.12.1--hdfd78af_0 \
  fastqc --help

# Run interactively
singularity shell /cvmfs/singularity.galaxyproject.org/all/fastqc:0.12.1--hdfd78af_0

──────────────────────────────────────────────────────────────────────
📚 OTHER VERSIONS
──────────────────────────────────────────────────────────────────────

   1. 0.12.1--hdfd78af_0
      /cvmfs/singularity.galaxyproject.org/all/fastqc:0.12.1--hdfd78af_0
   2. 0.11.9--hdfd78af_1
      /cvmfs/singularity.galaxyproject.org/all/fastqc:0.11.9--hdfd78af_1
   3. 0.11.9--0
      /cvmfs/singularity.galaxyproject.org/all/fastqc:0.11.9--0
   ... and 24 more versions

======================================================================
```

## Quick start

### Setup

To get started, clone and move into the repository.

```bash
git clone https://github.com/Sydney-Informatics-Hub/bio-finder.git
cd bio-finder
```

Install Python and the required libraries. Dependencies are listed in `requirements.txt`.

```bash
chmod +x setup.sh
./setup.sh
```

### Example usage 

This mini-tutorial demonstrates an example of starting the tool, displaying the supported commands, and a recommended flow of finding available software that can be used for sequence alignment. 

Once a (sequence alignment) tool is chosen, you can display more information about the available versions on the file system.

```bash
# Enter interactive mode
./biofinder

# Display help message
biofinder> help

# Search for tools related to sequence alignment
biofinder> search sequence alignment

# Find a specific tool with more information
biofinder> find clustalo

# Display all available versions
biofinder> versions clustalo

# Build an Lmod module from CVMFS (requires sudo)
biofinder> build samtools

# List CVMFS versions without building a module
biofinder> cvmfs-list samtools
```

## Building Lmod Modules from CVMFS

BioFinder can automatically create [Lmod](https://lmod.readthedocs.io/) module files for tools available in CVMFS at `/cvmfs/singularity.galaxyproject.org/all`. This feature requires:

- CVMFS mounted and accessible
- Lmod installed on the system
- Write permissions to `/apps/Modules/modulefiles` (run with `sudo`)

### Usage Examples

```bash
# Build module for latest version of samtools
./biofinder build samtools

# Build module for specific version
./biofinder build samtools/1.21

# List available versions without building
./biofinder cvmfs-list samtools
```

### Example Output

When building a module without specifying a version:

```
Available versions:
 - 1.22--hdfd78af_0
 - 1.21--h50ea8bc_0
 - 1.20--h50ea8bc_0

You did not specify a version.
Defaulting to newest version: 1.22--hdfd78af_0

If you want a specific version:
    bio-finder build samtools/1.21

Module successfully created.

To load:
    module load samtools/1.22--hdfd78af_0
```

The generated module file will be saved to `/apps/Modules/modulefiles/<tool>/<version>.lua` and can be loaded using the standard `module load` command.

### Loading Multiple Modules

You can load multiple bioinformatics tools simultaneously. Each module works independently:

```bash
# Load multiple tools at once
module load samtools/1.23--h96c455f_0 bwa/0.7.19--h577a1d6_0 bedtools/2.31.1--hf5e1c6e_0

# Check what's loaded
module list

# All tools are available simultaneously  
samtools
bwa
bedtools --version

# Unload specific tools
module unload samtools

# Clear all modules
module purge
```

This allows you to set up complete analysis environments with all the tools you need for a workflow.

### Requirements

For the CVMFS module builder functionality:

- **CVMFS**: Must be mounted at `/cvmfs/singularity.galaxyproject.org/all`
- **Lmod**: Must be installed and available (`module` command)
- **Permissions**: Write access to `/apps/Modules/modulefiles` (run with `sudo` for module creation)
- **Singularity**: Must be available on the system (loaded automatically by module)

### Usage Summary

```bash
# Traditional bio-finder commands (query container metadata)
./biofinder find samtools
./biofinder search "sequence alignment" 
./biofinder versions samtools

# New CVMFS module builder commands
./biofinder cvmfs-list samtools                # List versions in CVMFS
./biofinder build samtools                     # Build module with latest version
./biofinder build samtools/1.22--h96c455f_0   # Build specific version

# For automated scripts/VM builds (preserves Python environment)
sudo -E env "PATH=$PATH" ./biofinder build samtools
sudo -E env "PATH=$PATH" ./biofinder build samtools/1.22--h96c455f_0

# Interactive mode (includes all commands except build)
./biofinder

# After building modules, load and use them
module load samtools/1.22--h96c455f_0        # Load single module  
module load samtools bwa bedtools            # Load multiple modules
module list                                  # Check loaded modules
samtools                                     # Use the tools
```

### Automated/Script Usage

For VM build scripts and automation, you have two options:

**Option 1: Direct commands**
```bash
# Individual commands (preserves Python environment)
sudo -E env "PATH=$PATH" ./biofinder build samtools
sudo -E env "PATH=$PATH" ./biofinder build fastqc  
sudo -E env "PATH=$PATH" ./biofinder build bowtie2
```

**Option 2: Automation script (recommended)**
```bash
# Build multiple tools with one command
./build-modules.sh samtools fastqc bowtie2

# Build specific versions
./build-modules.sh samtools/1.22--h96c455f_0 fastqc/0.12.1--hdfd78af_0

# Use in VM build scripts
#!/bin/bash
cd /path/to/bio-finder
./build-modules.sh samtools fastqc bowtie2 bwa minimap2

# Then load them all for a complete analysis environment
module load samtools fastqc bowtie2 bwa minimap2
```

The automation script (`build-modules.sh`) handles sudo permissions and environment preservation automatically.

⚠️ Warning: The tool returns results based on **availability**. Independent research is advised to identify the best tool for your data and needs.

## Next steps

For an overview of all available options, examples, and tips for using BioFinder effectively, see the guide on [how to query](docs/HOW_TO_QUERY.md).

If you prefer the command-line version (e.g. for scripting and reproducibility), see the [command reference](docs/COMMAND_REFERENCE.md).

BioFinder is in active development with plans to improve functionality, the accuracy of search results, and implementation. See [Future Improvements](docs/DEVELOPER_REFERENCE.md#future-improvements).

## Links

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Galaxy Project CVMFS](https://galaxyproject.org/admin/reference-data-repo/)
- [finder-service-metadata](https://github.com/AustralianBioCommons/finder-service-metadata)
- [CERN VM-FS](https://cernvm.cern.ch/fs/)
