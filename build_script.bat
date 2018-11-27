FOR %%O IN (win linux) DO (
  docker build ^
      -t smartva-build-%%O ^
      -f ./pkg/docker/%%O-build/Dockerfile ^
      ./pkg/docker
  docker run --rm -v `pwd`:/home/smartva/smartva smartva-build-%%O
)
