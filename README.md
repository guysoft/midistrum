# Midistrum

An app to use android's native midi system to create an omnichord/auto harp-like strum instrument.
It also made me port native midi to kivy.

work in progres

## Build insrtuctions

```
mkdir kivy
cd kivy
git clone https://github.com/kivy/python-for-android.git
git clone https://github.com/guysoft/midistrum.git
cd midistrum/src
sudo docker compose up -d
./docker_build
```

Debug with:
```
./docker_debug
```
