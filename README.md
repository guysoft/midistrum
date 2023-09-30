# Midistrum

An app to use android's native midi system to create an omnichord/auto harp-like strum instrument for android.
It also made me port android native midi to kivy.

Midistrum does not generate sound on its own, it needs a synth to send midi t. For example [fluidsynth](https://play.google.com/store/apps/details?id=net.volcanomobile.fluidsynthmidi&hl=en&gl=US). Or your PC over USB.

[<img src="https://fdroid.gitlab.io/artwork/badge/get-it-on.png"
     alt="Get it on F-Droid"
     height="80">](https://f-droid.org/packages/com.gnethomelinux.midistrum/)

## Tutorial

[![Watch the video](https://img.youtube.com/vi/wS7LqcrN70k/hqdefault.jpg)](https://www.youtube.com/embed/wS7LqcrN70k)

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
