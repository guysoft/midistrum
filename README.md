# Midistrum

An app to use android's native midi system to create an omnichord/auto harp-like strum instrument for android.
It also made me port android native midi to kivy.

## Screenshot
![image](https://github.com/guysoft/midistrum/blob/main/media/screenshot.jpg?raw=true)

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
