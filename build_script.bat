
copy pkg/docker/Dockerfile Dockerfile

:: dos2unix is not a builtin but can be downloaded
:: This is the dos version of `ls -R *.exts | xargs dos2unix`
FOR /F %%k in ('dir /s /b *.xml *.patch *.py *.sh *.txt') DO dos2unix %%k

docker build -t smartva-build .
docker run --rm -v %cd%:/home/smartva/smartva smartva-build

del Dockerfile

:: reset line-endings (hopefully you weren't build from a dirty state)
git checkout *
