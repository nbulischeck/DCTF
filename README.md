# DCTF

DCTF is a Docker-based CTF platform that is used to deploy (currently) binary and web(flask) challenges in a docker container.

## Dependencies

* python>=3.5
* pip
	* docker
	* docker-compose
	* ruamel.yaml

> **Note:**
> To satisfy all pip dependencies run `sudo pip install -r requirements.txt`.

## Quick Setup

Quickly building and bringing the CTF up is as simple as running a single command.

`python ctf.py -bus`

This builds the docker images, brings the CTF up using the newly generated `docker-compose.yml` file, and prints the status of the challenges. More information on this below.

Connecting to `localhost:8010` with netcat, we can see that our binary is being served within the docker container on the specified port.

![foo-bin](images/foo-bin.png)

Navigating to `localhost:8011` with our browser, we can see that our flask app is running perfectly.

![bar-web](images/bar-web.png)

## Usage

```
usage: ctf.py [-h] [-b] [-u | -d] [-s] [-r] [-p] [--update]

optional arguments:
  -h, --help    show this help message and exit
  -b, --build   build the docker images
  -u, --up      start the CTF
  -d, --down    stop the CTF
  -s, --status  displays the status of the challenges
  -r, --remove  remove all ctf containers and images
  -p, --prune   prune unused docker networks
  --update      update the docker compose config
```

### Build

The `build` flag parses the INI files that are paired with every challenge and runs the `./scripts/gen.sh` script with the proper arguments according to the type of the challenge.

After the `gen.sh` script finishes, `build` calls the `build` script in the `skel` directory which builds the appropriate docker image.

More info on `gen.sh` below.

TBD: Make `build` pair with `up` to add new challenges on-the-fly.

### Up

The `up` flag calls the `update` function to get an up to date list of all of the challenges and then calls `docker-compose up -d` to start the challenges in the background.

### Down

The `down` flag calls `docker-compose down`.

### Status

The `status` flag calls `docker-compose ps`.

### Remove

The `remove` flag parses the INI files that are paired with every challenge and runs the `./scripts/delete.sh` script with the name of each challenge in order to delete all challenge-related containers and images.

Once all containers and images are removed, `remove` calls `./scripts/remove.sh` which removes all directories matching `*-build` in the main directory. After removing all build directories, it calls `docker network prune -f` to forcibly remove unused docker networks.

### Prune

The `prune` flag calls `docker network prune`.

### Update

The `update` flag has no short option. It is used as a manual way of updating the `docker-compose.yml` file. It parses all INI files in the challenge directories and builds the `docker-compose.yml` file based on the name of the challenge and the ports it runs on.

## config.ini

The `config.ini` file is a very important file. It is necessary to include one in every challenge folder. Without this, the platform doesn't know what to call your challenge or what port it runs on. The use of the `config.ini` file was to give the naming conventions of challenges as much leeway as possible.

Below is the sample `config.ini` file for `foo-bin`:

```
1. [Foo Binary Challenge]
2. Name = foo
3. Description = Binary challenge example.
4. Category = pwnable
5. Flag = FLAG{PLACEHOLDER_FLAG}
6. Points = 10
7. Port = 8010
8. Type = binary
```

### Section Title - Line 1

The section title can be anything. This is to help identify the challenge to the author. There is no limit as to what goes inside the section header as long as it remains within the two brackets.

### Name - Line 2

The name of the challenge must be within `[A-Za-z0-9._-]`. This is a requirement per the Docker specification. Docker image names may not stray from this.

**If there is a binary being served, it must be the same name.**

### Description - Line 3

The description can be anything. It is not parsed or used in any way, but it is there to help the challenge author describe the challenge or put additional information.

### Category - Line 4

The category can be anything. It is not parsed or used in any way, but it is recommended to use a typical CTF category i.e. Pwnable, Crypto, WebEx, etc.

### Flag - Line 5

The flag is not required, but it is used to help easily identify the flag of the challenge.

### Points - Line 6

The points are not required, but it is used as a reference.

### Port - Line 7

The port number is required. 

### Type - Line 8

The type of challenge is required. Currently this may either be `binary` or `web`. There are no other options. If it is not set as `binary` or `web`, the challenge will not be built!

### Barebones `config.ini`

The most barebones `config.ini` would be as follows:

```
[Foo Binary Challenge]
Name = foo
Port = 8010
Type = binary
```

## ./scripts/gen.sh

The `gen.sh` script is used to build the directories and dockerfiles that can be used in building Docker containers for CTF challenges. It is **NOT** meant to be called manually. All necessary `gen.sh` handling is done in the `ctf.py` file.

```
Usage: ./gen.sh -n foo -p 9999 [OPTION]
Generate CTF challenge docker containers.
  -n NAME	Name of your challenge
  -p PORT	Port the challenge is served on
  -d DIR	Path to a directory containing your challenge
  -w		Build a docker container with flask
  -f		Specify that a flag file exists
  -m		Specify that a makefile exists
  -v		Verbose output (set -x)
  -h		Help screen
```

### Common Examples

#### Basic

This generates a directory with a prefilled Dockerfile, docker-compose.yml, and xinetd configuration file. In order for everything to run smoothly you must place a binary with the name `foo` in `foo/bin`.

`./gen.sh -n foo -p 8010`

**Note**: A name [-n] and a port [-p] are **required**. Docker needs a name for the image and xinetd needs a port to run on. This may be updated later to serve defaults.

#### Challenge Directory

This generates a basic directory (the same thing as above) but moves everything in `foo-bin/` to `foo/bin`.

`./gen.sh -n foo -p 8010 -d foo-bin/`

#### Flask Webapps

Flask webapps can be generated with the `-h` option. These require there to be a `requirements.txt` file and an `app.py` file in the Challenge Directory.

`./gen.sh -n bar -p 8011 -d bar-web/ -w`

#### Makefiles

Makefiles can be placed in the `foo/bin` directory if necessary. The skeleton dockerfile is written to install gcc and reinstall make on the base Ubuntu system. Specifying the `-m` option tells docker to reinstall make on the Ubuntu base and run make in the directory where the files in `foo/bin` are placed.

`./gen.sh -n foo -p 8010 -m`

#### Flags

Flags may be used and dropped into the `foo/bin` directory. Flags must have the path of `foo/bin/flag` (no extension). Specifying the `-f` option tells docker to set the proper permissions on the flag file (`RUN chmod 740 /home/ctf/flag`).

`./gen.sh -n foo -p 8000 -f`

#### Combined

By using all of the options in `./gen.sh`, you can quickly deploy a CTF challenge using docker.

`./gen.sh -n foo -p 8000 -d foo-bin/ -m -f`

This creates a docker directory called `foo`. Tells xinetd and docker-compose to run on port `8000`. Copies the contents of `foo-bin/` to `foo/bin` and deploys them to the container. Calls make to create the binary in `foo/bin`. Sets the proper permissions on the flag in `foo/bin`.